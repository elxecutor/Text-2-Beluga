# scripts/compile_images.py

import os, json, subprocess

def load_config(path):
    cfg = json.load(open(path, encoding='utf8'))
    cfg['paths']['chat_output'] = os.path.normpath(cfg['paths']['chat_output'])
    return cfg

def build_concat_file(cfg, convo):
    chat = cfg['paths']['chat_output']
    lines = []
    for i, ev in enumerate(convo,1):
        img = os.path.join("..", chat, f"{i:03d}.png")
        lines.append(f"file '{img}'\noutpoint {ev['duration']}")
    lines.append(f"file '{img}'\noutpoint 0.04")
    cf = os.path.join(chat, 'concat.txt')
    open(cf,'w').write("\n".join(lines))
    return cf

def compile_video(cfg, convo):
    concat = build_concat_file(cfg, convo)
    os.makedirs('output', exist_ok=True)
    out    = cfg['paths']['ffmpeg_output']
    w      = cfg['layout']['world_width']
    cmd = [
      'ffmpeg','-f','concat','-safe','0','-i',concat,
      '-vcodec','libx264','-r','25','-crf','25',
      '-vf',f"scale={w}:-2,pad={w}:{w}:(ow-iw)/2:(oh-ih)/2",
      '-pix_fmt','yuv420p', out
    ]
    subprocess.run(cmd, check=True)
    os.remove(concat)

if __name__=='__main__':
    import argparse, json
    p = argparse.ArgumentParser()
    p.add_argument('config')
    p.add_argument('conversation')
    args = p.parse_args()
    cfg   = load_config(args.config)
    convo = json.load(open(args.conversation, encoding='utf8'))
    compile_video(cfg, convo)
