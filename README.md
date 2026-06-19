# ⚡ Real-Time Face Detection HUD System

A high-performance, real-time face detection desktop application written in **Python**, utilizing **Google MediaPipe Face Detection** and **OpenCV**.

Instead of standard, basic OpenCV bounding boxes, this application draws a custom, futuristic cybernetic **Heads-Up Display (HUD)** over the camera feed, rendering smoothed tracking stats and dynamic notification alerts.

---

## ✨ Features

- **High Fidelity Detection**: Utilizes MediaPipe's deep-learning model which operates seamlessly in real-time, detecting faces at varying angles, distances, and lighting conditions.
- **Cyberpunk HUD Overlay**: Renders a custom UI complete with a semi-transparent stats panel, a blinking live-feed indicator, frame counters, and live FPS logging.
- **Corner-Accented Bounding Boxes**: Draws sleek, sci-fi-themed corner tick lines and floating confidence tags (percentage match) next to faces.
- **Landmark Mapping**: Locates and renders core facial landmarks (eyes, nose, mouth, ears) with glowing crosshair tracking.
- **Clean Screenshots**: Captures screenshots of the *raw* clean camera stream (without overlays) when pressing `S` and stores them in a timestamped screenshots directory.
- **Modular Codebase**: Well-structured, configurable, and commented code.

---

## 📁 Project Architecture

The workspace is organized cleanly as follows:

```
Real-Time Face Detection/
├── src/
│   ├── __init__.py       # Package definition
│   ├── config.py         # App configurations (dimensions, colors, thresholds, key bindings)
│   ├── detector.py       # Wrapper interface around MediaPipe Face Detection
│   ├── hud.py            # HUD overlays and cyber-themed drawing calculations
│   ├── utils.py          # FPS calculator, alert trigger system, and screenshot file writers
│   └── main.py           # Core execution thread and video loop
│
├── requirements.txt      # Dependency list
├── run.py                # Main script launcher
└── README.md             # This guide
```

---

## 🚀 Installation & Usage

### 1. Prerequisites
Ensure you have **Python 3.8 to 3.11** installed on your system. 
*(Note: MediaPipe supports major python releases on Windows out of the box).*

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

---

## ⌨️ Control Guides & Hotkeys

All interactive commands can be triggered via keyboard while the feed window is active:

| Key | Action | Description |
| :---: | :--- | :--- |
| **`Q`** | **Exit App** | Closes camera stream, shuts down detectors, and exits cleanly. |
| **`S`** | **Take Snapshot** | Captures a raw, high-res frame (no HUD overlays) and saves to `screenshots/` directory. |
| **`H`** | **Toggle HUD** | Shows or hides the header/footer control dashboards. |
| **`B`** | **Toggle Bounding Boxes**| Hides/shows bounding boxes, labels, and landmarks tracking. |

---

## 🎨 Styling Customization

You can fully customize the look and feel by editing [src/config.py](file:///c:/Users/45kin/OneDrive/Desktop/project/Computer%20vision/Real-Time%20Face%20Detection/src/config.py):
- **Colors**: Change bounding boxes, glows, panels, and text colors (in `BGR` format).
- **HUD Layout**: Modify corner tick lengths (`BOX_CORNER_LENGTH`), line thickness, and fonts.
- **Thresholds**: Adjust `MIN_DETECTION_CONFIDENCE` to make the detector more or less sensitive.
- **Resolution**: Modify `FRAME_WIDTH` and `FRAME_HEIGHT` depending on your camera capabilities.
