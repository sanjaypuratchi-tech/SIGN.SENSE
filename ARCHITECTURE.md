# ISL Translator - System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     ISL TRANSLATOR SYSTEM                       │
└─────────────────────────────────────────────────────────────────┘

                        ┌─────────────┐
                        │   User      │
                        │  Interface  │
                        └──────┬──────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
            ┌───────▼────────┐   ┌───────▼────────┐
            │  Sign-to-Text  │   │  Text-to-Sign  │
            │      Mode      │   │      Mode      │
            └───────┬────────┘   └───────┬────────┘
                    │                     │
         ┌──────────┴──────────┐         │
         │                     │         │
    ┌────▼────┐        ┌──────▼─────┐   │
    │ Camera  │        │  MediaPipe │   │
    │  Input  │        │  Hand API  │   │
    └────┬────┘        └──────┬─────┘   │
         │                     │         │
         └──────────┬──────────┘         │
                    │                     │
              ┌─────▼──────┐      ┌──────▼─────┐
              │   Hand     │      │   Media    │
              │ Recognition│      │  Display   │
              └─────┬──────┘      └──────┬─────┘
                    │                     │
                    └──────────┬──────────┘
                               │
                        ┌──────▼──────┐
                        │  Output &   │
                        │   Storage   │
                        └─────────────┘
```

---

## Component Breakdown

### 1. User Interface Layer (Tkinter)

**Main Window**
```
ISLTranslator Class
├── Mode Selection Screen
│   ├── Sign-to-Text Button
│   └── Text-to-Sign Button
│
├── Sign-to-Text Interface
│   ├── Camera Feed Panel
│   ├── Detection Display
│   ├── Sentence Builder
│   ├── History Panel
│   └── Control Buttons
│
└── Text-to-Sign Interface
    ├── Text Input Field
    ├── Sign Display Canvas
    ├── Media Player
    └── Export Options
```

**GUI Features:**
- Responsive layout (1200x800)
- Real-time updates
- Visual feedback
- Status indicators

---

### 2. Sign-to-Text Pipeline

```
Camera Input → Frame Processing → Hand Detection → 
Feature Extraction → Pattern Matching → Word Recognition → 
Cooldown Check → Sentence Building → Display Output
```

**Step Details:**

#### A. Camera Input
```python
cv2.VideoCapture(0)
├── Resolution: Auto-detected
├── FPS: 30+
└── Format: BGR
```

#### B. MediaPipe Processing
```python
mp.solutions.hands.Hands()
├── max_num_hands: 2
├── min_detection_confidence: 0.7
├── min_tracking_confidence: 0.7
└── Output: 21 landmarks per hand
```

#### C. Feature Extraction
```python
Features Extracted:
├── Finger States (5 boolean)
│   ├── Thumb extended?
│   ├── Index extended?
│   ├── Middle extended?
│   ├── Ring extended?
│   └── Pinky extended?
│
├── Palm Direction
│   └── [up, down, left, right, forward]
│
├── Hand Orientation (degrees)
│   └── Rotation angle: -180° to 180°
│
├── Finger Angles (5 arrays)
│   └── Joint angles for each finger
│
└── Hand Position
    └── [high, middle, low]
```

#### D. Pattern Matching
```python
For each sign in database:
├── Check hand count match
├── Analyze finger configuration
├── Verify palm direction
├── Validate hand position
└── Return best match
```

---

### 3. Text-to-Sign Pipeline

```
Text Input → Word Tokenization → Sign Lookup → 
Media Loading → Canvas Rendering → Sequential Display
```

**Step Details:**

#### A. Text Processing
```python
Input: "HELLO THANK YOU"
└── Split: ["HELLO", "THANK_YOU"]
    └── Convert: Uppercase
        └── Validate: Check database
```

#### B. Media Resolution
```python
For each word:
├── Clean filename
├── Search sign_media/ folder
├── Check extensions
│   ├── Images: .png, .jpg, .jpeg, .gif
│   └── Videos: .mp4, .avi, .mov
└── Load or show placeholder
```

#### C. Display Rendering
```python
Canvas Layout:
├── Calculate grid (signs_per_row)
├── For each sign:
│   ├── Draw border box
│   ├── Load media file
│   ├── Resize to fit
│   ├── Display image/video
│   ├── Add word label
│   └── Add hand info
└── Update scroll region
```

---

## Data Flow Diagrams

### Sign-to-Text Data Flow

```
┌──────────┐
│  Camera  │
└────┬─────┘
     │ Raw Video Frame (BGR)
     ▼
┌──────────┐
│  Flip &  │
│ Convert  │ (Mirror + RGB)
└────┬─────┘
     │ RGB Frame
     ▼
┌──────────┐
│MediaPipe │
│   Hands  │
└────┬─────┘
     │ Hand Landmarks (x, y, z)
     ▼
┌──────────┐
│ Feature  │
│Extractor │
└────┬─────┘
     │ Feature Dict
     ▼
┌──────────┐
│ Pattern  │
│ Matcher  │
└────┬─────┘
     │ Detected Word
     ▼
┌──────────┐
│ Cooldown │
│  Check   │
└────┬─────┘
     │ (if pass)
     ▼
┌──────────┐
│ Sentence │
│ Builder  │
└────┬─────┘
     │ Updated Sentence
     ▼
┌──────────┐
│  Display │
└──────────┘
```

### Text-to-Sign Data Flow

```
┌──────────┐
│   User   │
│  Input   │
└────┬─────┘
     │ Text String
     ▼
┌──────────┐
│   Text   │
│ Process  │
└────┬─────┘
     │ Word Array
     ▼
┌──────────┐
│   Sign   │
│  Lookup  │
└────┬─────┘
     │ Sign Info + Media Path
     ▼
┌──────────┐
│  Media   │
│  Loader  │
└────┬─────┘
     │ Image/Video Data
     ▼
┌──────────┐
│  Canvas  │
│ Renderer │
└────┬─────┘
     │ Visual Display
     ▼
┌──────────┐
│  Screen  │
└──────────┘
```

---

## Key Algorithms

### 1. Finger Extension Detection

```python
Algorithm: Vertical Distance Check
─────────────────────────────────
Input: Hand landmarks
Output: Boolean array [5]

For each finger (except thumb):
    tip_y = landmark[tip_id].y
    pip_y = landmark[pip_id].y
    
    if tip_y < pip_y - threshold:
        finger_extended = True
    else:
        finger_extended = False

For thumb (special case):
    Check horizontal distance instead
```

### 2. Palm Direction Calculation

```python
Algorithm: Vector Direction
─────────────────────────────
Input: Wrist (0) and MCP (9) positions
Output: Direction string

direction_vector = MCP - Wrist

if direction_vector.y < -0.1:
    return "up"
elif direction_vector.y > 0.1:
    return "down"
elif direction_vector.x < -0.1:
    return "left"
elif direction_vector.x > 0.1:
    return "right"
else:
    return "forward"
```

### 3. Cooldown System

```python
Algorithm: Time-Based Throttle
─────────────────────────────
Input: Current time, last detection time
Output: Allow/Block

cooldown_duration = 1.5  # seconds

if (current_time - last_detection_time) >= cooldown_duration:
    allow_detection()
    update_last_detection_time()
else:
    block_detection()
    show_remaining_time()
```

---

## Technology Stack

### Core Technologies
```
┌─────────────────────────────┐
│  Python 3.8+                │
├─────────────────────────────┤
│  OpenCV (cv2)              │ ← Video processing
│  MediaPipe                 │ ← Google hand tracking
│  NumPy                     │ ← Numerical operations
│  Pandas                    │ ← Data management
│  Pillow (PIL)              │ ← Image processing
│  Tkinter                   │ ← GUI framework
│  openpyxl                  │ ← Excel reading
└─────────────────────────────┘
```

### Library Usage Map
```
OpenCV (cv2):
├── Camera capture
├── Frame processing
├── Video decoding
└── Image conversion

MediaPipe:
├── Hand landmark detection
├── Real-time tracking
├── Multi-hand support
└── Coordinate normalization

NumPy:
├── Vector operations
├── Angle calculations
└── Array manipulations

Tkinter:
├── Window management
├── Canvas rendering
├── Event handling
└── Layout control
```

---

## File System Structure

```
project_root/
│
├── isl_translator.py          # Main application (1500+ lines)
│   ├── ISLTranslator class
│   │   ├── __init__()
│   │   ├── GUI methods
│   │   ├── Camera methods
│   │   ├── Recognition methods
│   │   └── Display methods
│   └── main()
│
├── signs.xlsx                  # Sign database
│   └── [Word, Hand(s), Description]
│
├── sign_media/                 # Media resources
│   ├── HELLO.png
│   ├── THANK_YOU.mp4
│   └── ...
│
├── requirements.txt            # Python dependencies
├── setup.py                    # Setup automation
├── README.md                   # Documentation
├── ADDING_SIGNS_GUIDE.md      # Custom sign guide
│
└── [Generated at runtime]
    ├── ISL_Conversation_*.txt
    └── ISL_SignSequence_*.txt
```

---

## Performance Characteristics

### Speed Metrics
```
Component                    Target FPS/Time
─────────────────────────────────────────────
Camera Capture              30-60 FPS
MediaPipe Processing        30+ FPS
Feature Extraction          < 10ms per frame
Pattern Matching            < 5ms per check
GUI Update                  60 FPS
Overall Latency             < 100ms
```

### Resource Usage
```
Component                    Typical Usage
─────────────────────────────────────────────
CPU                         30-50%
RAM                         200-500 MB
GPU (if available)          10-20% (MediaPipe)
Disk I/O                    Minimal (media loading)
```

---

## Security & Privacy

### Data Handling
```
✅ All processing done locally
✅ No data sent to external servers
✅ Camera feed not recorded (unless user saves)
✅ Conversation history stored locally only
✅ User controls all save/export operations
```

### Permissions Required
```
Camera Access:
└── Required for Sign-to-Text mode
    └── Standard system permission
    └── Can be revoked anytime
```

---

## Extensibility Points

### Adding New Features
```
1. New Sign Types
   └── Edit: match_sign_pattern() method

2. Additional Languages
   └── Create: new Excel database
   └── Modify: sign_data loading

3. Enhanced UI
   └── Extend: create_*_interface() methods

4. Export Formats
   └── Add: new download_* methods

5. ML Models
   └── Replace: pattern matching with ML
```

---

## Error Handling Strategy

```
Layer                    Error Handling
─────────────────────────────────────────────
Camera Access           Try-catch + user message
MediaPipe Init          Fallback + error dialog
File Loading            Placeholder display
Pattern Matching        Return None + continue
GUI Updates             Safe state management
User Actions            Validation + feedback
```

---

This architecture enables:
✅ **Real-time performance**
✅ **Accurate recognition**
✅ **User-friendly interface**
✅ **Easy extensibility**
✅ **Robust error handling**
✅ **Privacy preservation**

**Built with ❤️ for accessibility**
