# 🤟 Indian Sign Language Translator

A comprehensive Python application for bidirectional Indian Sign Language translation using Google's MediaPipe API for real-time hand tracking.

## ✨ Features

### Sign-to-Text Mode
- **Real-time hand tracking** using Google MediaPipe (free API)
- **Precise gesture recognition** with finger-hand angle analysis
- **Multi-hand detection** (supports both single and double-handed signs)
- **Smart cooldown system** (1.5 seconds between words to prevent spam)
- **Live camera feed** with visual hand landmark overlay
- **Sentence building** and conversation history
- **Download conversations** as text files

### Text-to-Sign Mode
- **Text-to-sign conversion** with visual sign display
- **Image/video support** for sign demonstrations
- **Embedded media player** (plays inside the program)
- **Sequential sign display** for full sentences
- **Sign information** from Excel database
- **Download sign sequences** with descriptions

## 🔧 Requirements

- Python 3.8 or higher
- Webcam for sign-to-text mode
- The provided `signs.xlsx` file

## 📦 Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install opencv-python mediapipe numpy pandas Pillow openpyxl
```

### 2. Prepare Sign Media Files (for Text-to-Sign mode)

Create a folder named `sign_media` in the same directory as the program:

```bash
mkdir sign_media
```

Add your sign images or videos with filenames matching the words in the Excel file:
- Supported formats: `.png`, `.jpg`, `.jpeg`, `.gif`, `.mp4`, `.avi`, `.mov`
- Naming convention: `WORD.extension` (e.g., `HELLO.png`, `THANK_YOU.mp4`)
- Use underscores for multi-word signs: `THANK_YOU.png` instead of `THANK YOU.png`

**Example structure:**
```
project_folder/
├── isl_translator.py
├── signs.xlsx
├── requirements.txt
├── sign_media/
│   ├── HELLO.png
│   ├── THANK_YOU.mp4
│   ├── WATER.jpg
│   ├── EAT_FOOD.png
│   └── ...
```

### 3. Place the Excel File

Ensure `signs.xlsx` is in the same directory or update the path in the code (line 66):
```python
df = pd.read_excel('signs.xlsx')  # Update path if needed
```

## 🚀 Usage

### Running the Program

```bash
python isl_translator.py
```

### Mode Selection

Upon launch, choose your mode:
1. **📹 Sign-to-Text**: Use camera to convert signs to text
2. **✍️ Text-to-Sign**: Convert typed text to sign visuals

### Sign-to-Text Mode

1. Click **"▶️ Start Camera"** to activate webcam
2. Grant camera permissions when prompted
3. Perform signs in front of the camera
4. The program will detect and display:
   - Hand landmarks in real-time
   - Detected words
   - Current sentence
5. Click **"💾 Save Sentence"** to add to history
6. Click **"⬇️ Download Chat"** to save conversation
7. Click **"⏸️ Stop Camera"** when done

**Tips for best results:**
- Ensure good lighting
- Keep hands clearly visible
- Wait for the cooldown between words (green "Ready" indicator)
- Follow the sign descriptions from the Excel file

### Text-to-Sign Mode

1. Type your text in the input field
2. Click **"🔄 Convert to Signs"** or press Enter
3. View the sequential sign display showing:
   - Sign images/videos
   - Word labels
   - Hand requirements (single/both)
4. Click **"⬇️ Download Sequence"** to save sign information

## 🎯 Google API Integration

This program uses **Google MediaPipe**, a free and open-source API for:
- **Hand landmark detection** (21 keypoints per hand)
- **Real-time tracking** with high accuracy
- **Multi-hand support** (up to 2 hands)
- **Cross-platform compatibility**

MediaPipe provides:
- Precise finger joint positions
- Hand orientation detection
- Palm direction analysis
- Gesture classification capabilities

## 📊 Sign Recognition Logic

The program uses advanced feature extraction:

### Features Analyzed:
1. **Finger States**: Which fingers are extended
2. **Palm Direction**: Up, down, left, right, forward
3. **Hand Orientation**: Rotation angle in degrees
4. **Finger Angles**: Joint angles for each finger
5. **Hand Position**: High, middle, low in frame
6. **Hand Count**: Single or both hands

### Pattern Matching:
Each sign in the Excel file is matched against these features to ensure:
- **Accurate recognition** even for similar-looking signs
- **Reduced false positives** with multi-feature validation
- **Adaptable system** that can learn new signs

## 📁 File Structure

```
project_folder/
│
├── isl_translator.py          # Main program file
├── requirements.txt            # Python dependencies
├── signs.xlsx                  # Sign language database
├── README.md                   # This file
│
├── sign_media/                 # Media files for signs
│   ├── HELLO.png
│   ├── THANK_YOU.mp4
│   └── ...
│
└── [Generated files]           # Created during use
    ├── ISL_Conversation_*.txt
    └── ISL_SignSequence_*.txt
```

## 🔍 Troubleshooting

### Camera Issues
- **Permission denied**: Grant camera access in system settings
- **Camera not found**: Check if camera is connected and not used by another app
- **Poor detection**: Improve lighting and camera angle

### Import Errors
```bash
# If MediaPipe installation fails, try:
pip install --upgrade pip
pip install mediapipe --no-cache-dir

# For OpenCV issues on Linux:
sudo apt-get install python3-opencv
```

### Media Files Not Showing
- Check filename matches exactly (case-sensitive)
- Verify file is in the `sign_media` folder
- Ensure supported format (.png, .jpg, .mp4, etc.)

## 📝 Excel File Format

The `signs.xlsx` file should have these columns:
- **Word**: The sign/word name (e.g., "HELLO", "THANK YOU")
- **Hand(s)**: "Single" or "Both"
- **Description**: How to perform the sign

## 🎨 Customization

### Adjust Cooldown Time
Edit line 35 in `isl_translator.py`:
```python
self.cooldown_duration = 1.5  # Change to desired seconds
```

### Change Detection Confidence
Edit lines 341-344:
```python
self.hands = self.mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,  # Adjust (0.0-1.0)
    min_tracking_confidence=0.7    # Adjust (0.0-1.0)
)
```

### Add New Signs
1. Add entry to `signs.xlsx`
2. Add media file to `sign_media/` folder
3. Implement pattern matching in `match_sign_pattern()` method (line 583)

## 💡 Tips for Creating Sign Media

### For Images:
- Use clear, high-contrast backgrounds
- Show hand position clearly
- Resolution: 800x600 or higher
- Format: PNG for transparency, JPG for photos

### For Videos:
- Duration: 2-5 seconds
- Show complete sign motion
- Good lighting
- Format: MP4 (most compatible)

## 📄 License

This project is created for educational purposes. MediaPipe is licensed under Apache 2.0.

## 🙏 Acknowledgments

- **Google MediaPipe** for hand tracking technology
- Indian Sign Language standards and community
- Open-source Python community

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Verify all dependencies are installed
3. Ensure camera permissions are granted
4. Check that `signs.xlsx` is in the correct location

---

**Version**: 1.0  
**Created**: 2026  
**Purpose**: Bridging communication barriers through technology
