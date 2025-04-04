import os
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip

# Typing indicator constants (same as in generate_chat.py)
TYPING_FRAME_DURATION = 0.3  # Duration per frame in seconds
TYPING_ANIMATION_FRAMES = 3  # Number of animation frames

base_dir = os.path.dirname(os.path.abspath(__file__))

def add_sounds(filename):
    video = VideoFileClip("output.mp4")
    duration = 0
    audio_clips = []

    with open(filename, encoding="utf8") as f:
        name_up_next = True
        for line in f.read().splitlines():
            if line == '':
                name_up_next = True
                continue
            elif line.startswith('#'):
                continue
            elif line.startswith("WELCOME"):
                if "#!" in line:
                    parts = line.split('$^')
                    duration_part, sound_part = parts[1].split("#!")
                    audio_file = f'{base_dir}/{os.pardir}/assets/sounds/mp3/{sound_part.strip()}.mp3'
                    audio_clip = AudioFileClip(audio_file).set_start(duration)
                    audio_clips.append(audio_clip)
                    duration += float(duration_part)
                else:
                    duration += float(line.split('$^')[1])
            elif name_up_next:
                name_up_next = False
                # Add typing sound if available
                typing_sound = f'{base_dir}/{os.pardir}/assets/sounds/mp3/typing.mp3'
                if os.path.exists(typing_sound):
                    audio_clips.append(
                        AudioFileClip(typing_sound).set_start(duration)
                    )
                duration += TYPING_FRAME_DURATION * TYPING_ANIMATION_FRAMES
                continue
            else:
                if "#!" in line:
                    parts = line.split('$^')
                    duration_part, sound_part = parts[1].split("#!")
                    audio_file = f'{base_dir}/{os.pardir}/assets/sounds/mp3/{sound_part.strip()}.mp3'
                    audio_clip = AudioFileClip(audio_file).set_start(duration)
                    audio_clips.append(audio_clip)
                    duration += float(duration_part)
                else:
                    duration += float(line.split('$^')[1])
                    
    if len(audio_clips) > 0:
        composite_audio = CompositeAudioClip(audio_clips)
        video = video.set_audio(composite_audio)

    video.write_videofile(f'{base_dir}/{os.pardir}/final_video.mp4', codec="libx264", audio_codec="aac")
    os.remove("output.mp4")