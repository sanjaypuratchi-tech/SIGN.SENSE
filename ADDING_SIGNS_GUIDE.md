# Adding Custom Signs to ISL Translator

This guide explains how to add new signs to the Indian Sign Language Translator system.

## Quick Steps

1. **Add to Excel file** (`signs.xlsx`)
2. **Add media file** (to `sign_media/` folder)
3. **Implement recognition logic** (for Sign-to-Text mode)

---

## Step 1: Update Excel File

Open `signs.xlsx` and add a new row with:

| Column | Description | Example |
|--------|-------------|---------|
| **Word** | The sign name | `SORRY` |
| **Hand(s)** | Single or Both | `Single` |
| **Description** | How to perform the sign | `Place your closed fist on your chest and move it in a circular motion` |

**Tips:**
- Use UPPERCASE for word names (consistency)
- For multi-word signs, use underscores: `GOOD_MORNING`
- Be detailed in descriptions for recognition logic

---

## Step 2: Add Media File

Create an image or video showing the sign:

### File Naming
```
sign_media/WORD.extension
```

**Examples:**
- `sign_media/SORRY.png`
- `sign_media/GOOD_MORNING.mp4`
- `sign_media/YES.jpg`

### Media Guidelines

**For Images:**
- Format: PNG (for transparency) or JPG
- Resolution: 800x600 minimum
- Clear hand visibility
- Plain or contrasting background
- Show final position of the sign

**For Videos:**
- Format: MP4 (most compatible)
- Duration: 2-5 seconds
- Show complete sign motion
- Good lighting
- 30 fps minimum
- HD quality (1280x720 or higher)

---

## Step 3: Implement Recognition Logic (Optional)

For Sign-to-Text mode to recognize your new sign, add pattern matching logic.

### Location in Code

Edit `isl_translator.py`, find the `match_sign_pattern()` method (around line 583).

### Template

```python
# YOUR_SIGN Pattern: Brief description
if word == "YOUR_SIGN":
    # Define your recognition logic
    # Example checks:
    
    # Check specific fingers extended
    # finger_states = [Thumb, Index, Middle, Ring, Pinky]
    if finger_states[1] and finger_states[2]:  # Index and middle extended
        
        # Check palm direction
        if palm_dir == "forward":
            
            # Check hand position
            if hand['hand_position'] == "high":
                return True
    
    return False
```

### Available Features

You can use these features for pattern matching:

```python
finger_states      # [Thumb, Index, Middle, Ring, Pinky] - True/False for extended
palm_dir          # "up", "down", "left", "right", "forward"
hand['hand_position']     # "high", "middle", "low"
hand['hand_orientation']  # Rotation angle in degrees
hand['finger_angles']     # List of angles at each finger joint
features['num_hands']     # 1 or 2
```

### Example Patterns

#### Simple Pattern: Thumbs Up
```python
if word == "GOOD":
    # Only thumb extended, pointing up
    thumb_up = finger_states[0] and not any(finger_states[1:])
    if thumb_up and palm_dir == "forward":
        return True
```

#### Complex Pattern: Peace Sign
```python
if word == "PEACE":
    # Index and middle extended, others closed
    v_shape = (finger_states[1] and finger_states[2] and 
               not finger_states[3] and not finger_states[4])
    
    # Palm facing outward
    if v_shape and palm_dir == "forward":
        return True
```

#### Two-Hand Pattern
```python
if word == "APPLAUSE":
    # Requires both hands
    if features['num_hands'] == 2:
        # Both palms facing each other
        hands_facing = all(h['palm_direction'] == "forward" for h in features['hands'])
        if hands_facing:
            return True
```

---

## Testing Your New Sign

### For Text-to-Sign Mode:
1. Run the program
2. Select "Text-to-Sign"
3. Type your word
4. Verify the media file displays correctly

### For Sign-to-Text Mode:
1. Run the program
2. Select "Sign-to-Text"
3. Start camera
4. Perform the sign
5. Check if it's detected correctly

### Debugging Tips:

**If media doesn't show:**
- Check filename matches Excel entry exactly
- Verify file is in `sign_media/` folder
- Check file extension is supported
- Try renaming with underscores for multi-word signs

**If sign isn't recognized:**
- Print debug info in `match_sign_pattern()`:
  ```python
  print(f"Checking {word}: fingers={finger_states}, palm={palm_dir}")
  ```
- Adjust confidence thresholds
- Make pattern matching less strict
- Ensure Excel entry exists

---

## Advanced: Creating Complex Signs

### Multi-Step Signs

For signs requiring motion or multiple positions:

```python
# Track sign progression
if not hasattr(self, 'sign_state'):
    self.sign_state = {}

if word == "TOMORROW":
    # Step 1: Closed fist
    if all(not f for f in finger_states[1:]):
        self.sign_state['tomorrow_step'] = 1
    
    # Step 2: Open hand after fist
    elif self.sign_state.get('tomorrow_step') == 1:
        if all(finger_states[1:]):
            self.sign_state['tomorrow_step'] = 0
            return True
```

### Direction-Based Signs

```python
if word == "GO":
    # Check if hand is moving (compare current vs previous position)
    current_pos = hand['hand_position']
    
    if hasattr(self, 'prev_hand_pos'):
        # Detect forward motion
        if current_pos != self.prev_hand_pos:
            return True
    
    self.prev_hand_pos = current_pos
```

---

## Best Practices

1. **Start Simple**: Begin with basic finger patterns
2. **Test Thoroughly**: Perform sign multiple times
3. **Adjust Sensitivity**: Fine-tune detection thresholds
4. **Document Well**: Write clear descriptions
5. **Use Quality Media**: Clear, well-lit images/videos
6. **Be Consistent**: Follow naming conventions
7. **Consider Variations**: Account for different hand sizes/speeds

---

## Common Issues

| Problem | Solution |
|---------|----------|
| Media not loading | Check filename matches exactly (case-sensitive) |
| Sign always detected | Pattern too broad - add more conditions |
| Sign never detected | Pattern too strict - loosen conditions |
| Wrong sign detected | Add distinctive features to pattern |
| Slow detection | Optimize pattern matching code |

---

## Example: Complete New Sign Addition

Let's add "SORRY" sign:

### 1. Excel Entry
```
Word: SORRY
Hand(s): Single
Description: Place closed fist on chest, move in small circle
```

### 2. Media File
Create `sign_media/SORRY.mp4` showing the circular motion

### 3. Recognition Code
```python
if word == "SORRY":
    # Closed fist (no fingers extended)
    is_fist = not any(finger_states[1:])
    
    # Hand near chest (middle to low position)
    chest_level = hand['hand_position'] in ['middle', 'low']
    
    # Palm facing inward
    palm_in = palm_dir == "forward"
    
    if is_fist and chest_level and palm_in:
        return True
```

---

## Resources

- **MediaPipe Documentation**: https://google.github.io/mediapipe/solutions/hands
- **Hand Landmark Reference**: 21 landmarks per hand
- **ISL Standards**: Consult official ISL dictionaries

---

## Support

If you encounter issues:
1. Check this guide
2. Verify all steps completed
3. Test with similar existing signs
4. Adjust pattern matching logic
5. Consider lighting and camera quality

---

**Happy Signing! 🤟**
