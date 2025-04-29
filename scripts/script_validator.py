# scripts/script_validator.py

import os, sys, json, argparse

def load_config(path):
    return json.load(open(path, encoding='utf8'))

def validate(convo, config):
    errors = []
    codes = set(config['sound_codes'])
    sd = config['paths']['sound_dir']
    for idx, ev in enumerate(convo, 1):
        if ev.get('type') not in ('join','message'):
            errors.append(f"#{idx}: bad type {ev.get('type')}")
        if 'actor' not in ev:
            errors.append(f"#{idx}: missing actor")
        if 'sound' not in ev or ev['sound'] not in codes:
            errors.append(f"#{idx}: invalid sound '{ev.get('sound')}'")
        if ev['type']=='message':
            if 'text' not in ev or not ev['text']:
                errors.append(f"#{idx}: empty text")
            if 'duration' not in ev:
                errors.append(f"#{idx}: missing duration")
            else:
                try:
                    float(ev['duration'])
                except:
                    errors.append(f"#{idx}: bad duration '{ev['duration']}'")
        else:
            if 'duration' not in ev:
                errors.append(f"#{idx}: missing duration for join")
        fn = os.path.join(sd, f"{ev['sound']}.mp3")
        if not os.path.isfile(fn):
            errors.append(f"#{idx}: file not found {fn}")
    return errors

def main():
    p = argparse.ArgumentParser()
    p.add_argument('config')
    p.add_argument('conversation')
    args = p.parse_args()

    cfg = load_config(args.config)
    convo = json.load(open(args.conversation, encoding='utf8'))
    errs = validate(convo, cfg)
    if errs:
        print("Errors:")
        for e in errs: print(" -", e)
        sys.exit(1)
    print("Validation OK.")

if __name__=='__main__':
    main()
