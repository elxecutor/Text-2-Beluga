# main.py

import argparse, sys, json
from scripts.script_validator import load_config, validate
from scripts.generate_chat    import save_images, load_config as _lc_gc, load_characters
from scripts.compile_images   import compile_video, load_config as _lc_ci
from scripts.sound_effects    import main as sound_main

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--config',       default='config.json')
    p.add_argument('--conversation', default='conversation.json')
    p.add_argument('--characters',   default='assets/profile_pictures/characters.json')
    args = p.parse_args()

    cfg   = load_config(args.config)
    convo = json.load(open(args.conversation, encoding='utf8'))

    errs = validate(convo, cfg)
    if errs:
        print("Validation failed:", *errs, sep="\n - ")
        sys.exit(1)

    # 1) generate chat images
    save_images(cfg, convo,
                load_characters(args.characters))

    # 2) compile silent video
    compile_video(cfg, convo)

    # 3) mix in sounds
    sound_main_args = [
        '--config',       args.config,
        '--conversation', args.conversation,
        '--input-video',  cfg['paths']['ffmpeg_output'],
        '--output-video', cfg['paths']['final_video']
    ]
    sound_main()  # or call via subprocess if you prefer

    print("All done! Final video at", cfg['paths']['final_video'])

if __name__=='__main__':
    main()
