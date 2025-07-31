# scripts/script_validator.py

import os, sys, json, argparse

def load_config(path):
    with open(path, encoding='utf8') as f:
        return json.load(f)

def validate(convo, config):
    errors = []
    warnings = []
    codes = set(config['sound_codes'])
    sd = config['paths']['sound_dir']
    
    valid_types = ('join', 'leave', 'message', 'typing')
    valid_attachment_types = ('image', 'gif', 'text', 'file')
    
    for idx, ev in enumerate(convo, 1):
        # Validate event type
        if ev.get('type') not in valid_types:
            errors.append(f"#{idx}: bad type '{ev.get('type')}', valid types: {valid_types}")
        
        # Validate actor
        if 'actor' not in ev:
            errors.append(f"#{idx}: missing actor")
        
        # Validate sound
        if 'sound' not in ev or ev['sound'] not in codes:
            errors.append(f"#{idx}: invalid sound '{ev.get('sound')}', available sounds: {sorted(codes)}")
        
        # Validate duration
        if 'duration' not in ev:
            errors.append(f"#{idx}: missing duration")
        else:
            try:
                dur = float(ev['duration'])
                if dur <= 0:
                    errors.append(f"#{idx}: duration must be positive, got {dur}")
                elif dur > 30:
                    warnings.append(f"#{idx}: duration {dur}s is quite long, consider breaking into smaller segments")
            except:
                errors.append(f"#{idx}: bad duration '{ev['duration']}'")
        
        # Typing-specific validation
        if ev['type'] == 'typing':
            # Typing events should have reasonable durations
            if 'duration' in ev:
                try:
                    dur = float(ev['duration'])
                    if dur > 10:
                        warnings.append(f"#{idx}: typing duration {dur}s is very long")
                except:
                    pass
        if ev['type'] == 'message':
            if 'text' not in ev or not ev['text'].strip():
                errors.append(f"#{idx}: empty or missing text")
            
            # Validate attachments if present
            if 'attachments' in ev:
                for att_idx, att in enumerate(ev['attachments']):
                    if 'type' not in att or att['type'] not in valid_attachment_types:
                        errors.append(f"#{idx}: attachment {att_idx+1} has invalid type '{att.get('type')}'")
                    if 'path' not in att:
                        errors.append(f"#{idx}: attachment {att_idx+1} missing path")
                    elif not os.path.exists(att['path']):
                        errors.append(f"#{idx}: attachment file not found: {att['path']}")
            
            # Validate background music if present
            if 'background_music' in ev:
                bg_file = os.path.join(sd, f"{ev['background_music']}.mp3")
                if not os.path.isfile(bg_file):
                    errors.append(f"#{idx}: background music file not found: {bg_file}")
        
        # Validate sound file exists
        sound_file = os.path.join(sd, f"{ev['sound']}.mp3")
        if not os.path.isfile(sound_file):
            errors.append(f"#{idx}: sound file not found {sound_file}")
    
    # Print warnings
    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f" - {w}")
    
    return errors

def main():
    p = argparse.ArgumentParser()
    p.add_argument('config')
    p.add_argument('conversation')
    args = p.parse_args()

    cfg = load_config(args.config)
    with open(args.conversation, encoding='utf8') as f:
        convo = json.load(f)
    errs = validate(convo, cfg)
    if errs:
        print("Errors:")
        for e in errs: print(" -", e)
        sys.exit(1)
    print("Validation OK.")

if __name__=='__main__':
    main()
