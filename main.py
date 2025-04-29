# main.py

import argparse, sys, json
from scripts.script_validator import load_config, validate
from scripts.generate_chat    import save_images
from scripts.compile_images   import compile_video
from scripts.sound_effects    import main as sound_main

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--config',       default='utils/config.json')
    p.add_argument('--conversation', default='utils/conversation.json')
    p.add_argument('--characters',   default='utils/characters.json')
    args = p.parse_args()

    cfg   = load_config(args.config)
    convo = json.load(open(args.conversation, encoding='utf8'))

    errs = validate(convo, cfg)
    if errs:
        print("Validation failed:", *errs, sep="\n - ")
        sys.exit(1)

    save_images(cfg, convo, json.load(open(args.characters, encoding='utf8')))
    compile_video(cfg, convo)

    # mix in sounds
    sound_main_args = [
      '--config',       args.config,
      '--conversation', args.conversation,
      '--input-video',  cfg['paths']['ffmpeg_output'],
      '--output-video', cfg['paths']['final_video']
    ]
    # you can invoke sound_main via subprocess if needed, or adapt its signature
    sound_main()

    print("✅ All done! Final video at", cfg['paths']['final_video'])

if __name__=='__main__':
    main()
