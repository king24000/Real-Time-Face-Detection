import os
import cv2
import base64
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src.config import SCREENSHOTS_DIR
from src.detector import FaceDetector
from src.utils import calculate_distance, save_screenshot

app = FastAPI(title="Real-Time Face Detection Web HUD API")

# Initialize face detector model
detector = FaceDetector()

# Mount static folder for serving CSS, JS and index.html
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def get_index():
    """
    Renders the main dashboard webpage.
    """
    return FileResponse("static/index.html")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """
    Handles browser favicon requests with 204 No Content to avoid console 404 warnings.
    """
    return Response(status_code=204)

class ScreenshotRequest(BaseModel):
    image_base64: str

@app.post("/api/screenshot")
async def save_client_screenshot(req: ScreenshotRequest):
    """
    Saves a clean raw camera frame uploaded by the web client to the backend disk.
    """
    try:
        # Extract base64 image data
        if "," in req.image_base64:
            header, encoded = req.image_base64.split(",", 1)
        else:
            encoded = req.image_base64
            
        data = base64.b64decode(encoded)
        nparr = np.frombuffer(data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return {"success": False, "error": "Invalid image data"}

        saved_path = save_screenshot(frame)
        if saved_path:
            filename = os.path.basename(saved_path)
            print(f"[WEB API] Screenshot saved to: {saved_path}")
            return {"success": True, "filepath": saved_path, "filename": filename}
        
        return {"success": False, "error": "Failed to write image to disk"}
    except Exception as e:
        print(f"[WEB API] Error saving screenshot: {e}")
        return {"success": False, "error": str(e)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket route that receives binary camera frames, performs face detection,
    calculates physical face distance, and sends coordinates back to the client.
    """
    await websocket.accept()
    try:
        while True:
            # Receive binary frame (JPEG) from browser (will raise disconnect exception if connection closed)
            data = await websocket.receive_bytes()
            
            # Decode JPEG binary payload into OpenCV image
            nparr = np.frombuffer(data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                await websocket.send_json({"success": False, "error": "Invalid frame data"})
                continue
            
            try:
                # Run MediaPipe face detector
                faces = detector.detect_faces(frame)
                
                # Build payload of coordinates and estimated distances
                payload = []
                for face in faces:
                    x, y, w, h = face["bbox"]
                    confidence = face["confidence"]
                    landmarks = face["landmarks"]
                    
                    # Calculate estimated distance in cm
                    distance_cm = calculate_distance(w)
                    
                    payload.append({
                        "bbox": [x, y, w, h],
                        "confidence": float(confidence),
                        "landmarks": landmarks,
                        "distance": float(round(distance_cm, 2))
                    })
            except Exception as inference_err:
                print(f"[DETECTION ERROR] Error during MediaPipe inference: {inference_err}")
                await websocket.send_json({"success": False, "error": str(inference_err)})
                continue
                
            # Send results back as JSON (will raise disconnect exception if connection closed)
            await websocket.send_json({
                "success": True,
                "faces": payload
            })
            
    except WebSocketDisconnect:
        # Client closed connection
        pass
    except Exception as e:
        print(f"[WEBSOCKET ERROR] Exception in WebSocket connection: {e}")
        try:
            await websocket.send_json({"success": False, "error": str(e)})
        except:
            pass
