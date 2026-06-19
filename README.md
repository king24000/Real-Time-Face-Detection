# ⚡ Real-Time Face Detection HUD System

A high-performance, real-time face detection desktop application written in **Python**, utilizing **Google MediaPipe Face Detection** and **OpenCV**.

Instead of standard, basic OpenCV bounding boxes, this application draws a custom, futuristic cybernetic **Heads-Up Display (HUD)** over the camera feed, rendering smoothed tracking stats, estimated face distance, and dynamic notification alerts.

---

## ✨ Features

- **Full-Range Detection (Up to 5m)**: Utilizes MediaPipe's deep-learning model which operates seamlessly in real-time, detecting faces at varying angles, distances, and lighting conditions up to 5 meters (16 feet) away.
- **Real-Time Distance Estimation**: Estimates how far you are from the camera in centimeters (`cm`) or meters (`m`) dynamically using the pixel size of your face and webcam focal similarities.
- **Dynamic Multi-Theme Cycling**: Cycle between 4 cybernetic/neon UI themes instantly:
  - 🩵 **Cyberpunk Cyan** (Neon Cyan, Pink, and Electric Blue)
  - 💚 **Matrix Neon** (Terminal Green and Dark Green accents)
  - ❤️ **Stealth Red** (Alert Red and Deep Crimson shades)
  - 💛 **Sunset Gold** (Amber Orange and Golden Yellow)
- **Landmark Mapping**: Locates and renders core facial landmarks (eyes, nose, mouth, ears) with glowing crosshair tracking.
- **Clean Screenshots**: Captures screenshots of the *raw* clean camera stream (without overlays) when pressing `S` and stores them in a timestamped screenshots directory.
- **Modular Codebase**: Well-structured, configurable, and commented code.

---

## 📁 Project Architecture

The workspace is organized cleanly as follows:

```
Real-Time Face Detection/
├── models/
│   └── blaze_face_full_range.tflite   # Automatic downloaded Face Detection Model
│
├── src/
│   ├── __init__.py       # Package definition
│   ├── config.py         # App configurations (dimensions, themes, thresholds, calibration)
│   ├── detector.py       # Wrapper interface around MediaPipe Face Detection Tasks API
│   ├── hud.py            # HUD overlays and cyber-themed drawing calculations
│   ├── utils.py          # FPS, alerts, screenshot writer, and distance estimators
│   └── main.py           # Core execution thread and video loop
│
├── requirements.txt      # Dependency list
├── run.py                # Main script launcher
└── README.md             # This guide
```

---

## 🚀 Installation & Usage

### 1. Prerequisites
Ensure you have **Python 3.8 to 3.14** installed on your system. 

### 2. Setup Virtual Environment (Recommended)
Open your terminal (PowerShell, Command Prompt, or Bash) in the project root directory and run:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Windows (CMD):
.\venv\Scripts\activate.bat
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
Install all required libraries using `pip`:

```bash
pip install -r requirements.txt
```

### 4. Run the Application
Start the real-time application directly from the root launcher:

```bash
python run.py
```
*(On the very first launch, it will take a couple of seconds to automatically download the `blaze_face_full_range.tflite` model (2.4MB) into your workspace).*

---

## ⌨️ Control Guides & Hotkeys

All interactive commands can be triggered via keyboard while the feed window is active:

| Key | Action | Description |
| :---: | :--- | :--- |
| **`Q`** | **Exit App** | Closes camera stream, shuts down detectors, and exits cleanly. |
| **`S`** | **Take Snapshot** | Captures a raw, high-res frame (no HUD overlays) and saves to `screenshots/` directory. |
| **`H`** | **Toggle HUD** | Shows or hides the header/footer control dashboards. |
| **`B`** | **Toggle Bounding Boxes**| Hides/shows bounding boxes, landmarks, and distance labels. |
| **`C`** | **Cycle UI Themes** | Instantly switches the entire HUD colors (Cyberpunk, Matrix, Stealth, Sunset). |

---

## 🎨 Styling Customization

You can customize the camera parameters and themes by editing [src/config.py](file:///c:/Users/45kin/OneDrive/Desktop/project/Computer%20vision/Real-Time%20Face%20Detection/src/config.py):
- **Distance Calibration**: If the distance is slightly off on your webcam, modify `FOCAL_LENGTH` (increase to increase distance value, decrease to decrease).
- **Themes**: Modify, rename, or add new themes to the `THEMES` list.
- **Thresholds**: Adjust `MIN_DETECTION_CONFIDENCE` to make the detector more or less sensitive.
