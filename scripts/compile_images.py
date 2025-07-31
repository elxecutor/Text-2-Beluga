# scripts/compile_images.py

import os, json, subprocess

def load_config(path):
    cfg = json.load(open(path, encoding='utf8'))
    cfg['paths']['chat_output'] = os.path.normpath(cfg['paths']['chat_output'])
    return cfg

def build_concat_file(cfg, convo):
    chat = cfg['paths']['chat_output']
    lines = []
    last_img = None
    for i, ev in enumerate(convo,1):
        img = os.path.join("..", chat, f"{i:03d}.png")
        lines.append(f"file '{img}'\noutpoint {ev['duration']}")
        last_img = img
    # Add final frame with minimal duration
    if last_img:
        lines.append(f"file '{last_img}'\noutpoint 0.04")
    cf = os.path.join(chat, 'concat.txt')
    with open(cf, 'w', encoding='utf8') as f:
        f.write("\n".join(lines))
    return cf

def compile_video(cfg, convo):
    concat = build_concat_file(cfg, convo)
    os.makedirs('output', exist_ok=True)
    out = cfg['paths']['ffmpeg_output']
    w = cfg['layout']['world_width']
    
    # Check if fade transitions are enabled in config
    use_fades = cfg.get('video_settings', {}).get('fade_transitions', False)
    fade_duration = cfg.get('video_settings', {}).get('fade_duration', 0.3)
    
    if use_fades:
        # Create video with fade transitions using complex filter
        cmd = [
            'ffmpeg', '-f', 'concat', '-safe', '0', '-i', concat,
            '-vcodec', 'libx264', '-r', '25', '-crf', '25',
            '-vf', f"scale={w}:-2,pad={w}:{w}:(ow-iw)/2:(oh-ih)/2,fade=t=in:st=0:d={fade_duration},fade=t=out:st=0:d={fade_duration}",
            '-pix_fmt', 'yuv420p', out
        ]
    else:
        # Original compilation without fades
        cmd = [
            'ffmpeg', '-f', 'concat', '-safe', '0', '-i', concat,
            '-vcodec', 'libx264', '-r', '25', '-crf', '25',
            '-vf', f"scale={w}:-2,pad={w}:{w}:(ow-iw)/2:(oh-ih)/2",
            '-pix_fmt', 'yuv420p', out
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
