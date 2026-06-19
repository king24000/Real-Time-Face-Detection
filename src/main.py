import cv2
import sys
from src.config import (
    CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT, KEY_QUIT, KEY_SCREENSHOT,
    KEY_TOGGLE_HUD, KEY_TOGGLE_BOX
)
from src.detector import FaceDetector
from src.utils import FPSTracker, AlertSystem, save_screenshot
from src.hud import draw_hud_box, draw_hud_landmarks, draw_hud_interface

def main():
    print("==================================================")
    print("     Real-Time Face Detection HUD Launcher        ")
    print("==================================================")
    print("Initializing camera feed and detector models...")

    # Initialize video capture
    cap = cv2.VideoCapture(CAMERA_INDEX)
    
    # Configure camera resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not cap.isOpened():
        print(f"\n[ERROR] Could not access camera with index {CAMERA_INDEX}.")
        print("Please check the following troubleshooting steps:")
        print("1. Ensure your webcam is plugged in and turned on.")
        print("2. Close any other application currently using the camera.")
        print("3. Check 'src/config.py' and try modifying 'CAMERA_INDEX' if you have multiple cameras.")
        sys.exit(1)

    # Print settings status
    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Camera opened successfully. Resolution: {actual_w}x{actual_h}")
    print(f"Press '{KEY_QUIT.upper()}' to exit the application.")
    print(f"Press '{KEY_SCREENSHOT.upper()}' to save a screenshot of the raw camera feed.")
    print(f"Press '{KEY_TOGGLE_HUD.upper()}' to show/hide the dashboard HUD panels.")
    print(f"Press '{KEY_TOGGLE_BOX.upper()}' to show/hide the face bounding boxes.")
    print("--------------------------------------------------")

    # Instantiate modules
    detector = FaceDetector()
    fps_tracker = FPSTracker()
    alert_system = AlertSystem()

    # App display state flags
    show_hud = True
    show_boxes = True

    # Windows creation
    window_name = "Real-Time Face Detection (Antigravity HUD)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, actual_w, actual_h)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[ERROR] Failed to read frame from camera feed.")
                break

            # Mirror the frame horizontally for a more natural webcam user experience
            frame = cv2.flip(frame, 1)

            # Make a clean copy of the frame before drawing overlays for clean screenshot capture
            clean_frame = frame.copy()

            # Perform detection
            faces = []
            if show_boxes:
                faces = detector.detect_faces(frame)
                
                # Draw bounding boxes & landmarks on frame
                for i, face in enumerate(faces, start=1):
                    x, y, w, h = face["bbox"]
                    confidence = face["confidence"]
                    landmarks = face["landmarks"]

                    # Draw Custom Corners bounding box
                    draw_hud_box(frame, x, y, w, h, confidence, i)
                    
                    # Draw Facial Landmarks (eyes, nose, mouth tip, ears)
                    draw_hud_landmarks(frame, landmarks)

            # Update FPS calculation
            fps_val = fps_tracker.update()

            # Fetch active screen notification
            current_alert = alert_system.active_message()

            # Render overall HUD dashboard structure
            draw_hud_interface(
                frame, 
                faces_count=len(faces), 
                fps=fps_tracker.get_fps(), 
                alert_msg=current_alert, 
                show_hud=show_hud, 
                show_boxes=show_boxes
            )

            # Render window frame
            cv2.imshow(window_name, frame)

            # Input key event handling (wait 1ms)
            key = cv2.waitKey(1) & 0xFF
            
            # Quit application
            if key == ord(KEY_QUIT.lower()) or key == ord(KEY_QUIT.upper()):
                print("\nShutdown request received. Closing...")
                break
                
            # Screenshot / Snapshot save
            elif key == ord(KEY_SCREENSHOT.lower()) or key == ord(KEY_SCREENSHOT.upper()):
                saved_path = save_screenshot(clean_frame)
                if saved_path:
                    filename = saved_path.split("\\")[-1]
                    print(f"[HUD] Screenshot saved to: {saved_path}")
                    alert_system.trigger(f"SNAPSHOT SAVED: {filename}")
                else:
                    alert_system.trigger("SCREENSHOT ERROR!")
                    
            # Toggle Dashboard HUD Panels
            elif key == ord(KEY_TOGGLE_HUD.lower()) or key == ord(KEY_TOGGLE_HUD.upper()):
                show_hud = not show_hud
                status_str = "ENABLED" if show_hud else "DISABLED"
                alert_system.trigger(f"HUD PANELS {status_str}", duration=1.5)
                
            # Toggle detections bounding boxes
            elif key == ord(KEY_TOGGLE_BOX.lower()) or key == ord(KEY_TOGGLE_BOX.upper()):
                show_boxes = not show_boxes
                status_str = "VISIBLE" if show_boxes else "HIDDEN"
                alert_system.trigger(f"DETECTIONS {status_str}", duration=1.5)

            # Check if OpenCV window was closed via close 'X' button
            if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                print("\nWindow closed manually. Closing...")
                break

    except Exception as e:
        print(f"\n[CRITICAL ERROR] Exception during runtime execution: {e}")
    finally:
        # Resource cleanup
        cap.release()
        detector.close()
        cv2.destroyAllWindows()
        print("Application terminated cleanly.")

if __name__ == "__main__":
    main()
