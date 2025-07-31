# Text 2 Beluga 🎥💬

Ef## Prerequisites 📋

- [Python 3.9+](https://www.python.org/downloads/)
- [FFmpeg](https://ffmpeg.org/download.html) (ensure it's added to your system PATH)
- Required Python## Font Note 🗒️

By default, **Whitney** is used. The sample video preview mentions Discord's proprietary `gg sans` font which is not publicly available. To use `gg sans`:
- Download the [ggsans folder](https://drive.google.com/drive/folders/1Zm8c2o-bStC7nsAGMXALdMVuCkU1hQFY?usp=drive_link).
- Place it in the `assets/fonts/` directory.
- Update the font configuration in `utils/config.json`.

## Technical Features 🔧

### Message Rendering Engine
- **Dynamic Height Calculation**: Message blocks auto-resize based on content length
- **Smart Text Wrapping**: Intelligent line breaking with emoji spacing consideration  
- **Font Metrics**: Accurate text measurement using PIL font metrics
- **Attachment Processing**: Automatic image resizing and GIF handling

### Emoji Processing
- **Unicode Support**: Full emoji range detection (U+1F300-U+1FAFF, U+2600-U+27BF)
- **Automatic Spacing**: 4px left + 8px right padding to prevent congestion
- **Sequence Handling**: Multiple consecutive emojis treated as single units
- **Regex-Based Parsing**: Sophisticated pattern matching for emoji detection

### Performance Optimizations
- **Efficient Parsing**: Single-pass regex parsing for all text formatting
- **Memory Management**: Images closed after processing to prevent memory leaks
- **Caching**: Font objects cached for faster rendering
- **Background Processing**: Non-blocking video compilation

### Recent Improvements
- ✅ Removed visual effects system for cleaner codebase
- ✅ Enhanced auto-resizing message blocks
- ✅ Improved emoji spacing with regex-based approach
- ✅ Better text wrapping for emojis at line ends
- ✅ Removed code block and fancy text parsing for simplicityges (automatically installed):
    - `Pillow` - Image processing and manipulation
    - `pilmoji` - Emoji rendering support
    - Additional dependencies listed in `requirements.txt`

### System Requirements
- **OS**: Windows, macOS, or Linux
- **RAM**: 2GB+ recommended for large conversations
- **Storage**: 100MB+ for assets and output videos
- **Network**: Not required for core functionalityly transform plain text files into dynamic, Discord-style conversation videos with rich text formatting, immersive sound effects, and extensive customization—all completely **free** and in **seconds**!

## Features ✨

- 🖼️ **Automatic Message Rendering**: Generate Discord-style message images from plain text with dynamic height calculation
- 🔊 **Sound Effect Integration**: Enhance your videos with immersive sound effects and join/leave notifications
- 🎞️ **Video Compilation**: Seamlessly stitch images into MP4 videos with precise timing using FFmpeg
- 🧹 **Automatic Cleanup**: Optional automatic removal of temporary image files after video creation
- 📝 **Script Validation**: Built-in error checks for chat scripts with comprehensive validation
- 📎 **Attachment Support**: Display images, GIFs, and file attachments with auto-resizing
- 🎵 **Background Music**: Add individual background music tracks to messages
- ⌨️ **Typing Indicators**: Show "user is typing..." animations with visual dots
- **Smart Text Wrapping**: Intelligent text wrapping with emoji spacing consideration
- 😊 **Enhanced Emoji Support**: Automatic emoji spacing to prevent congestion
- **Auto-Resizing Blocks**: Message blocks automatically resize based on content length
- 😎 **Advanced Text Formatting**: Supports:
    - **Bold** and *italic* text
    - Combined ***bold italic***
    - ~~Strikethrough~~ text
    - Native emoji support with proper spacing
    - **Links:** URLs starting with `http://` or `https://` are automatically parsed and styled
    - Mentions (`@Character`) and channel tags (`#channel`)
    - Custom durations per message
    - Custom character creation with role colors and badges

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
     git clone https://github.com/elxecutor/Text-2-Beluga.git
     cd Text-2-Beluga
     ```
2. **Install dependencies:**
     ```bash
     pip install -r requirements.txt
     ```
3. **Configure Characters:**
     - Place profile pictures in the `assets/profile_pictures/temp/` directory
     - Edit character details in `utils/characters.json`
     - Assign role colors and badges in the character configuration

4. **Verify Setup:**
     ```bash
     python main.py --help  # Check if everything is working
     ```

## Chat Script Format 📜

Define your conversation script in the `utils/conversation.json` file. The script supports various message types and rich formatting:

### Basic Message Structure
```json
[
    {
        "type": "join",
        "actor": "Character",
        "duration": 1.0,
        "sound": "join"
    },
    {
        "type": "message",
        "actor": "Character", 
        "text": "Hello **everyone**! Check out this link: https://example.com 🎉",
        "duration": 3.0,
        "sound": "message"
    },
    {
        "type": "leave",
        "actor": "Character",
        "duration": 1.0,
        "sound": "leave"
    }
]
```

### Message Types Available
- `"join"` - Character joins the chat
- `"leave"` - Character leaves the chat  
- `"message"` - Regular text message
- `"typing"` - Typing indicator animation

### Text Formatting Syntax
- **Bold:** `**text**`
- *Italic:* `*text*`
- ***Bold Italic:*** `***text***`
- ~~Strikethrough:~~ `~~text~~`
- **Links:** `https://example.com` (auto-detected)
- **Mentions:** `@Character`
- **Channels:** `#general`
- **Emojis:** Use directly: `🎉😎🔥`

### Extended Features Examples

**Attachments:**
```json
{
    "type": "message",
    "actor": "Character",
    "text": "Check out this image!",
    "duration": 3,
    "sound": "message",
    "attachments": [
        {
            "type": "image",
            "path": "path/to/image.png",
            "filename": "image.png"
        }
    ]
}
```

**Background Music:**
```json
{
    "type": "message",
    "actor": "Character",
    "text": "This message has background music!",
    "duration": 4,
    "sound": "message",
    "background_music": "chill_beat"
}
```

**Typing Indicator:**
```json
{
    "type": "typing",
    "actor": "Character",
    "duration": 2,
    "sound": "typing"
}
```

## Running the Program 🚀

### Quick Start
1. **Prepare your chat script** in `utils/conversation.json`
2. **Configure characters** in `utils/characters.json`  
3. **Execute the main script:**
     ```bash
     python main.py
     ```

### Command Line Options
```bash
python main.py --config utils/config.json --conversation utils/conversation.json --characters utils/characters.json
```

### Output Structure
- **Chat Images**: Saved in `chat/` directory (001.png, 002.png, etc.)
- **Final Video**: Created as `output/final_video.mp4`
- **Processing Log**: Shows progress and any validation errors

### Performance Tips
- **Large conversations**: Process in smaller batches for better performance
- **High-resolution**: Adjust image quality settings in `config.json`
- **Memory usage**: Close other applications for smoother processing

### Configuration Options 🔧

#### Video Settings (`utils/config.json`)
```json
"video_settings": {
    "fade_transitions": false,
    "fade_duration": 0.3,
    "frame_rate": 25,
    "quality": 25,
    "cleanup_temp_files": true
}
```

- **`cleanup_temp_files`**: When `true` (default), automatically removes temporary chat images after video creation to save disk space. Set to `false` to preserve images for debugging or manual review.

## Font Note 🗒️

By default, **Whitney** is used. The sample video preview mentions Discord’s proprietary `gg sans` font which is not publicly available. To use `gg sans`:
- Download the [ggsans folder](https://drive.google.com/drive/folders/1Zm8c2o-bStC7nsAGMXALdMVuCkU1hQFY?usp=drive_link).
- Place it in the `assets/fonts/` directory.
- Update the `font` variable in `scripts/generate_chat.py` to `"ggsans"`.

## TODO ✏️

Check out the [TODO list](TODO.md) for upcoming features and improvements.

### Planned Features
- 🤖 **Discord Bot Integration**: Dedicated Text-2-Beluga Discord bot (top priority)
- 🎨 **Theme System**: Multiple Discord themes (dark, light, custom)
- 🔊 **Advanced Audio**: Better sound mixing and audio effects
- 📱 **Mobile Support**: Responsive layouts for different screen sizes
- 🔄 **Real-time Preview**: Live preview while editing conversations
- 🛠️ **GUI Interface**: User-friendly graphical interface
- 📊 **Analytics**: Video engagement and performance metrics

### Contributing
Contributions are welcome! Please check the issues page for current development needs.

---

*Developing a dedicated Text-2-Beluga Discord bot is currently a top priority.*

