import os
import urllib.request
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from src.config import MIN_DETECTION_CONFIDENCE

class FaceDetector:
    """
    A class to encapsulate MediaPipe's modern Face Detection Tasks API,
    handling model downloading, initialization, and face inference.
    """
    def __init__(self, confidence_threshold=MIN_DETECTION_CONFIDENCE):
        self.model_dir = "models"
        self.model_path = os.path.join(self.model_dir, "blaze_face_full_range.tflite")
        
        # Auto-download the model if not present
        self._ensure_model_exists()

        # Initialize detector options
        base_options = python.BaseOptions(model_asset_path=self.model_path)
        options = vision.FaceDetectorOptions(
            base_options=base_options,
            min_detection_confidence=confidence_threshold
        )
        self._detector = vision.FaceDetector.create_from_options(options)

    def _ensure_model_exists(self):
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)

        if not os.path.exists(self.model_path):
            print("\n[INFO] Face detection model not found. Downloading full-range model (~2.4MB)...")
            url = "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_full_range/float16/1/blaze_face_full_range.tflite"
            try:
                urllib.request.urlretrieve(url, self.model_path)
                print("[INFO] Model downloaded successfully.")
            except Exception as e:
                print(f"[ERROR] Failed to download model from {url}: {e}")
                raise RuntimeError("Could not download Face Detector model. Please verify your internet connection.")

    def detect_faces(self, frame):
        """
        Processes a frame and returns details of all detected faces using Tasks API.
        
        Args:
            frame: OpenCV BGR image frame.
            
        Returns:
            list: List of dictionaries containing:
                - 'bbox': (x, y, w, h) bounding box coordinates in pixels.
                - 'confidence': confidence score (float [0.0, 1.0]).
                - 'landmarks': list of (x, y) keypoints for nose, eyes, mouth, ears.
        """
        if frame is None:
            return []

        h, w, _ = frame.shape
        # Convert OpenCV BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Create MediaPipe Image object
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Run inference
        detection_result = self._detector.detect(mp_image)

        faces = []
        if detection_result.detections:
            for detection in detection_result.detections:
                # Extract bounding box (in pixels)
                bbox = detection.bounding_box
                x = bbox.origin_x
                y = bbox.origin_y
                width = bbox.width
                height = bbox.height

                # Boundary safety checks
                x = max(0, x)
                y = max(0, y)
                width = min(width, w - x)
                height = min(height, h - y)

                confidence = detection.categories[0].score if detection.categories else 0.0

                # Extract keypoints/landmarks
                landmarks = []
                if detection.keypoints:
                    for kp in detection.keypoints:
                        # Keypoints are normalized in the Tasks API, so multiply by dimensions
                        kp_x = int(kp.x * w)
                        kp_y = int(kp.y * h)
                        landmarks.append((kp_x, kp_y))

                faces.append({
                    "bbox": (x, y, width, height),
                    "confidence": confidence,
                    "landmarks": landmarks
                })

        return faces

    def close(self):
        """
        Release resources used by the detector.
        """
        if hasattr(self, "_detector"):
            self._detector.close()
