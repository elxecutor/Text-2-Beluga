# scripts/compile_images.py

import os, json, subprocess

def load_config(path):
    cfg = json.load(open(path, encoding='utf8'))
    # collapse any redundant segments in chat_output
    cfg['paths']['chat_output'] = os.path.normpath(cfg['paths']['chat_output'])
    return cfg

def build_concat_file(cfg, convo):
    chat_dir = os.path.normpath(cfg['paths']['chat_output'])
    lines = []
    for idx, ev in enumerate(convo, 1):
        img = os.path.join("..", chat_dir, f"{idx:03d}.png")
        lines.append(f"file '{img}'\noutpoint {ev['duration']}")
    # last hold
    lines.append(f"file '{img}'\noutpoint 0.04")

    concat = os.path.join(chat_dir, 'concat.txt')
    with open(concat, 'w') as f:
        f.write("\n".join(lines))
    return concat

def compile_video(cfg, convo):
    concat = build_concat_file(cfg, convo)
    out    = cfg['paths']['ffmpeg_output']
    width  = cfg['layout']['world_width']
    cmd = [
        'ffmpeg','-f','concat','-safe','0','-i',concat,
        '-vcodec','libx264','-r','25','-crf','25',
        '-vf',f"scale={width}:-2,pad={width}:{width}:(ow-iw)/2:(oh-ih)/2",
        '-pix_fmt','yuv420p', out
    ]
    subprocess.run(cmd, check=True)
    os.remove(concat)

if __name__=='__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('config')
    p.add_argument('conversation')
    args = p.parse_args()
    cfg   = load_config(args.config)
    convo = json.load(open(args.conversation, encoding='utf8'))
    compile_video(cfg, convo)
