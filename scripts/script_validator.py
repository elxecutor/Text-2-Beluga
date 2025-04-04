import os
import sys
import re
import argparse
from PyQt5.QtWidgets import QApplication, QFileDialog

base_dir = os.path.dirname(os.path.abspath(__file__))

def get_filename():
    """Opens a file dialog and returns the selected filename."""
    app = QApplication(sys.argv)
    options = QFileDialog.Options()
    filename, _ = QFileDialog.getOpenFileName(
        None, "Select Script Text File", "", "Text Files (*.txt);;All Files (*)", options=options
    )
    app.exit()
    return filename

def validate_script_lines(lines):
    errors = []
    state = "waiting_for_name"
    current_name = None
    typing_expected = False

    for idx, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if line == "":
            state = "waiting_for_name"
            current_name = None
            continue
        if line.startswith("#"):
            continue
        if line.startswith("WELCOME "):
            continue

        if state == "waiting_for_name":
            if ':' not in line:
                errors.append(f"Line {idx}: Expected name line with ':'")
            else:
                # Check for typing toggle syntax
                if '^:' in line:
                    if line.count('^:') != 1:
                        errors.append(f"Line {idx}: Invalid typing toggle syntax")
                    current_name = line.split('^:', 1)[0].strip()
                    typing_expected = True
                else:
                    current_name = line.split(':', 1)[0].strip()
                    typing_expected = False
                
                if not current_name:
                    errors.append(f"Line {idx}: Empty character name")
                elif current_name not in characters_dict:
                    errors.append(f"Line {idx}: Character '{current_name}' not found")
                
                state = "expecting_message"
        elif state == "expecting_message":
            if '$^' not in line:
                errors.append(f"Line {idx}: Missing '$^' delimiter in message")
            else:
                # Validate duration and sound effect
                parts = line.split('$^', 1)
                duration_part = parts[1].strip()
                
                if '#!' in duration_part:
                    dur_str, sound_marker = duration_part.split('#!', 1)
                    dur_str = dur_str.strip()
                    sound_name = sound_marker.strip()
                    sound_path = os.path.join(
                        base_dir, os.pardir, "assets", "sounds", "mp3", 
                        f"{sound_name}.mp3"
                    )
                    if not os.path.isfile(sound_path):
                        errors.append(f"Line {idx}: Sound '{sound_name}' not found")
                else:
                    dur_str = duration_part
                
                try:
                    float(dur_str)
                except ValueError:
                    errors.append(f"Line {idx}: Invalid duration '{dur_str}'")
                
                state = "waiting_for_name"

    return errors
def main():
    parser = argparse.ArgumentParser(description="Validate a script text file for chat generation.")
    parser.add_argument("script_file", nargs="?", help="Path to the script text file. If not provided, a file dialog will open.")
    args = parser.parse_args()

    if args.script_file:
        filename = args.script_file
    else:
        filename = get_filename()

    if not filename or not os.path.isfile(filename):
        print("No valid file selected. Exiting.")
        sys.exit(1)

    with open(filename, encoding="utf8") as f:
        lines = f.read().splitlines()

    errors = validate_script_lines(lines)

    if errors:
        print("Script validation found issues:")
        for error in errors:
            print("  -", error)
    else:
        print("Script validation successful: no problems found.")

if __name__ == '__main__':
    # main()
    print('Please run the main.py script!')