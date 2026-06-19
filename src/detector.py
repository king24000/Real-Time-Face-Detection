import cv2
import mediapipe as mp
from src.config import MIN_DETECTION_CONFIDENCE

class FaceDetector:
    """
    A class to encapsulate MediaPipe's Face Detection functionality, 
    offering simple inputs and outputs.
    """
    def __init__(self, confidence_threshold=MIN_DETECTION_CONFIDENCE):
        self.mp_face_detection = mp.solutions.face_detection
        self._detector = self.mp_face_detection.FaceDetection(
            min_detection_confidence=confidence_threshold,
            model_selection=0  # 0 for short-range faces (within 2 meters), 1 for full-range (within 5 meters)
        )

    def detect_faces(self, frame):
        """
        Processes a frame and returns details of all detected faces.
        
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
        # MediaPipe expects RGB images, OpenCV captures in BGR
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._detector.process(rgb_frame)

        faces = []
        if results.detections:
            for detection in results.detections:
                # Extract relative bounding box
                bbox_rel = detection.location_data.relative_bounding_box
                
                # Convert relative to pixel coordinates
                x = int(bbox_rel.xmin * w)
                y = int(bbox_rel.ymin * h)
                width = int(bbox_rel.width * w)
                height = int(bbox_rel.height * h)

                # Boundary safety checks
                x = max(0, x)
                y = max(0, y)
                width = min(width, w - x)
                height = min(height, h - y)

                confidence = detection.score[0] if detection.score else 0.0

                # Extract relative keypoints/landmarks
                landmarks = []
                if detection.location_data.relative_keypoints:
                    for kp in detection.location_data.relative_keypoints:
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
        self._detector.close()
