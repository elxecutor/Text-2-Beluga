# Text 2 Beluga 🎥💬

Effortlessly transform plain text files into dynamic, Discord-style conversation videos with rich text formatting, immersive sound effects, and extensive customization—all completely **free** and in **seconds**!

## Features ✨

- 🖼️ **Automatic Message Rendering**: Generate Discord-style message images from text.
- 🔊 **Sound Effect Integration**: Add immersive sound effects and join notifications.
- 🎞️ **Video Compilation**: Seamlessly compile images into MP4 videos with precise timing.
- 📝 **Script Validation**: Built-in error checking for your chat script.
- 😎 **Advanced Formatting**: Supports:
    - **Bold** and *italic* text
    - Native emoji support
    - Mentions
    - Custom durations for each message
    - Custom character creation
    - Auto-generated character colors

## Prerequisites 📋

- [Python 3.9+](https://www.python.org/downloads/)
- [FFmpeg](https://ffmpeg.org/download.html) (ensure it’s added to your system PATH)
- Required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

## Installation & Setup 🛠

1. **Clone the repository:**
    ```bash
    git clone https://github.com/noiz-x/Text-2-Beluga.git
    cd Text-2-Beluga
    ```
2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3. **Configure Characters:**
    - Place profile pictures in `assets/profile_pictures/temp/`.
    - Edit character details in `assets/profile_pictures/characters.json`.

## Chat Script Format 📜

Define your conversation script in the `utils/conversation.json` file following the template provided in `templates/conversation.json`. This JSON file establishes the structure required for your conversation entries.

Below is an example JSON template to define your conversation script:

```json
[
    {
        "type": "join",
        "actor": "Character",
        "duration": 1,
        "sound": "SoundEffect"
    },
    {
        "type": "message",
        "actor": "Character",
        "text": "Message Text",
        "duration": 1,
        "sound": "SoundEffect"
    },
    {
        "type": "leave",
        "actor": "Character",
        "duration": 1,
        "sound": "SoundEffect"
    }
]
```

### Syntax Guidelines

**Formatting Options:**
- **Bold:** `**text**`
- *Italic:* `*text*`
- **Combined:** `***text***`
- **Strikethrough:** `~text~`
- **Mention:** Use `@Character`
- **Channel Mention:** Use `#channel`
- **Emojis:** Supported directly in messages.


## Running the Program 🚀

1. **Prepare your chat script file.**
2. **Run the main script:**
    ```bash
    python main.py
    ```
3. **Output:**  
   The processed chat images are saved in the `chat/` directory, and the final video (`final_video.mp4`) is generated in the `output/` directory.

## Font Note 🗒️

The sample video preview uses Discord’s proprietary `gg sans` font, which isn’t available for public use.  
By default, **Whitney** is used. To switch to `gg sans`:
- Download the [ggsans folder](https://drive.google.com/drive/folders/1Zm8c2o-bStC7nsAGMXALdMVuCkU1hQFY?usp=drive_link).
- Place it in the `assets/fonts/` directory.
- Update the `font` variable in `scripts/generate_chat.py` to `"ggsans"`.

## TODO ✏️

Check out the [TODO list](NOTES.md) for upcoming features and improvements.  
Developing a dedicated Text-2-Beluga Discord bot is currently a top priority.
