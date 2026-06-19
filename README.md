# ⚡ Real-Time Face Detection Web Dashboard

A high-performance, real-time face detection web application written in **Python**, utilizing **FastAPI**, **WebSockets**, **HTML5 Canvas**, and **Google MediaPipe Face Detection**.

Instead of standard, basic bounding boxes, this application runs a zero-latency WebSocket stream that draws a custom, futuristic cybernetic **Heads-Up Display (HUD)** directly in your browser. It renders smoothed tracking stats, estimated face distance, and dynamic neon glasses that map to facial landmarks.

---

## ✨ Features

- **Zero-Latency Web Stream**: Transmits camera frames to the backend via binary WebSocket packets. To eliminate lag, the browser displays the local video instantly and overlays detection boxes dynamically.
- **Full-Range Detection (Up to 5m)**: Utilizes MediaPipe's deep-learning model which operates seamlessly in real-time, detecting faces at varying angles, distances, and lighting conditions up to 5 meters (16 feet) away.
- **Real-Time Distance Estimation**: Estimates how far you are from the camera in centimeters (`cm`) or meters (`m`) dynamically using the pixel width of your face.
- **👓 Cybernetic Hexagon Glasses**: Generates responsive neon glasses that map to eye and ear coordinates, rotating and scaling to fit your movements.
- **🎨 Dynamic Multi-Theme Dashboard**: Switch between 4 glassmorphism-designed color themes on-the-fly:
  - 🩵 **Cyberpunk Cyan** (Neon Cyan, Pink, and Electric Blue)
  - 💚 **Matrix Neon** (Terminal Green and Dark Green accents)
  - ❤️ **Stealth Red** (Alert Red and Deep Crimson shades)
  - 💛 **Sunset Gold** (Amber Orange and Golden Yellow)
- **📸 Clean Snapshots**: Saves screenshots of the *raw* clean camera stream (without overlays) directly onto the backend `screenshots/` directory when clicking the capture button or pressing `S`.

---

## 📁 Project Architecture

The workspace is organized cleanly as follows:

```
Real-Time Face Detection/
├── models/
│   └── blaze_face_full_range.tflite   # Auto-downloaded Face Detection Model
│
├── static/               # Client-side Web Dashboard
│   ├── index.html        # Glassmorphic layout structure
│   ├── style.css         # Premium neon styling and themes
│   └── script.js         # Camera stream, WebSockets, & HTML5 Canvas drawings
│
├── src/
│   ├── __init__.py       # Package definition
│   ├── config.py         # Web port settings & distance calibrations
│   ├── detector.py       # Wrapper around MediaPipe Face Detection Tasks API
│   └── utils.py          # Distance calculation & screenshot writing utils
│
├── requirements.txt      # Web & AI library dependencies
├── run.py                # Web server launcher script
└── README.md             # This guide
```

---

## 🚀 Installation & Running

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
Start the Uvicorn web server:

```bash
python run.py
```
*(On the very first launch, it will take a couple of seconds to automatically download the `blaze_face_full_range.tflite` model (2.4MB) into your workspace).*

### 5. Open in Browser
Open your web browser and navigate to:
👉 **[http://localhost:8000](http://localhost:8000)**

---

## ⌨️ Control Guides & Hotkeys

All interactive commands can be triggered via keyboard while the dashboard page is focused:

| Key | Action | Description |
| :---: | :--- | :--- |
| **`Q`** | **Shutdown** | Closes camera streams, closes WebSockets, and attempts to close tab. |
| **`S`** | **Take Snapshot** | Captures a raw, high-res frame (no HUD overlays) and saves to backend `screenshots/` directory. |
| **`H`** | **Toggle HUD** | Shows or hides the header/footer control dashboards. |
| **`B`** | **Toggle Bounding Boxes**| Hides/shows bounding boxes, landmarks, and distance labels. |
| **`C`** | **Cycle UI Themes** | Instantly switches the entire HUD colors (Cyberpunk, Matrix, Stealth, Sunset). |
