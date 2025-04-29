# scripts/generate_chat.py

import os
import json
import datetime
import random
import re

from PIL import Image, ImageFont, ImageDraw
from pilmoji import Pilmoji

# ——— Markdown parsing ——————————————————————————————————————————————

MD_RE = re.compile(r"(\*\*\*.+?\*\*\*|\*\*.+?\*\*|\*.+?\*|~.+?~|@\w+|[^*\~@]+)")

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
        elif t.startswith('~') and t.endswith('~'):
            parsed.append(('strike', t[1:-1]))
        elif t.startswith('@'):
            parsed.append(('mention', t))
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

def render_block(actor, lines, cfg, fonts, profpics, colors, now):
    """
    Renders a cumulative block of messages for `actor` with all `lines` so far.
    """
    L = cfg['layout']
    height = L['message']['y'] + L['message']['line_height'] * len(lines)
    canvas = Image.new('RGBA', (L['world_width'], height), tuple(L['world_color']))
    draw = ImageDraw.Draw(canvas)

    # profile picture
    pic = Image.open(profpics[actor]).convert('RGBA')
    pic.thumbnail((L['profpic']['size'], L['profpic']['size']), Image.LANCZOS)
    mask = Image.new('L', pic.size, 0)
    ImageDraw.Draw(mask).ellipse((0,0,*pic.size), fill=255)
    canvas.paste(pic, tuple(L['profpic']['position']), mask)

    # name + timestamp
    nx, ny = L['name']['pos']
    draw.text((nx, ny), actor, fill=colors[actor], font=fonts['name'])
    ts = now.strftime('%-I:%M %p')
    tx = nx + fonts['name'].getbbox(actor)[2] + L['time']['spacing']
    draw.text((tx, ny), f"Today at {ts}", fill=tuple(L['time']['color']), font=fonts['time'])

    # message content
    y = L['message']['y']
    with Pilmoji(canvas) as pil:
        for line in lines:
            x = L['message']['x']
            for kind, txt in parse_md(line):
                if kind == 'text':
                    pil.text((x,y), txt, tuple(L['message']['color']), font=fonts['message'])
                    w = fonts['message'].getbbox(txt)[2]
                elif kind == 'bold':
                    pil.text((x,y), txt, tuple(L['message']['color']), font=fonts['message_bold'])
                    w = fonts['message_bold'].getbbox(txt)[2]
                elif kind == 'italic':
                    pil.text((x,y), txt, tuple(L['message']['color']), font=fonts['message_italic'])
                    w = fonts['message_italic'].getbbox(txt)[2]
                elif kind == 'bolditalic':
                    pil.text((x,y), txt, tuple(L['message']['color']), font=fonts['message_bold_italic'])
                    w = fonts['message_bold_italic'].getbbox(txt)[2]
                elif kind == 'strike':
                    pil.text((x,y), txt, tuple(L['message']['color']), font=fonts['message_strike'])
                    asc,_ = fonts['message_strike'].getmetrics()
                    mid = y + asc//2
                    draw.line((x, mid, x + fonts['message_strike'].getbbox(txt)[2], mid),
                              fill=tuple(L['message']['color']))
                    w = fonts['message_strike'].getbbox(txt)[2]
                else:  # mention
                    pad = L['message']['mention_pad']
                    w_txt = fonts['mention'].getbbox(txt)[2]
                    bg = [x, y-pad//2, x + w_txt + pad, y + fonts['mention'].getbbox(txt)[3] + pad//2]
                    draw.rounded_rectangle(bg, radius=8, fill=tuple(L['name']['mention_bg']))
                    pil.text((x+pad/2,y), txt, tuple(L['name']['mention_text']), font=fonts['mention'])
                    w = w_txt + pad
                x += w
            y += L['message']['line_height']

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
    pending_dur   = 0.0
    idx = 1

    for ev in convo:
        if ev['type'] == 'message':
            # same actor?
            if ev['actor'] == current_actor:
                current_lines.append(ev['text'])
            else:
                # if switching actor, reset
                current_actor = ev['actor']
                current_lines = [ev['text']]

            pending_dur = ev['duration']
            img = render_block(current_actor, current_lines, cfg, fonts, profpics, colors, now)
            img.save(os.path.join(out, f"{idx:03d}.png"))
            now += datetime.timedelta(seconds=pending_dur)
            idx += 1

        else:  # join event
            # reset current block because join breaks conversation flow
            current_actor = None
            current_lines = []
            pending_dur = ev['duration']

            img = render_join(ev, cfg, fonts, colors, now)
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
