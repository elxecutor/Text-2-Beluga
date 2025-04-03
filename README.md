# Text 2 Beluga 🎥💬

Convert plain text files into professional Beluga-style Discord conversation videos in seconds. Enjoy an array of text formatting options, integrated sound effects, and extensive customization – all available ***free of charge***.

---

## Overview

Text 2 Beluga is engineered for efficiency and precision. It automatically renders Discord-style messages, compiles video sequences with proper timing, and validates your script for errors. Whether you’re a casual creator or a professional content producer, this tool ensures a seamless transition from script to video.

---

## Key Features ✨

- **Automatic Message Rendering**  
  Generates Discord-style message images directly from your text.
  
- **Sound Effect Integration**  
  Enhances videos with impact sounds and join notifications.
  
- **Video Compilation**  
  Compiles chat images into a smooth MP4 video, perfectly timed.
  
- **Script Validation**  
  Checks for syntax errors, missing durations, and invalid sound effect references.
  
- **Advanced Formatting Support**  
  - **Text Styling:** Bold, italic, and combined formatting (e.g., `__**text**__`)
  - **Mentions & Emojis:** Tag characters (`@Character`) and use emojis seamlessly.
  - **Custom Timings:** Define message display durations.
  - **Character Customization:** Create custom characters with unique profile images and roll colours.

---

## Prerequisites 📋

- **Python 3.9+**  
  [Download Python](https://www.python.org/downloads/)

- **FFmpeg**  
  Ensure FFmpeg is installed and added to your system PATH.  
  [Download FFmpeg](https://ffmpeg.org/download.html)

- **Python Packages**  
  Install required packages via:
  ```bash
  pip install -r requirements.txt
  ```

---

## Installation & Setup 🛠

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/noiz-x/Text-2-Beluga.git
    cd Text-2-Beluga
    ```

2. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Configure Character Settings:**
   - Add profile pictures to `assets/profile_pictures/temp/`
   - Edit character details in `assets/profile_pictures/characters.json`

---

## Chat Script Format 📜

Create a text file (`.txt`) that adheres to the following structure.

### Script Structure

```txt
WELCOME Character$^Duration#!SoundEffect

Character:
Message Text$^Duration#!SoundEffect
Another Message$^Duration
```

### Syntax Rules

1. **Comments:**  
   Lines starting with `#` are ignored.

2. **Join Messages:**  
   Format:  
   `WELCOME Character$^Duration#!SoundEffect`  
   (Creates a "User joined" image.)

3. **Character Messages:**  
   - Begin with `Character:` to declare the speaker.
   - Subsequent lines must follow the format:  
     `Message$^Duration[#!SoundEffect]`

4. **Formatting Guidelines:**
   - **Bold:** `**text**`
   - **Italic:** `__text__`
   - **Combined:** `__**text**__`
   - **Mentions:** Use `@Character` to mention another character.
   - **Emojis:** Emojis are fully supported.
   - **Durations:** Append `$^` followed by the duration in seconds at the end of each message (mandatory).
   - **Sound Effects:** Append `#!` followed by the sound effect name (optional). Files should be placed in `assets/sounds/mp3/`.

---

## Running the Program 🚀

1. **Prepare your Script File.**

2. **Execute the Main Script:**
    ```bash
    python3 scripts/main.py
    ```

3. **Program Options:**
   - **Generate Video:**  
     Compiles chat images into `final_video.mp4` (located in the project root).
   - **Validate Script:**  
     Checks your script for common errors such as:
       - Missing duration markers (`$^`)
       - Incorrect sound effect references
       - Syntax errors
       - Unspecified character declarations
   - **Instructions:**  
     Displays detailed syntax instructions and available sound effects.  
     *(To add custom sounds, place the corresponding `.mp3` file in `assets/sounds/mp3/`.)*
   - **Exit:**  
     Terminates the program.

4. **Output:**  
   When "Generate Video" is selected, the program creates chat images in the `chat/` directory and compiles them into a single MP4 video with integrated sound effects.

---

## Font Details 🗒️

- **Default Font:**  
  The repository uses `Whitney` by default. You can replace it with any preferred font by updating the files in `assets/fonts/`.

---

## Upcoming Enhancements ✏️
For the latest updates, refer to the [TODO list](NOTES.md).