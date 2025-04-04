import os
from sound_effects import add_sounds

base_dir = os.path.dirname(os.path.abspath(__file__))

# Typing indicator constants (same as in generate_chat.py)
TYPING_FRAME_DURATION = 0.3  # Duration per frame in seconds
TYPING_ANIMATION_FRAMES = 3  # Number of animation frames

def gen_vid(filename):
    input_folder = f'{base_dir}/{os.pardir}/chat/'
    image_files = sorted([f for f in os.listdir(input_folder) if f.endswith('.png')])

    # Read durations from the file
    durations = []
    with open(filename, encoding="utf8") as f:
        name_up_next = True
        
        lines = f.read().splitlines()
        for line in lines:
            if line == '':
                name_up_next = True
                continue
            elif line[0] == '#':
                continue
            elif line.startswith("WELCOME"):
                if "#!" in line:
                    durations.append(line.split('$^')[1].split("#!")[0])
                else:
                    durations.append(line.split('$^')[1])
                continue
            elif name_up_next == True:
                name_up_next = False
                # Add durations for typing animation frames
                durations.extend([str(TYPING_FRAME_DURATION)] * TYPING_ANIMATION_FRAMES)
                continue
            else:
                if "#!" in line:
                    durations.append(line.split('$^')[1].split("#!")[0])
                else:
                    durations.append(line.split('$^')[1])
                
    # Create image paths file
    with open('image_paths.txt', 'w') as file:    
        count = 0
        for image_file in image_files:
            file.write(f"file '{input_folder}{image_file}'\noutpoint {durations[count]}\n")
            count += 1
        file.write(f"file '{input_folder}{image_files[-1]}'\noutpoint 0.04\n")

    video_width, video_height = 1280, 720
    ffmpeg_cmd = (
        f"ffmpeg -f concat -safe 0 -i image_paths.txt -vcodec libx264 -r 25 -crf 25 "
        f"-vf \"scale={video_width}:{video_height}:force_original_aspect_ratio=decrease,"
        f"pad={video_width}:{video_height}:(ow-iw)/2:(oh-ih)/2\" -pix_fmt yuv420p output.mp4"
    )
    os.system(ffmpeg_cmd)
    os.remove('image_paths.txt')

    add_sounds(filename)