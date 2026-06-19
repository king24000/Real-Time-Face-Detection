import cv2

# Camera Settings
CAMERA_INDEX = 0          # Default built-in camera
FRAME_WIDTH = 1280        # Desired stream width
FRAME_HEIGHT = 720        # Desired stream height

# Face Detection Settings
MIN_DETECTION_CONFIDENCE = 0.55  # MediaPipe face detection confidence threshold

# Color Theme (BGR Format)
COLOR_PRIMARY = (255, 223, 0)       # Cyan
COLOR_SECONDARY = (200, 0, 255)     # Magenta/Pink
COLOR_TEXT = (255, 255, 255)        # White
COLOR_HUD_BG = (20, 20, 20)         # Very dark gray (for overlay background panels)
COLOR_SUCCESS = (0, 255, 0)         # Green (for status indicators)
COLOR_GLOW = (255, 180, 100)        # Electric blue (for detection highlights)

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

# Directory Settings
SCREENSHOTS_DIR = "screenshots"
