# scripts/sound_effects.py

#!/usr/bin/env python3
import os, json, argparse
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip

def load_config(p): return json.load(open(p, encoding='utf8'))

def add_sounds(cfg, convo, silent, final):
    video = VideoFileClip(silent)
    clips = []
    t = 0.0
    sd = cfg['paths']['sound_dir']
    for ev in convo:
        dur = float(ev['duration'])
        fn = os.path.join(sd, f"{ev.get('sound')}.mp3")
        if ev.get('sound') and os.path.isfile(fn):
            clips.append(AudioFileClip(fn).set_start(t))
        t += dur
    if clips:
        video = video.set_audio(CompositeAudioClip(clips))
    video.write_videofile(final, codec='libx264', audio_codec='aac',
                          temp_audiofile='temp-audio.m4a', remove_temp=True)
    video.close()

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--config',       default='utils/config.json')
    p.add_argument('--conversation', default='utils/conversation.json')
    p.add_argument('--input-video',  default=None)
    p.add_argument('--output-video', default=None)
    args = p.parse_args()

    cfg   = load_config(args.config)
    convo = json.load(open(args.conversation, encoding='utf8'))
    silent = args.input_video  or cfg['paths']['intermediate_video']
    final  = args.output_video or cfg['paths']['final_video']

    if not os.path.isfile(silent):
        print(f"Error: missing {silent}")
        return
    add_sounds(cfg, convo, silent, final)

if __name__=='__main__':
    main()
