# 🚀 Air Canvas Pro - Quick Start Guide

## ⚡ Fast Setup (3 Steps)

### Step 1: Run Setup Script
```bash
python setup.py
```
This will:
- ✅ Check Python version
- ✅ Install missing dependencies
- ✅ Download model file
- ✅ Test camera access

### Step 2: Run Air Canvas
```bash
python main.py
```

### Step 3: Start Drawing!
- ✌️ Point with index finger to draw
- ✋ Open palm to clear canvas
- 🤏 Pinch to erase

---

## 🔧 Manual Setup (If Automated Fails)

### 1. Install Dependencies
```bash
pip install opencv-python mediapipe numpy
```

### 2. Download Model File

**Option A: Use Download Script**
```bash
python download_model.py
```

**Option B: Manual Download**
1. Visit: https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
2. Save as `hand_landmarker.task` in the project folder

### 3. Verify Setup
```bash
python -c "import cv2, mediapipe, numpy; print('✅ All dependencies OK')"
```

---

## 🎮 Controls

### 👆 Hand Gestures

| Gesture | Action |
|---------|--------|
| ✌️ Index finger up | Draw / Click buttons |
| 🤏 Thumb + Index pinch | Eraser mode |
| ✋ All 5 fingers up | Clear canvas |
| 🖖 Index + Middle + Ring | Next color |
| 🤘 Thumb + Pinky | Undo |

### ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `ESC` | Exit |
| `D` | Toggle debug mode |
| `S` | Toggle statistics |
| `I` | Toggle instructions |
| `H` | Show help |
| `R` | Reset stats |

---

## ⚠️ Troubleshooting

### Model File Missing
```
❌ Error: Unable to open file at hand_landmarker.task
```
**Solution:**
```bash
python download_model.py
```

### Camera Not Working
```
❌ Error: Could not open camera
```
**Solutions:**
1. Close other apps using camera (Zoom, Teams, etc.)
2. Check camera permissions
3. Try: `cap = cv2.VideoCapture(1)` (different camera)

### Import Errors
```
ModuleNotFoundError: No module named 'mediapipe'
```
**Solution:**
```bash
pip install opencv-python mediapipe numpy
```

### Hand Not Detected
**Solutions:**
1. Improve lighting (bright, even light)
2. Use plain background
3. Keep hand 30-60cm from camera
4. Face palm toward camera

### Slow Performance
**Solutions:**
1. Lower resolution in `main.py`:
   ```python
   WIDTH, HEIGHT = 640, 480
   ```
2. Use performance mode (already default)
3. Close other applications

---

## 💡 Tips for Best Experience

### 🌟 Optimal Conditions
- **Lighting**: Bright room or desk lamp
- **Background**: Plain wall or solid color
- **Distance**: 40-50cm from camera
- **Hand**: Palm facing camera, fingers clear

###  Drawing Tips
- Make deliberate, smooth movements
- Hold gestures for 1-2 seconds
- Keep fingers clearly separated
- Practice gestures before drawing

###  Performance Tips
- Close unnecessary apps
- Use wired connection if on laptop
- Ensure good lighting (helps tracking)
- Start with small drawings first

---

## System Requirements

### Minimum
- Python 3.7+
- 2GB RAM
- Webcam
- Windows/macOS/Linux

### Recommended
- Python 3.8+
- 4GB+ RAM
- HD Webcam (720p+)
- Good lighting

---

##First Time Using?

### 1. Run Setup
```bash
python setup.py
```

### 2. Start Application
```bash
python main.py
```

### 3. Test Gestures
- Press `I` to show instructions
- Press `D` to see hand tracking
- Try each gesture slowly

### 4. Practice Drawing
- Start with simple shapes
- Experiment with colors (3-finger gesture)
- Try different brush sizes (thumb-index distance)

---

## Still Need Help?

### Check These Files:
- `TROUBLESHOOTING.md` - Detailed problem solving
- `README.md` - Full documentation
- Console output - Error messages

### Quick Diagnostic:
```bash
# Check installation
python -c "import cv2; print(f'OpenCV: {cv2.__version__}')"
python -c "import mediapipe; print(f'MediaPipe: {mediapipe.__version__}')"

# Test camera
python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera Failed')"

# Check model
python -c "from pathlib import Path; print('Model OK' if Path('hand_landmarker.task').exists() else 'Model Missing')"
```

---

## Ready to Draw!

Once setup is complete:
```bash
python main.py
```

Have fun creating! 

---

**Need more help?** Check `TROUBLESHOOTING.md` for detailed solutions.