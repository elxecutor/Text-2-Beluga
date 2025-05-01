# Text 2 Beluga 🎥💬

Effortlessly transform plain text files into dynamic, Discord-style conversation videos with rich text formatting, immersive sound effects, and extensive customization—all completely **free** and in **seconds**!

## Features ✨

- 🖼️ **Automatic Message Rendering**: Generate Discord-style message images from plain text.
- 🔊 **Sound Effect Integration**: Enhance your videos with immersive sound effects and join/leave notifications.
- 🎞️ **Video Compilation**: Seamlessly stitch images into MP4 videos with precise timing.
- 📝 **Script Validation**: Enjoy built-in error checks for your chat script.
- 😎 **Advanced Formatting**: Supports:
    - **Bold** and *italic* text
    - Combined ***bold italic***
    - ~~Strikethrough~~ text
    - Native emoji support
    - **Code Blocks & Monospace:** Use triple backticks to denote code blocks (e.g., ```...```) so that your code is rendered in a clear monospace font.
    - **Links:** Any URL starting with `http://` or `https://` is automatically parsed and styled (often with an underline and a blue hue).
    - Mentions (`@Character`) and channel tags (`#channel`)
    - Custom durations per message
    - Custom character creation with auto-generated role colors

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
     - Place profile pictures in the `assets/profile_pictures/temp/` directory.
     - Edit character details in `assets/profile_pictures/characters.json`.

## Chat Script Format 📜

Define your conversation script in the `utils/conversation.json` file using the structure outlined in `templates/conversation.json`. For example:

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
        "text": "```def hello():```",
        "duration": 1,
        "sound": "SoundEffect"
    },
    {
        "type": "message",
        "actor": "Character",
        "text": "```    print(\"Hello, World!\")\n``",
        "duration": 1,
        "sound": "SoundEffect"
    },
    {
        "type": "message",
        "actor": "Character",
        "text": "https://www.example.com",
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
- **Code Blocks (Monospace):**  
  Wrap your code with triple backticks. For example:
    ```bash
    ```def hello():```
    ```    print(\"Hello, World!\")\n```
    ```
- **Links:**  
  Simply include the full URL (e.g., `https://www.example.com`), and it will be parsed and highlighted.
- **Mentions:** `@Character`
- **Channel Tags:** `#channel`
- **Emojis:** Use directly in your message text

## Running the Program 🚀

1. **Prepare your chat script file** in `utils/conversation.json`.
2. **Execute the main script:**
     ```bash
     python main.py
     ```
3. **Output:**  
     Chat images are saved in the `chat/` directory and the final video (`final_video.mp4`) is created in the `output/` directory.

## Font Note 🗒️

By default, **Whitney** is used. The sample video preview mentions Discord’s proprietary `gg sans` font which is not publicly available. To use `gg sans`:
- Download the [ggsans folder](https://drive.google.com/drive/folders/1Zm8c2o-bStC7nsAGMXALdMVuCkU1hQFY?usp=drive_link).
- Place it in the `assets/fonts/` directory.
- Update the `font` variable in `scripts/generate_chat.py` to `"ggsans"`.

## TODO ✏️

Check out the [TODO list](NOTES.md) for upcoming features and improvements.  
*Developing a dedicated Text-2-Beluga Discord bot is currently a top priority.*

