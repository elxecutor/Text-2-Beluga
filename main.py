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
    with open(args.conversation, encoding='utf8') as f:
        convo = json.load(f)

    errs = validate(convo, cfg)
    if errs:
        print("Validation failed:", *errs, sep="\n - ")
        sys.exit(1)

    with open(args.characters, encoding='utf8') as f:
        chars = json.load(f)
    save_images(cfg, convo, chars)
    compile_video(cfg, convo)

    # mix in sounds
    sound_main_args = [
      '--config',       args.config,
      '--conversation', args.conversation,
      '--input-video',  cfg['paths']['ffmpeg_output'],
      '--output-video', cfg['paths']['final_video']
    ]
    # Call sound_main with the prepared arguments
    original_argv = sys.argv
    sys.argv = ['sound_effects.py'] + sound_main_args
    sound_main()
    sys.argv = original_argv

    # Clean up temporary files after final video creation (if enabled)
    if cfg.get('video_settings', {}).get('cleanup_temp_files', True):
        chat_folder = cfg['paths']['chat_output']
        if os.path.exists(chat_folder):
            try:
                import shutil
                shutil.rmtree(chat_folder)
                print(f"✅ Cleaned up temporary chat images: {chat_folder}")
            except Exception as e:
                print(f"⚠️ Warning: Could not clean up chat folder: {e}")
        else:
            print("ℹ️  No chat folder found to cleanup")
    else:
        print("ℹ️  Cleanup disabled - temporary chat images preserved")

    print("✅ All done! Final video at", cfg['paths']['final_video'])

if __name__=='__main__':
    main()
