import cv2

# Camera Settings
CAMERA_INDEX = 0          # Default built-in camera
FRAME_WIDTH = 1280        # Desired stream width
FRAME_HEIGHT = 720        # Desired stream height

# Face Detection Settings
MIN_DETECTION_CONFIDENCE = 0.55  # MediaPipe face detection confidence threshold

# Distance Estimation Configuration
KNOWN_FACE_WIDTH = 14.5     # Average human face width in centimeters (ear-to-ear/cheekbone)
FOCAL_LENGTH = 950.0        # Calibrated focal length constant for 720p webcams

# Color Themes List (BGR Format)
THEMES = [
    {
        "name": "CYBERPUNK CYAN",
        "primary": (255, 223, 0),       # Neon Cyan
        "secondary": (200, 0, 255),     # Neon Pink/Magenta
        "glow": (255, 180, 100),        # Electric Blue
    },
    {
        "name": "MATRIX NEON",
        "primary": (0, 255, 0),         # Matrix Green
        "secondary": (0, 140, 0),       # Dark Green
        "glow": (100, 255, 100),        # Light Green
    },
    {
        "name": "STEALTH RED",
        "primary": (0, 0, 255),         # Alert Red
        "secondary": (100, 100, 255),   # Coral Red
        "glow": (50, 50, 255),          # Deep Red
    },
    {
        "name": "SUNSET GOLD",
        "primary": (0, 165, 255),       # Amber Gold / Orange
        "secondary": (0, 90, 255),       # Dark Gold / Reddish Orange
        "glow": (150, 220, 255),        # Sun Yellow
    }
]

# Static Colors (Common to all themes)
COLOR_TEXT = (255, 255, 255)        # White
COLOR_HUD_BG = (15, 15, 15)         # Translucent black/dark gray for dashboard
COLOR_SUCCESS = (0, 255, 0)         # Green status dot

# UI Font Configuration
FONT_FACE = cv2.FONT_HERSHEY_DUPLEX
FONT_SCALE_HUD = 0.55
FONT_SCALE_BOX = 0.5
FONT_SCALE_ALERT = 0.6
THICKNESS_HUD = 1
THICKNESS_BOX = 2

# HUD Box Styling
BOX_CORNER_LENGTH = 25              # Length of the bounding box corner ticks in pixels
BOX_CORNER_THICKNESS = 4            # Thickness of the corner ticks
BOX_RECTANGLE_THICKNESS = 1         # Thickness of the base border line

# Control Keys (Case-insensitive)
KEY_QUIT = 'q'
KEY_SCREENSHOT = 's'
KEY_TOGGLE_HUD = 'h'
KEY_TOGGLE_BOX = 'b'
KEY_CYCLE_THEME = 'c'               # Theme changing hotkey

# Directory Settings
SCREENSHOTS_DIR = "screenshots"
