# scripts/generate_chat.py

import os, json, datetime, random
from PIL import Image, ImageFont, ImageDraw
from pilmoji import Pilmoji

def load_config(path):
    return json.load(open(path, encoding='utf8'))

def load_characters(path):
    return json.load(open(path, encoding='utf8'))

def init_fonts(cfg):
    fd = cfg['paths']['fonts_dir']
    fonts = {}
    for key in ('name','time','message','joined'):
        fconf = cfg['layout'][key]
        fonts[key] = ImageFont.truetype(
            os.path.join(fd, fconf['font']), fconf['size']
        )
    return fonts

def render_join(actor, ev, cfg, fonts, current_time):
    txt = random.choice(cfg['joined_texts']).replace("CHARACTER", actor)
    jconf = cfg['layout']['joined']
    img = Image.new(
        'RGBA',
        (cfg['layout']['world_width'], jconf['height']),
        tuple(cfg['layout']['world_color'])
    )
    draw = ImageDraw.Draw(img)
    arrow = Image.open(cfg['paths']['green_arrow']).convert('RGBA')
    arrow.thumbnail((40,40), Image.LANCZOS)
    arrow_x = ev.get('arrow_x', 36)
    text_y = (jconf['height'] - jconf['size']) // 2
    img.paste(arrow, (arrow_x, text_y), arrow)
    text_x = arrow_x + arrow.width + 20
    draw.text(
        (text_x, text_y),
        txt,
        tuple(jconf['color']),
        font=fonts['joined']
    )
    return img

def render_message(ev, cfg, fonts, current_time, profpics, chars):
    mconf = cfg['layout']['message']
    nconf = cfg['layout']['name']
    tconf = cfg['layout']['time']
    # start new template
    height = mconf['position'][1] + mconf['line_height'] * len(ev['text'].split('\n'))
    img = Image.new('RGBA',(cfg['layout']['world_width'], height),tuple(cfg['layout']['world_color']))
    draw = ImageDraw.Draw(img)
    # profile pic
    pic = Image.open(profpics[ev['actor']]).convert('RGBA')
    pic.thumbnail((mconf['position'][1], mconf['position'][1]), Image.LANCZOS)
    mask = Image.new('L', pic.size, 0)
    ImageDraw.Draw(mask).ellipse((0,0,*pic.size), fill=255)
    img.paste(pic, tuple(cfg['layout']['profpic']['position']), mask)
    # name & time
    nm_x, nm_y = tuple(nconf['position'])
    draw.text((nm_x,nm_y), ev['actor'], tuple(nconf['color']), font=fonts['name'])
    time_str = current_time.strftime('%-I:%M %p')
    time_x = nm_x + fonts['name'].getbbox(ev['actor'])[2] + tconf['spacing']
    draw.text((time_x,nm_y), time_str, tuple(tconf['color']), font=fonts['time'])
    # message text
    with Pilmoji(img) as pil:
        y = mconf['position'][1]
        for line in ev['text'].split('\n'):
            pil.text((mconf['position'][0], y), line, tuple(mconf['color']), font=fonts['message'])
            y += mconf['line_height']
    return img

def save_images(cfg, convo, chars):
    out = cfg['paths']['chat_output']
    os.makedirs(out, exist_ok=True)
    fonts = init_fonts(cfg)
    profpics = {
        actor: os.path.join(cfg['paths']['profile_pics'], data['profile_pic'])
        for actor,data in chars.items()
    }
    t = datetime.datetime.now()
    for idx, ev in enumerate(convo,1):
        if ev['type']=='join':
            img = render_join(ev['actor'], ev, cfg, fonts, t)
        else:
            img = render_message(ev, cfg, fonts, t, profpics, chars)
        img.save(os.path.join(out, f"{idx:03d}.png"))
        t += datetime.timedelta(seconds=ev['duration'])

if __name__=='__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('config')
    p.add_argument('conversation')
    p.add_argument('characters')
    args = p.parse_args()
    cfg  = load_config(args.config)
    convo= json.load(open(args.conversation, encoding='utf8'))
    chars= load_characters(args.characters)
    save_images(cfg, convo, chars)
