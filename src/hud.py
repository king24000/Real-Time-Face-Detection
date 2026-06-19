import cv2
import time
import numpy as np
from src.config import (
    COLOR_TEXT, COLOR_HUD_BG, COLOR_SUCCESS, FONT_FACE, FONT_SCALE_HUD, 
    FONT_SCALE_BOX, FONT_SCALE_ALERT, THICKNESS_HUD, THICKNESS_BOX, 
    BOX_CORNER_LENGTH, BOX_CORNER_THICKNESS, BOX_RECTANGLE_THICKNESS, 
    KEY_QUIT, KEY_SCREENSHOT, KEY_TOGGLE_HUD, KEY_TOGGLE_BOX, KEY_CYCLE_THEME
)

def draw_semi_transparent_rect(img, x, y, w, h, color=COLOR_HUD_BG, alpha=0.55):
    """
    Draws a semi-transparent colored rectangle overlay onto the frame.
    """
    sub_img = img[y:y+h, x:x+w]
    rect = np.full(sub_img.shape, color, dtype=np.uint8)
    res = cv2.addWeighted(sub_img, 1 - alpha, rect, alpha, 0)
    img[y:y+h, x:x+w] = res


def draw_hud_box(img, x, y, w, h, confidence, index, theme, distance):
    """
    Draws a futuristic HUD-style bounding box with dynamic theme colors 
    and estimated face distance.
    """
    primary_color = theme["primary"]
    secondary_color = theme["secondary"]

    # Draw a thin base rectangle
    cv2.rectangle(img, (x, y), (x + w, y + h), primary_color, BOX_RECTANGLE_THICKNESS)

    # Draw thick corner ticks
    length = min(BOX_CORNER_LENGTH, w // 2, h // 2)
    t = BOX_CORNER_THICKNESS
    
    # Top-Left Corner
    cv2.line(img, (x, y), (x + length, y), secondary_color, t)
    cv2.line(img, (x, y), (x, y + length), secondary_color, t)

    # Top-Right Corner
    cv2.line(img, (x + w, y), (x + w - length, y), secondary_color, t)
    cv2.line(img, (x + w, y), (x + w, y + length), secondary_color, t)

    # Bottom-Left Corner
    cv2.line(img, (x, y + h), (x + length, y + h), secondary_color, t)
    cv2.line(img, (x, y + h), (x, y + h - length), secondary_color, t)

    # Bottom-Right Corner
    cv2.line(img, (x + w, y + h), (x + w - length, y + h), secondary_color, t)
    cv2.line(img, (x + w, y + h), (x + w, y + h - length), secondary_color, t)

    # Format distance label
    if distance < 100.0:
        dist_str = f"{distance:.0f}cm"
    else:
        dist_str = f"{distance/100.0:.2f}m"

    # Draw confidence & distance label tag above the box
    text = f"FACE {index:02d} | Conf: {int(confidence * 100)}% | Dist: {dist_str}"
    (text_w, text_h), baseline = cv2.getTextSize(text, FONT_FACE, FONT_SCALE_BOX, THICKNESS_HUD)
    
    # Draw label box position
    label_y = y - 8 if y - 8 - text_h > 0 else y + text_h + 8
    label_x = x
    
    # Draw background for the label
    draw_semi_transparent_rect(img, label_x, label_y - text_h - 4, text_w + 10, text_h + 8, COLOR_HUD_BG, alpha=0.7)
    # Highlight left side of label
    cv2.rectangle(img, (label_x, label_y - text_h - 4), (label_x + 2, label_y + 4), secondary_color, -1)
    
    # Draw text
    cv2.putText(img, text, (label_x + 6, label_y - 2), FONT_FACE, FONT_SCALE_BOX, COLOR_TEXT, THICKNESS_HUD, cv2.LINE_AA)


def draw_hud_landmarks(img, landmarks, theme):
    """
    Draws custom sci-fi neon glasses on the eyes and subtle trackers 
    on the nose/mouth landmarks.
    """
    if len(landmarks) < 6:
        return

    eye_left = landmarks[0]   # Viewer's left eye (person's right)
    eye_right = landmarks[1]  # Viewer's right eye (person's left)
    nose = landmarks[2]       # Nose tip
    mouth = landmarks[3]      # Mouth center
    ear_left = landmarks[4]   # Viewer's left ear
    ear_right = landmarks[5]  # Viewer's right ear

    primary_color = theme["primary"]
    secondary_color = theme["secondary"]
    glow_color = theme["glow"]

    # 1. Calculate dimensions for glasses based on eye distance
    dx = eye_right[0] - eye_left[0]
    dy = eye_right[1] - eye_left[1]
    eye_dist = np.sqrt(dx**2 + dy**2)
    
    if eye_dist > 0:
        # Radius of lenses is proportional to distance between eyes
        r = int(eye_dist * 0.32)
        
        # Draw glasses bridge connecting the eyes
        cv2.line(img, eye_left, eye_right, primary_color, 2, cv2.LINE_AA)
        
        # Draw side temples connecting eyes to ears
        cv2.line(img, eye_left, ear_left, secondary_color, 1, cv2.LINE_AA)
        cv2.line(img, eye_right, ear_right, secondary_color, 1, cv2.LINE_AA)
        
        # Draw hex lenses around eyes
        for eye_center in [eye_left, eye_right]:
            # Outer Hexagon
            points_outer = []
            for i in range(6):
                angle = i * np.pi / 3 + np.pi / 6  # Flat top/bottom rotated
                x = int(eye_center[0] + r * np.cos(angle))
                y = int(eye_center[1] + r * np.sin(angle))
                points_outer.append((x, y))
            pts_outer = np.array(points_outer, np.int32).reshape((-1, 1, 2))
            cv2.polylines(img, [pts_outer], isClosed=True, color=primary_color, thickness=2, lineType=cv2.LINE_AA)

            # Inner Hexagon (Neon double-ring effect)
            points_inner = []
            r_inner = int(r * 0.75)
            for i in range(6):
                angle = i * np.pi / 3 + np.pi / 6
                x = int(eye_center[0] + r_inner * np.cos(angle))
                y = int(eye_center[1] + r_inner * np.sin(angle))
                points_inner.append((x, y))
            pts_inner = np.array(points_inner, np.int32).reshape((-1, 1, 2))
            cv2.polylines(img, [pts_inner], isClosed=True, color=glow_color, thickness=1, lineType=cv2.LINE_AA)

            # Draw a tiny center dot in the eye
            cv2.circle(img, eye_center, 2, glow_color, -1, cv2.LINE_AA)

    # 2. Draw subtle tracker markers for nose & mouth
    for landmark_point in [nose, mouth]:
        cv2.circle(img, landmark_point, 2, glow_color, -1, cv2.LINE_AA)
        cv2.line(img, (landmark_point[0] - 4, landmark_point[1]), (landmark_point[0] + 4, landmark_point[1]), glow_color, 1, cv2.LINE_AA)
        cv2.line(img, (landmark_point[0], landmark_point[1] - 4), (landmark_point[0], landmark_point[1] + 4), glow_color, 1, cv2.LINE_AA)


def draw_hud_interface(img, faces_count, fps, theme, alert_msg=None, show_hud=True, show_boxes=True):
    """
    Renders the overall HUD dashboard structure onto the image.
    """
    h, w, _ = img.shape
    primary_color = theme["primary"]
    secondary_color = theme["secondary"]

    # 1. Top HUD Dashboard Panel
    if show_hud:
        panel_h = 50
        draw_semi_transparent_rect(img, 0, 0, w, panel_h, COLOR_HUD_BG, alpha=0.6)
        
        # Cyber bottom border line for the top dashboard
        cv2.line(img, (0, panel_h), (w, panel_h), primary_color, 1)
        # Small corner indicators on top dash
        cv2.line(img, (10, panel_h), (30, panel_h), secondary_color, 2)
        cv2.line(img, (w - 30, panel_h), (w - 10, panel_h), secondary_color, 2)

        # Title & Blinking indicator
        title_text = "REAL-TIME FACE DETECTION HUD v2.0"
        cv2.putText(img, title_text, (20, 30), FONT_FACE, FONT_SCALE_HUD + 0.1, COLOR_TEXT, THICKNESS_HUD, cv2.LINE_AA)
        
        # Binds blinking state to clock seconds
        blink = int(time.time() * 2) % 2 == 0
        status_color = COLOR_SUCCESS if blink else (50, 100, 50)
        cv2.circle(img, (w - 280, 25), 6, status_color, -1)
        cv2.putText(img, "LIVE FEED", (w - 265, 30), FONT_FACE, FONT_SCALE_HUD, COLOR_TEXT, THICKNESS_HUD, cv2.LINE_AA)

        # Stats info
        stats_text = f"TARGETS: {faces_count:02d}  |  FPS: {fps}"
        cv2.putText(img, stats_text, (w - 180, 30), FONT_FACE, FONT_SCALE_HUD, COLOR_TEXT, THICKNESS_HUD, cv2.LINE_AA)

    # 2. Bottom Help/Command Panel
    if show_hud:
        b_panel_h = 35
        b_panel_y = h - b_panel_h
        draw_semi_transparent_rect(img, 0, b_panel_y, w, b_panel_h, COLOR_HUD_BG, alpha=0.6)
        
        # Top border line for bottom panel
        cv2.line(img, (0, b_panel_y), (w, b_panel_y), primary_color, 1)

        # Build shortcut guides
        k_quit = KEY_QUIT.upper()
        k_snap = KEY_SCREENSHOT.upper()
        k_hud = KEY_TOGGLE_HUD.upper()
        k_box = KEY_TOGGLE_BOX.upper()
        k_theme = KEY_CYCLE_THEME.upper()
        
        help_text = f"[{k_quit}] EXIT   [{k_snap}] SNAPSHOT   [{k_hud}] TOGGLE HUD   [{k_box}] DETECTIONS   [{k_theme}] THEME: {theme['name']}"
        cv2.putText(img, help_text, (20, h - 12), FONT_FACE, FONT_SCALE_HUD - 0.05, COLOR_TEXT, THICKNESS_HUD, cv2.LINE_AA)

    # 3. Toast Notifications/Alert Messages
    if alert_msg:
        alert_w, alert_h = 450, 45
        alert_x = (w - alert_w) // 2
        alert_y = h - 90
        
        # Panel Background
        draw_semi_transparent_rect(img, alert_x, alert_y, alert_w, alert_h, COLOR_HUD_BG, alpha=0.85)
        # Bounding border
        cv2.rectangle(img, (alert_x, alert_y), (alert_x + alert_w, alert_y + alert_h), secondary_color, 1)
        # Left edge accent
        cv2.rectangle(img, (alert_x, alert_y), (alert_x + 4, alert_y + alert_h), secondary_color, -1)
        
        # Text positioning centered inside the alert box
        (tw, th), tb = cv2.getTextSize(alert_msg, FONT_FACE, FONT_SCALE_ALERT, THICKNESS_HUD)
        tx = alert_x + (alert_w - tw) // 2
        ty = alert_y + (alert_h + th) // 2
        cv2.putText(img, alert_msg, (tx, ty), FONT_FACE, FONT_SCALE_ALERT, COLOR_TEXT, THICKNESS_HUD, cv2.LINE_AA)
