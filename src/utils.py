import os
import cv2
import time
from datetime import datetime
from src.config import SCREENSHOTS_DIR

class FPSTracker:
    """
    Tracks and filters the frames per second (FPS) calculation for smooth visual display.
    """
    def __init__(self):
        self.prev_time = time.time()
        self.fps = 0.0

    def update(self):
        """
        Updates the frame rate based on the current time tick.
        """
        curr_time = time.time()
        diff = curr_time - self.prev_time
        self.prev_time = curr_time

        if diff > 0:
            instant_fps = 1.0 / diff
            # Low pass filter: 90% history, 10% instant change to smooth fluctuations
            self.fps = (self.fps * 0.9) + (instant_fps * 0.1)
        return self.fps

    def get_fps(self):
        return int(round(self.fps))


class AlertSystem:
    """
    Handles on-screen notifications that auto-expire after a duration.
    """
    def __init__(self):
        self._message = ""
        self._expire_at = 0.0

    def trigger(self, message, duration=2.5):
        """
        Activate a message for the specified duration (seconds).
        """
        self._message = message
        self._expire_at = time.time() + duration

    def active_message(self):
        """
        Returns the message if still valid, otherwise None.
        """
        if time.time() < self._expire_at:
            return self._message
        return None


def save_screenshot(frame):
    """
    Saves the given frame as a timestamped PNG in the screenshots folder.
    
    Args:
        frame: OpenCV image matrix.
        
    Returns:
        str: Absolute path of the saved screenshot, or None if failed.
    """
    try:
        if not os.path.exists(SCREENSHOTS_DIR):
            os.makedirs(SCREENSHOTS_DIR)

        # Unique timestamp file name
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S_%f")[:-3]
        filename = f"capture_{timestamp}.png"
        filepath = os.path.join(SCREENSHOTS_DIR, filename)

        # Write file
        success = cv2.imwrite(filepath, frame)
        if success:
            return os.path.abspath(filepath)
    except Exception as e:
        print(f"Error saving screenshot: {e}")
    
    return None


def calculate_distance(face_pixel_width):
    """
    Estimates the distance of a face from the camera in centimeters
    using the triangle similarity formula.
    
    Formula: Distance = (Known Width * Focal Length) / Pixel Width
    """
    from src.config import KNOWN_FACE_WIDTH, FOCAL_LENGTH
    if face_pixel_width <= 0:
        return 0.0
    return (KNOWN_FACE_WIDTH * FOCAL_LENGTH) / face_pixel_width

