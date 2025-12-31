
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" />
  <img src="https://img.shields.io/badge/OpenCV-Computer%20Vision-green.svg" />
  <img src="https://img.shields.io/badge/MediaPipe-Hand%20Tracking-orange.svg" />
  <img src="https://img.shields.io/badge/Realtime-30%20FPS-success.svg" />
  <img src="https://img.shields.io/github/stars/thomakepratik58/air-canvas?style=social" />
</p>

# 🎨 Air Canvas Pro

Air Canvas Pro is a real-time gesture-controlled drawing application that enables users
to draw, erase, and interact with a digital canvas using natural hand movements captured
through a standard webcam. The project demonstrates touchless human–computer interaction
using computer vision and real-time gesture recognition.

---

## Overview

Traditional drawing applications rely on physical input devices such as a mouse or stylus.
Air Canvas Pro removes this dependency by allowing users to control a canvas entirely
through hand gestures.

The system captures live video input, detects hand landmarks using MediaPipe, interprets
gestures through geometric analysis, and renders smooth drawing strokes on a virtual
canvas in real time. The project emphasizes performance, stability, and modular software
design.

---

## Demo

<p align="center">
  <img src="assets/demo.gif" width="800" alt="Air Canvas Pro demo"/>
</p>

---
---
## Screenshots

<p align="center">
  <img src="assets/demo - frame at 1m22s.jpg" width="45%" />
  <img src="assets/clideo_editor_ffc1b6550d374f5cb00b5d0a448d136c - frame at 0m18s.jpg" width="45%" />
</p>

---
## System Architecture

The application follows a real-time processing pipeline with clearly separated modules:

### Hand Tracking
- MediaPipe Hand Landmarker for real-time landmark detection  
- Single-hand tracking optimized for performance  
- Exponential Moving Average (EMA) smoothing for stability  
- Detection confidence and frame consistency tracking  

### Gesture Recognition
- Finger-state detection using landmark geometry  
- Distance-based pinch detection  
- Gesture cooldown and debounce logic  
- Support for compound gestures (undo, clear, color change)  

### Canvas Engine
- Weighted stroke smoothing for natural drawing  
- Dynamic brush size based on finger distance  
- Anti-aliased rendering using OpenCV  
- Memory-efficient undo stack  

### User Interface
- OpenCV-rendered interactive buttons  
- Real-time cursor and tool feedback  
- FPS and performance monitoring overlays  

---

## Features

- Gesture-based drawing and erasing  
- Dynamic brush size control  
- Multi-color selection via gestures  
- Undo and clear canvas actions  
- Smooth, jitter-free stroke rendering  
- Modular and extensible architecture  

---

## Performance

- Real-time execution at approximately **30 FPS**  
- Gesture-to-render latency under **50 ms**  
- Stable tracking under normal lighting conditions  
- Optimized for consumer-grade hardware  

---

## Tech Stack

- **Language:** Python  
- **Computer Vision:** OpenCV  
- **Hand Tracking:** MediaPipe  
- **Numerical Computing:** NumPy  
- **Architecture:** Modular real-time pipeline  

---

## Installation

### Prerequisites
- Python 3.8 or higher  
- Webcam  

### Setup
```bash
git clone https://github.com/thomakepratik58/air-canvas.git
cd air-canvas
python setup.py
````

### Run

```bash
python main.py
```

---

## Project Structure

```
air-canvas/
├── main.py                 # Application entry point
├── hand_tracking.py        # Hand landmark detection & stabilization
├── gesture_controller.py  # Gesture recognition logic
├── canvas.py               # Drawing engine and canvas state
├── setup.py                # Automated setup and dependency checks
├── requirements.txt        # Dependencies
├── hand_landmarker.task    # MediaPipe model
├── assets/
│   └── demo.gif
└── README.md
```

---

## Design Considerations

* **Stability vs Responsiveness:** EMA smoothing balances jitter reduction with responsiveness
* **Separation of Concerns:** Each module has a single responsibility
* **Performance Constraints:** Frame rate capped for consistent rendering
* **Extensibility:** New gestures and tools can be added with minimal changes

---

## Future Enhancements

* Multi-hand collaborative drawing
* Shape recognition and auto-completion
* Export canvas to SVG/PDF formats
* Web-based deployment using WebRTC
* AR/VR and smart-board integration

---

## Acknowledgements

* MediaPipe for real-time hand tracking
* OpenCV for computer vision utilities
* NumPy for efficient numerical computation

---

**Built with a focus on real-time performance, modular design, and touchless interaction.**

````


