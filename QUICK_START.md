# 🚀 QUICK START GUIDE - ISL Translator

## Fastest Way to Get Started (3 Steps!)

### Step 1: Install Dependencies
```bash
pip install opencv-python mediapipe numpy pandas Pillow openpyxl
```

Or use the requirements file:
```bash
pip install -r requirements.txt
```

### Step 2: Run Setup (Optional but Recommended)
```bash
python setup.py
```
This will check everything and create necessary folders.

### Step 3: Run the Program
```bash
python isl_translator.py
```

---

## First Time Usage

### Mode 1: Sign-to-Text (Camera Tracking)
1. Launch program → Select "Sign-to-Text"
2. Click "Start Camera"
3. Grant camera permission
4. Make signs in front of camera
5. Watch words appear on screen!

### Mode 2: Text-to-Sign (Display Signs)
1. Launch program → Select "Text-to-Sign"
2. Type a sentence (e.g., "HELLO THANK YOU")
3. Click "Convert to Signs"
4. View the sign sequence!

**Note:** For text-to-sign, you'll need to add images/videos to the `sign_media/` folder first.

---

## What's Included

### 📁 Files You Have:
- `isl_translator.py` - Main program (complete code)
- `signs.xlsx` - Sign language database (22 signs)
- `requirements.txt` - Python packages needed
- `setup.py` - Automated setup helper
- `README.md` - Full documentation
- `ADDING_SIGNS_GUIDE.md` - How to add more signs

### 📁 Folders to Create:
- `sign_media/` - Put your sign images/videos here
  - Example: `HELLO.png`, `THANK_YOU.mp4`

---

## Key Features ✨

### Google MediaPipe Integration
✅ Uses Google's free MediaPipe API for hand tracking  
✅ Detects 21 hand landmarks per hand  
✅ Tracks up to 2 hands simultaneously  
✅ Real-time processing at 30+ FPS  

### Smart Recognition
✅ Analyzes finger positions, angles, and orientations  
✅ Distinguishes between similar-looking signs  
✅ 1.5-second cooldown prevents word spam  
✅ Supports both single and double-handed signs  

### User-Friendly Interface
✅ Clean, modern GUI with Tkinter  
✅ Live camera feed with hand landmark overlay  
✅ Conversation history tracking  
✅ Download conversations as text files  
✅ Embedded media player (no external players needed)  

---

## Troubleshooting Quick Fixes

### "Camera not found"
→ Check camera is connected and not used by another app  
→ Grant camera permissions in system settings

### "Module not found"
→ Run: `pip install [module-name]`  
→ Or run: `python setup.py` to auto-install

### "No sign detected"
→ Improve lighting  
→ Keep hands clearly visible  
→ Wait for green "Ready" indicator  
→ Follow sign descriptions from Excel file

### Media not showing in Text-to-Sign
→ Create `sign_media/` folder  
→ Add files named exactly as words in Excel (e.g., `HELLO.png`)  
→ Use supported formats: .png, .jpg, .mp4, .avi

---

## Next Steps

1. ✅ **Run the program** - Try both modes
2. 📸 **Add sign media** - Create/download sign images/videos
3. 📊 **Expand database** - Add more signs to Excel file
4. 🔧 **Customize** - Adjust cooldown, confidence levels
5. 🤝 **Share** - Help others bridge communication gaps!

---

## Current Sign Database (22 Signs)

Your `signs.xlsx` includes:
- YOU, ME/I, HELLO, THANK YOU, PLEASE
- WATER, EAT/FOOD, WANT, HELP, SORRY
- YES, NO, GOOD, BAD, MORE
- And more...

**Want to add more?** Check `ADDING_SIGNS_GUIDE.md`

---

## Important Notes 📌

### For Different PCs:
- Program is self-contained
- Media plays inside the program
- No external video player needed
- All paths are relative (portable)

### Saving Conversations:
- Click "Download Chat" anytime
- Files saved to program directory
- Format: `ISL_Conversation_YYYYMMDD_HHMMSS.txt`

### Media Folder:
- Place media files in `sign_media/` folder
- Program finds them automatically
- Works with images AND videos
- Videos show first frame + play icon

---

## System Requirements

- **OS**: Windows, Mac, or Linux
- **Python**: 3.8 or higher
- **Camera**: Any webcam (for Sign-to-Text)
- **RAM**: 4GB minimum
- **Storage**: 500MB for dependencies

---

## Support & Help

📖 **Full Documentation**: Read `README.md`  
🔧 **Adding Signs**: Read `ADDING_SIGNS_GUIDE.md`  
🐛 **Setup Issues**: Run `python setup.py` for diagnostics  

---

## Example Session

```
1. python isl_translator.py
2. Select "Sign-to-Text"
3. Click "Start Camera"
4. Show "HELLO" sign → Detected!
5. Show "THANK YOU" sign → Detected!
6. Click "Save Sentence" → Added to history
7. Click "Download Chat" → Saved!
```

---

**You're all set! Enjoy bridging communication barriers! 🤟**

*Version 1.0 | Complete & Ready to Use*
