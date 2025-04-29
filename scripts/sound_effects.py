# scripts/sound_effects.py

#!/usr/bin/env python3
import os
import json
import argparse
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip

def load_config(path):
    return json.load(open(path, encoding='utf8'))

def add_sounds_to_video(cfg, convo, intermediate, final):
    video = VideoFileClip(intermediate)
    clips = []
    current = 0.0
    sd = cfg['paths']['sound_dir']
    for ev in convo:
        dur = float(ev['duration'])
        key = ev.get('sound')
        if key:
            fn = os.path.join(sd, f"{key}.mp3")
            if os.path.isfile(fn):
                clips.append(AudioFileClip(fn).set_start(current))
            else:
                print(f"[Warn] missing sound: {fn}")
        current += dur
    if clips:
        video = video.set_audio(CompositeAudioClip(clips))
    video.write_videofile(
        final,
        codec='libx264',
        audio_codec='aac',
        temp_audiofile='temp-audio.m4a',
        remove_temp=True
    )
    video.close()

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--config',       default='config.json')
    p.add_argument('--conversation', default='conversation.json')
    p.add_argument('--input-video',  default=None)
    p.add_argument('--output-video', default=None)
    args = p.parse_args()

    cfg   = load_config(args.config)
    convo = json.load(open(args.conversation, encoding='utf8'))
    inter= args.input_video  or cfg['paths']['intermediate_video']
    final= args.output_video or cfg['paths']['final_video']

    if not os.path.isfile(inter):
        print(f"Error: missing {inter}")
        exit(1)
    add_sounds_to_video(cfg, convo, inter, final)

if __name__=='__main__':
    main()
