# scripts/generate_chat.py

import os
import json
import datetime
import random
import re

from PIL import Image, ImageFont, ImageDraw
from pilmoji import Pilmoji

# ——— Markdown parsing ——————————————————————————————————————————————

MD_RE = re.compile(
    r"("
    r"\`\`\`.*?\`\`\`|"                               # `monospace`
    r"https?://\S+|"                                  # URL
    r"\*\*\*.+?\*\*\*|"                               # ***bolditalic***
    r"\*\*.+?\*\*|"                                   # **bold**
    r"\*.+?\*|"                                       # *italic*
    r"~.+?~|"                                         # ~strike~
    r"@\w+|"                                          # @mention
    r"#\w+|"                                          # #channel
    r"[\U0001F300-\U0001FAFF\U00002600-\U000027BF]|"  # emoji range
    r"[^\*\~@#`\s]+|\s+)"                             # text or whitespace
)

def parse_md(text):
    toks = MD_RE.findall(text)
    parsed = []
    for t in toks:
        if t.startswith('```') and t.endswith('```'):
            parsed.append(('monospace', t[3:-3]))
        elif t.startswith('***') and t.endswith('***'):
            parsed.append(('bolditalic', t[3:-3]))
        elif t.startswith('**') and t.endswith('**'):
            parsed.append(('bold', t[2:-2]))
        elif t.startswith('*') and t.endswith('*'):
            parsed.append(('italic', t[1:-1]))
        elif t.startswith('~') and t.endswith('~'):
            parsed.append(('strike', t[1:-1]))
        elif t.startswith('@'):
            parsed.append(('mention', t))
        elif t.startswith('#'):
            parsed.append(('channel mention', t))
        elif t.startswith("http://") or t.startswith("https://"):
            parsed.append(('link', t))
        elif re.match(r"[\U0001F300-\U0001FAFF\U00002600-\U000027BF]", t):
            parsed.append(('emoji', t))
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
def wrap_text(text, font, max_width):
    if text.startswith('```') and text.endswith('```'):
        return text.splitlines()
        
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        # measure width of the combined string
        if font.getbbox(test)[2] <= max_width:
            current = test
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

def render_block(actor, lines, cfg, fonts, profpics, colors, now):
    """
    Renders a cumulative block of messages for `actor`, with each message
    wrapped to fit the world_width and canvas height adjusted.
    """
    L = cfg['layout']
    world_w = L['world_width']
    x0 = L['message']['x']
    max_text_w = world_w - x0 - 20

    # 1) wrap every logical line into sub-lines
    wrapped = []  # will hold (sublined_text, edited_flag)
    for msg in lines:
        # if this entire message is a triple-backtick code block, measure with monospace
        if msg['text'].startswith('```') and msg['text'].endswith('```'):
            sublines = wrap_text(msg['text'], fonts['monospace'], max_text_w)
        else:
            sublines = wrap_text(msg['text'], fonts['message'],  max_text_w)

        for i, sl in enumerate(sublines):
            wrapped.append((sl, msg['edited'] if (i == len(sublines)-1) else False))


    # 2) compute needed height
    line_h = L['message']['line_height']
    height = L['message']['y'] + line_h * len(wrapped) + 20
    pic_y, pic_size = L['profpic']['position'][1], L['profpic']['size']
    min_h = pic_y + pic_size + 10
    if height < min_h:
        height = min_h

    canvas = Image.new('RGBA', (world_w, height), tuple(L['world_color']))
    draw = ImageDraw.Draw(canvas)

    # paste profile picture
    pic = Image.open(profpics[actor]).convert('RGBA')
    pic.thumbnail((pic_size, pic_size), Image.LANCZOS)
    mask = Image.new('L', pic.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, *pic.size), fill=255)
    canvas.paste(pic, tuple(L['profpic']['position']), mask)

    # draw name + timestamp
    nx, ny = L['name']['pos']
    draw.text((nx, ny), actor, fill=colors[actor], font=fonts['name'])
    ts = now.strftime('%-I:%M %p')
    tx = nx + fonts['name'].getbbox(actor)[2] + L['time']['spacing']
    draw.text((tx, ny+10), f"Today at {ts}", fill=tuple(L['time']['color']), font=fonts['time'])

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
                elif kind == 'emoji':
                    pil.text((x, y+5), txt + " ", tuple(L['message']['color']), font=fonts['message'])
                    w = fonts['message'].getbbox(txt + " ")[2]
                elif kind == 'monospace':
                    pil.text((x, y), txt, tuple(L['message']['color']), font=fonts['monospace'])
                    w = fonts['monospace'].getbbox(txt)[2]
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
                img.thumbnail((max_w, L['max_height']), Image.LANCZOS)
                canvas.paste(img, (x, y), img)
                y += img.height + pad
            except Exception as e:
                # fallback to filename card on error
                draw.text((x, y), f"[Error loading {att['filename']}]", font=fonts['message'], fill=(255,0,0))
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
    profpics = {n: os.path.join(cfg['paths']['profile_pics'], c['profile_pic'])
                for n,c in chars.items()}
    colors   = {n: rgb(c['role_color']) for n,c in chars.items()}

    now = datetime.datetime.now()
    current_actor = None
    current_lines = []
    idx = 1

    for ev in convo:
        if ev['type'] == 'message':
            global EDITED_FLAG
            EDITED_FLAG = ev.get('edited', False)

            msg = {'text': ev['text'], 'edited': ev.get('edited', False)}
            if ev['actor'] == current_actor:
                if msg['edited']:
                    current_lines[-1] = msg
                else:
                    current_lines.append(msg)
            else:
                current_actor = ev['actor']
                current_lines = [msg]

            img = render_block(current_actor, current_lines, cfg, fonts, profpics, colors, now)
            img.save(os.path.join(out, f"{idx:03d}.png"))
            now += datetime.timedelta(minutes=ev['duration'])
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
