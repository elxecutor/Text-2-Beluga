# scripts/sound_effects.py

#!/usr/bin/env python3
import os, json, argparse
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, concatenate_audioclips, afx

def load_config(path):
    with open(path, encoding='utf8') as f:
        return json.load(f)

def find_theme_change_indices(convo):
    # Change themes based on key moments or pacing.
    # Naively, every 5-7 messages or every "explosion", "scream", "panic", etc.
    theme_events = []
    current_theme = 0
    for i, event in enumerate(convo):
        if event.get("sound") in {"explosion", "scream", "panic", "modeugene", "oh-my-god-bro-oh-hell-nah-man"}:
            theme_events.append((i, current_theme))
            current_theme += 1
    return theme_events

def add_sounds_and_themes(cfg, convo, silent_video_path, final_video_path):
    video = VideoFileClip(silent_video_path)
    event_clips = []
    theme_clips = []

    sound_dir = cfg['paths']['sound_dir']
    theme_dir = cfg['paths']['theme_dir']  # Assuming theme tracks also reside here
    themes = cfg.get('theme_codes', [])
    total_duration = 0.0

    # Add sound effect clips and individual background music
    for event in convo:
        dur = float(event['duration'])
        
        # Add sound effects
        sound_name = event.get('sound')
        if sound_name:
            sound_path = os.path.join(sound_dir, f"{sound_name}.mp3")
            if os.path.isfile(sound_path):
                event_clips.append(AudioFileClip(sound_path).set_start(total_duration))
        
        # Add individual background music for messages
        if event.get('type') == 'message' and 'background_music' in event:
            bg_music_name = event['background_music']
            bg_music_path = os.path.join(sound_dir, f"{bg_music_name}.mp3")
            if os.path.isfile(bg_music_path):
                bg_clip = AudioFileClip(bg_music_path)
                # Loop or trim to match message duration
                if bg_clip.duration < dur:
                    bg_clip = afx.audio_loop(bg_clip, duration=dur)
                else:
                    bg_clip = bg_clip.subclip(0, dur)
                # Lower volume for background music
                bg_clip = bg_clip.volumex(0.3)
                theme_clips.append(bg_clip.set_start(total_duration))
        
        total_duration += dur

    # Add background themes
    theme_points = find_theme_change_indices(convo)
    if not theme_points:
        theme_points = [(0, 0)]  # fallback

    # Calculate theme segments
    theme_points.append((len(convo), len(themes)-1))  # mark end
    timeline = 0.0
    for (start_idx, theme_idx), (end_idx, _) in zip(theme_points, theme_points[1:]):
        if theme_idx >= len(themes):
            break
        segment_duration = sum(float(convo[i]['duration']) for i in range(start_idx, end_idx))
        theme_file = os.path.join(theme_dir, f"{themes[theme_idx]}.mp3")
        if os.path.isfile(theme_file):
            theme_clip = AudioFileClip(theme_file)
            theme_clip = afx.audio_loop(theme_clip, duration=segment_duration).volumex(0.15)
            theme_clips.append(theme_clip.set_start(timeline))
        timeline += segment_duration

    # Mix all clips together
    all_audio = event_clips + theme_clips
    if all_audio:
        video = video.set_audio(CompositeAudioClip(all_audio))

    video.write_videofile(final_video_path, codec='libx264', audio_codec='aac',
                          temp_audiofile='temp-audio.m4a', remove_temp=True)
    video.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config',       default='utils/config.json')
    parser.add_argument('--conversation', default='utils/conversation.json')
    parser.add_argument('--input-video',  default=None)
    parser.add_argument('--output-video', default=None)
    args = parser.parse_args()

    cfg = load_config(args.config)
    with open(args.conversation, encoding='utf8') as f:
        convo = json.load(f)

    input_video = args.input_video or cfg['paths']['intermediate_video']
    output_video = args.output_video or cfg['paths']['final_video']

    if not os.path.isfile(input_video):
        print(f"Error: missing {input_video}")
        return

    add_sounds_and_themes(cfg, convo, input_video, output_video)

if __name__ == '__main__':
    main()
