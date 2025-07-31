# scripts/generate_chat.py

import os
import json
import datetime
import random
import re

from PIL import Image, ImageFont, ImageDraw
from pilmoji import Pilmoji

# Global flag for edited messages
EDITED_FLAG = False

# ——— Markdown parsing ——————————————————————————————————————————————

MD_RE = re.compile(
    r"("
    r"https?://\S+|"                                  # URL
    r"\*\*\*.+?\*\*\*|"                               # ***bolditalic***
    r"\*\*.+?\*\*|"                                   # **bold**
    r"\*.+?\*|"                                       # *italic*
    r"~~.+?~~|"                                       # ~~strike~~
    r"@\w+|"                                          # @mention
    r"#\w+|"                                          # #channel
    r"[\U0001F300-\U0001FAFF\U00002600-\U000027BF]+|"  # emoji sequence
    r"[^\*\~@#\s]+|"                                  # text
    r"\s+)"                                           # whitespace
)

def parse_md(text):
    toks = MD_RE.findall(text)
    parsed = []
    for t in toks:
        if t.startswith('***') and t.endswith('***'):
            parsed.append(('bolditalic', t[3:-3]))
        elif t.startswith('**') and t.endswith('**'):
            parsed.append(('bold', t[2:-2]))
        elif t.startswith('*') and t.endswith('*'):
            parsed.append(('italic', t[1:-1]))
        elif t.startswith('~~') and t.endswith('~~'):
            parsed.append(('strike', t[2:-2]))
        elif t.startswith('@'):
            parsed.append(('mention', t))
        elif t.startswith('#'):
            parsed.append(('channel mention', t))
        elif t.startswith("http://") or t.startswith("https://"):
            parsed.append(('link', t))
        elif re.match(r"[\U0001F300-\U0001FAFF\U00002600-\U000027BF]", t):
            # Handle emoji with automatic spacing
            parsed.append(('emoji_spaced', t))
        else:
            parsed.append(('text', t))
    return parsed

# ——— Utilities ——————————————————————————————————————————————————

def load_json(path):
    with open(path, encoding='utf8') as f:
        return json.load(f)

def rgb(hexcol):
    h = hexcol.lstrip('#')
    return tuple(int(h[i:i+2],16) for i in (0,2,4))

def init_fonts(cfg):
    fd = cfg['paths']['fonts_dir']
    fonts = {}
    for key,spec in cfg['layout']['fonts'].items():
        fonts[key] = ImageFont.truetype(
            os.path.join(fd, spec['file']),
            spec['size']
        )
    return fonts

# ——— Rendering functions ——————————————————————————————————————————————
def calculate_rendered_width(text, font):
    """
    Calculate the actual rendered width including emoji spacing.
    """
    total_width = 0
    tokens = parse_md(text)
    
    for kind, content in tokens:
        if kind == 'emoji_spaced':
            # Account for emoji padding: 4px left + 8px right = 12px total
            emoji_width = font.getbbox(content)[2]
            total_width += emoji_width + 12  # 4 + 8 padding
        else:
            # Regular text, use actual font measurement
            total_width += font.getbbox(content)[2]
    
    return total_width

def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    
    for i, word in enumerate(words):
        # Test the line with the new word added
        test_line = f"{current} {word}".strip()
        
        # Calculate actual rendered width including emoji spacing
        rendered_width = calculate_rendered_width(test_line, font)
        
        if rendered_width <= max_width:
            current = test_line
        else:
            # Line would be too wide, wrap it
            if current:
                lines.append(current)
                current = word
            else:
                # Even single word is too wide, but we must include it
                current = word
            
            # Check if even a single word is too wide
            single_word_width = calculate_rendered_width(word, font)
            if single_word_width > max_width:
                # Word itself is too wide due to emoji spacing
                # Check if it's an emoji causing the issue
                tokens = parse_md(word)
                emoji_tokens = [t for t in tokens if t[0] == 'emoji_spaced']
                if emoji_tokens:
                    # Force break before emoji if possible
                    lines.append(current)
                    current = ""
    
    # Handle the last line - critical for emojis at the end
    if current:
        final_width = calculate_rendered_width(current, font)
        if final_width > max_width:
            # Final line is too wide, try to break it
            words_in_current = current.split()
            if len(words_in_current) > 1:
                # Try to find a good break point
                for split_idx in range(len(words_in_current) - 1, 0, -1):
                    line_part = " ".join(words_in_current[:split_idx])
                    remaining_part = " ".join(words_in_current[split_idx:])
                    
                    line_width = calculate_rendered_width(line_part, font)
                    if line_width <= max_width:
                        lines.append(line_part)
                        # Check if remaining part also fits
                        remaining_width = calculate_rendered_width(remaining_part, font)
                        if remaining_width <= max_width:
                            lines.append(remaining_part)
                        else:
                            # Recursively wrap the remaining part
                            remaining_lines = wrap_text(remaining_part, font, max_width)
                            lines.extend(remaining_lines)
                        current = ""
                        break
        
        if current:  # Still have content to add
            lines.append(current)
    
    return lines

def calculate_attachment_height(attachments, cfg):
    """
    Pre-calculate the exact height needed for attachments without rendering them.
    Returns the total height required for all attachments.
    """
    if not attachments:
        return 0
        
    L = cfg['layout']['attachment']
    total_height = 0
    max_w = L['max_width']
    pad = L['padding']
    
    for att in attachments:
        if att['type'] in ['image', 'gif']:
            try:
                # Load the actual image to get its dimensions after thumbnailing
                img = Image.open(att['path']).convert('RGBA')
                if img.format == 'GIF':
                    img.seek(0)  # Go to first frame for GIFs
                
                # Calculate the actual size after thumbnail operation
                original_size = img.size
                max_h = L['max_height']
                
                # Calculate thumbnail size (same logic as PIL.thumbnail)
                aspect_ratio = original_size[0] / original_size[1]
                if original_size[0] > max_w or original_size[1] > max_h:
                    if aspect_ratio > max_w / max_h:
                        # Width is the limiting factor
                        new_h = int(max_w / aspect_ratio)
                    else:
                        # Height is the limiting factor
                        new_h = max_h
                else:
                    new_h = original_size[1]
                
                total_height += new_h + pad
                img.close()
            except Exception:
                # Fallback to estimated height if image can't be loaded
                total_height += L['max_height'] + pad
        else:
            # Text or other file attachments
            if att['type'] == 'text':
                total_height += L['text_box_height'] + pad
            else:
                total_height += L.get('other_box_height', 50) + pad
    
    return total_height

def render_block(actor, lines, cfg, fonts, profpics, colors, badges, now):
    """
    Renders a cumulative block of messages for `actor`, with each message
    wrapped to fit the world_width and canvas height automatically adjusted
    based on content length (text + attachments).
    
    The function dynamically calculates the required height by:
    1. Measuring the actual text content after wrapping
    2. Pre-calculating attachment dimensions
    3. Ensuring minimum height for UI elements (profile pic, name, etc.)
    """
    L = cfg['layout']
    world_w = L['world_width']
    x0 = L['message']['x']
    max_text_w = world_w - x0 - 20

    # 1) wrap every logical line into sub-lines
    wrapped = []  # will hold (sublined_text, edited_flag)
    attachments = []
    for msg in lines:
        # Extract attachments if present
        if 'attachments' in msg:
            attachments.extend(msg['attachments'])
            
        sublines = wrap_text(msg['text'], fonts['message'], max_text_w)

        for i, sl in enumerate(sublines):
            wrapped.append((sl, msg['edited'] if (i == len(sublines)-1) else False))


    # 2) DYNAMIC HEIGHT CALCULATION - Auto-resize based on content
    # This ensures the message block is exactly the right size for its content
    line_h = L['message']['line_height']
    
    # More accurate text height calculation
    if wrapped:
        # Calculate actual text height based on font metrics
        font_height = fonts['message'].getmetrics()[0] + fonts['message'].getmetrics()[1]  # ascent + descent
        text_height = L['message']['y'] + (len(wrapped) * line_h) + 10  # Added small padding
    else:
        # Minimum text area even with no content
        text_height = L['message']['y'] + line_h
    
    # Calculate exact attachment height using helper function
    attachment_height = calculate_attachment_height(attachments, cfg)
    
    # Calculate total height with proper bottom padding
    height = text_height + attachment_height + 30  # Added extra bottom padding
    
    # Ensure minimum height for profile picture and name/timestamp area
    pic_y, pic_size = L['profpic']['position'][1], L['profpic']['size']
    name_height = L['name']['pos'][1] + fonts['name'].getmetrics()[0] + fonts['name'].getmetrics()[1]
    min_h = max(pic_y + pic_size + 20, name_height + 40)  # Increased margins
    
    if height < min_h:
        height = min_h
    
    # Create canvas with the dynamically calculated height

    canvas = Image.new('RGBA', (world_w, height), tuple(L['world_color']))
    draw = ImageDraw.Draw(canvas)

    # paste profile picture
    pic = Image.open(profpics[actor]).convert('RGBA')
    pic.thumbnail((pic_size, pic_size), Image.LANCZOS)
    mask = Image.new('L', pic.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, *pic.size), fill=255)
    canvas.paste(pic, tuple(L['profpic']['position']), mask)

    # draw name + timestamp
        # — draw name —
    nx, ny = L['name']['pos']
    draw.text((nx, ny), actor, fill=colors[actor], font=fonts['name'])

    # — load & draw badge (if defined) —
    badge_filename = badges[actor]
    badge_offset = 0
    if badge_filename:
        badge_img = Image.open(badge_filename).convert('RGBA')
        # resize to configured badge size
        size = L['badge']['size']
        badge_img.thumbnail((size, size), Image.LANCZOS)

        # position badge vertically centered on the name line
        text_h = fonts['name'].getbbox(actor)[3]
        by = ny + (text_h - size + L['badge']['spacing']) // 2
        bx = nx + fonts['name'].getbbox(actor)[2] + L['badge']['spacing']

        canvas.paste(badge_img, (bx, by), badge_img)
        badge_offset = size + L['badge']['spacing']

    # — draw timestamp, shifted right by name width + badge_offset + spacing —
    ts = now.strftime('%-I:%M %p')
    tx = nx + fonts['name'].getbbox(actor)[2] + badge_offset + L['time']['spacing']
    draw.text((tx, ny + 10),
              f"Today at {ts}",
              fill=tuple(L['time']['color']),
              font=fonts['time'])

    # ——— ADD: draw "(edited)" next to timestamp if flagged —————————————
    global EDITED_FLAG
    if EDITED_FLAG:
        edited_txt = " (edited)"
        width_ts = fonts['time'].getbbox(f"Today at {ts}")[2]
        draw.text((tx + width_ts, ny+10), edited_txt, fill=tuple(L['time']['color']), font=fonts['time'])

    # draw wrapped message lines
    y = L['message']['y']
    with Pilmoji(canvas) as pil:
        for raw, was_edited in wrapped:
            x = x0
            for kind, txt in parse_md(raw):
                if kind == 'text':
                    pil.text((x, y), txt, tuple(L['message']['color']), font=fonts['message'])
                    w = fonts['message'].getbbox(txt)[2]
                elif kind == 'bold':
                    pil.text((x, y), txt, tuple(L['message']['color']), font=fonts['message_bold'])
                    w = fonts['message_bold'].getbbox(txt)[2]
                elif kind == 'italic':
                    pil.text((x, y), txt, tuple(L['message']['color']), font=fonts['message_italic'])
                    w = fonts['message_italic'].getbbox(txt)[2]
                elif kind == 'bolditalic':
                    pil.text((x, y), txt, tuple(L['message']['color']), font=fonts['message_bold_italic'])
                    w = fonts['message_bold_italic'].getbbox(txt)[2]
                elif kind == 'strike':
                    pil.text((x, y), txt, tuple(L['message']['color']), font=fonts['message_strike'])
                    asc,_ = fonts['message_strike'].getmetrics()
                    mid = y + asc//1.4
                    draw.line((x, mid, x + fonts['message_strike'].getbbox(txt)[2], mid), fill=tuple(L['message']['color']), width=2)
                    w = fonts['message_strike'].getbbox(txt)[2]
                elif kind == 'link':
                    underline_y = y + fonts['message'].getmetrics()[0] + 2
                    pil.text((x, y), txt, (66, 135, 245), font=fonts['message'])  # blue color
                    draw.line((x, underline_y, x + fonts['message'].getbbox(txt)[2], underline_y), fill=(66, 135, 245), width=1)
                    w = fonts['message'].getbbox(txt)[2]
                elif kind == 'emoji' or kind == 'emoji_spaced':
                    # Render emoji with automatic generous spacing
                    left_padding = 4    # Left padding for better appearance
                    right_padding = 8   # Right padding to prevent congestion
                    
                    pil.text((x + left_padding, y + 2), txt, tuple(L['message']['color']), font=fonts['message'])
                    # Calculate width: emoji width + total padding
                    emoji_width = fonts['message'].getbbox(txt)[2]
                    w = emoji_width + left_padding + right_padding
                else:  # mention
                    pad = L['message']['mention_pad']
                    w_txt = fonts['mention'].getbbox(txt)[2]
                    bg = [x, y-pad//2, x + w_txt + pad, y + fonts['mention'].getbbox(txt)[3] + pad//2]
                    draw.rounded_rectangle(bg, radius=8, fill=tuple(L['name']['mention_bg']))
                    pil.text((x+pad/2, y), txt, tuple(L['name']['mention_text']), font=fonts['mention'])
                    w = w_txt + pad
                x += w
            if was_edited:
                edit_str = " (edited)"
                # x is already at end-of-line after drawing the last token
                pil.text((x + 4, y),
                         edit_str,
                         tuple(L['message']['color']),
                         font=fonts['message_italic'])

            y += line_h

    # Render attachments below the text
    if attachments:
        render_attachments(canvas, attachments, cfg, fonts, y)

    return canvas

def render_typing(ev, cfg, fonts, colors, now):
    """
    Renders a typing indicator message in the style of join/leave messages.
    """
    L = cfg['layout']['joined']  # Use same layout as join messages
    canvas = Image.new('RGBA', (cfg['layout']['world_width'], L['height']), tuple(cfg['layout']['world_color']))
    draw = ImageDraw.Draw(canvas)

    # Create typing dots indicator (like the arrows for join/leave)
    dots_bg = Image.new('RGBA', (40, 40), (0, 0, 0, 0))
    dots_draw = ImageDraw.Draw(dots_bg)
    
    # Draw three animated dots in a circular pattern
    for i, (x_offset, y_offset) in enumerate([(15, 15), (25, 20), (35, 15)]):
        alpha = 255 if i < 2 else 128  # Make third dot dimmer for animation effect
        dots_draw.ellipse((x_offset-3, y_offset-3, x_offset+3, y_offset+3), 
                         fill=(185, 187, 190, alpha))
    
    # Position the dots where the arrow would be
    ax = cfg['layout']['profpic']['position'][0]
    ay = (L['height'] - 40) // 2
    canvas.paste(dots_bg, (ax, ay), dots_bg)

    # Create typing message similar to join/leave templates
    typing_message = f"CHARACTER is typing..."
    before, after = typing_message.split("CHARACTER")
    
    # Draw the typing message
    tx = ax + 40 + 20  # Same offset as join/leave messages
    draw.text((tx, ay + 10), before, fill=tuple(L['color']), font=fonts['message'])
    
    # Draw name in role color
    w_before = fonts['message'].getbbox(before)[2]
    draw.text((tx + w_before, ay + 10), ev['actor'], fill=colors[ev['actor']], font=fonts['name'])
    
    # Draw after text
    w_name = fonts['name'].getbbox(ev['actor'])[2]
    draw.text((tx + w_before + w_name, ay + 10), after, fill=tuple(L['color']), font=fonts['message'])

    return canvas

def render_join(ev, cfg, fonts, colors, now):
    """
    Renders a join message with role-colored name.
    """
    L = cfg['layout']['joined']
    canvas = Image.new('RGBA', (cfg['layout']['world_width'], L['height']), tuple(cfg['layout']['world_color']))
    draw = ImageDraw.Draw(canvas)

    # green arrow
    arrow = Image.open(cfg['paths']['green_arrow']).convert('RGBA')
    arrow.thumbnail((40,40), Image.LANCZOS)
    ax = cfg['layout']['profpic']['position'][0]
    ay = (L['height'] - arrow.height) // 2
    canvas.paste(arrow, (ax, ay), arrow)

    # split template around CHARACTER
    template = random.choice(cfg['joined_texts'])
    before, after = template.split("CHARACTER")
    # draw before text
    tx = ax + arrow.width + 20
    draw.text((tx, ay), before, fill=tuple(L['color']), font=fonts['message'])
    # draw name in role color
    w_before = fonts['message'].getbbox(before)[2]
    draw.text((tx + w_before, ay), ev['actor'], fill=colors[ev['actor']], font=fonts['name'])
    # draw after
    w_name = fonts['name'].getbbox(ev['actor'])[2]
    draw.text((tx + w_before + w_name, ay), after, fill=tuple(L['color']), font=fonts['message'])

    return canvas

def render_leave(ev, cfg, fonts, colors, now):
    """
    Renders a leave message with role-colored name.
    """
    L = cfg['layout']['left']
    canvas = Image.new('RGBA', (cfg['layout']['world_width'], L['height']), tuple(cfg['layout']['world_color']))
    draw = ImageDraw.Draw(canvas)

    # red arrow
    arrow = Image.open(cfg['paths']['red_arrow']).convert('RGBA')
    arrow.thumbnail((40,40), Image.LANCZOS)
    ax = cfg['layout']['profpic']['position'][0]
    ay = (L['height'] - arrow.height) // 2
    canvas.paste(arrow, (ax, ay), arrow)

    # split template around CHARACTER
    template = random.choice(cfg['left_texts'])
    before, after = template.split("CHARACTER")
    # draw before text
    tx = ax + arrow.width + 20
    draw.text((tx, ay), before, fill=tuple(L['color']), font=fonts['message'])
    # draw name in role color
    w_before = fonts['message'].getbbox(before)[2]
    draw.text((tx + w_before, ay), ev['actor'], fill=colors[ev['actor']], font=fonts['name'])
    # draw after
    w_name = fonts['name'].getbbox(ev['actor'])[2]
    draw.text((tx + w_before + w_name, ay), after, fill=tuple(L['color']), font=fonts['message'])

    return canvas

def render_attachments(canvas, attachments, cfg, fonts, start_y):
    """
    Draw attachments below the text block on `canvas`.
    Returns the new Y offset after rendering all attachments.
    """
    draw = ImageDraw.Draw(canvas)
    L = cfg['layout']['attachment']
    x = L['x']
    y = start_y
    max_w = L['max_width']
    pad = L['padding']

    for att in attachments:
        if att['type'] == 'image':
            try:
                img = Image.open(att['path']).convert('RGBA')
                # Handle GIFs by taking the first frame
                if img.format == 'GIF':
                    img.seek(0)  # Go to first frame
                img.thumbnail((max_w, L['max_height']), Image.LANCZOS)
                canvas.paste(img, (x, y), img)
                y += img.height + pad
            except Exception as e:
                # fallback to filename card on error
                draw.text((x, y), f"[Error loading {att['filename']}]", font=fonts['message'], fill=(255,0,0))
                y += fonts['message'].getbbox(att['filename'])[3] + pad

        elif att['type'] == 'gif':
            try:
                # For GIFs, show a placeholder with GIF indicator
                gif_img = Image.open(att['path']).convert('RGBA')
                gif_img.seek(0)  # First frame
                gif_img.thumbnail((max_w, L['max_height']), Image.LANCZOS)
                canvas.paste(gif_img, (x, y), gif_img)
                # Add GIF indicator
                gif_badge = Image.new('RGBA', (40, 20), (88, 101, 242, 200))
                badge_draw = ImageDraw.Draw(gif_badge)
                badge_draw.text((5, 2), "GIF", fill=(255, 255, 255), font=fonts['message'])
                canvas.paste(gif_badge, (x + 5, y + 5), gif_badge)
                y += gif_img.height + pad
            except Exception as e:
                draw.text((x, y), f"[Error loading GIF {att['filename']}]", font=fonts['message'], fill=(255,0,0))
                y += fonts['message'].getbbox(att['filename'])[3] + pad

        elif att['type'] == 'text':
            # draw a file icon or just a box with filename
            box_h = L['text_box_height']
            draw.rectangle((x, y, x+max_w, y+box_h), outline=L['border_color'])
            draw.text((x+pad, y+pad),
                      att['filename'],
                      font=fonts['message_bold'],
                      fill=tuple(L['text_color']))
            y += box_h + pad

        else:  # generic other file
            draw.rectangle((x, y, x+max_w, y+L['other_box_height']), outline=L['border_color'])
            draw.text((x+pad, y+pad),
                      att['filename'],
                      font=fonts['message'],
                      fill=tuple(L['text_color']))
            y += L['other_box_height'] + pad

    return y

# ——— Main with cumulative logic —————————————————————————————————————————

def save_images(cfg, convo, chars):
    out = cfg['paths']['chat_output']
    os.makedirs(out, exist_ok=True)

    fonts    = init_fonts(cfg)
    profpics = {n: os.path.join(cfg['paths']['profile_pics'], c['profile_pic']) for n,c in chars.items()}
    badges = {n: os.path.join(cfg['paths']['badges_dir'], c['badge']) if c['badge'] else None for n, c in chars.items()}
    colors   = {n: rgb(c['role_color']) for n,c in chars.items()}

    now = datetime.datetime.now()
    current_actor = None
    current_lines = []
    idx = 1

    for ev in convo:
        if ev['type'] == 'message':
            global EDITED_FLAG
            EDITED_FLAG = ev.get('edited', False)

            msg = {
                'text': ev['text'], 
                'edited': ev.get('edited', False),
                'attachments': ev.get('attachments', [])
            }
            if ev['actor'] == current_actor:
                if msg['edited']:
                    current_lines[-1] = msg
                else:
                    current_lines.append(msg)
            else:
                current_actor = ev['actor']
                current_lines = [msg]

            img = render_block(current_actor, current_lines, cfg, fonts, profpics, colors, badges, now)
            img.save(os.path.join(out, f"{idx:03d}.png"))
            now += datetime.timedelta(seconds=ev['duration'])
            idx += 1

            EDITED_FLAG = False

        elif ev['type'] == 'join':
            current_actor = None
            current_lines = []
            img = render_join(ev, cfg, fonts, colors, now)
            img.save(os.path.join(out, f"{idx:03d}.png"))
            now += datetime.timedelta(seconds=ev['duration'])
            idx += 1

        elif ev['type'] == 'leave':
            current_actor = None
            current_lines = []
            img = render_leave(ev, cfg, fonts, colors, now)
            img.save(os.path.join(out, f"{idx:03d}.png"))
            now += datetime.timedelta(seconds=ev['duration'])
            idx += 1

        elif ev['type'] == 'typing':
            current_actor = None
            current_lines = []
            img = render_typing(ev, cfg, fonts, colors, now)
            img.save(os.path.join(out, f"{idx:03d}.png"))
            now += datetime.timedelta(seconds=ev['duration'])
            idx += 1


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('config', help='Path to config.json')
    parser.add_argument('conversation', help='Path to conversation.json')
    parser.add_argument('characters', help='Path to characters.json')
    args = parser.parse_args()

    cfg   = load_json(args.config)
    convo = load_json(args.conversation)
    chars = load_json(args.characters)

    save_images(cfg, convo, chars)
