import cv2
import time
import numpy as np
from src.config import (
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_TEXT, COLOR_HUD_BG,
    COLOR_SUCCESS, COLOR_GLOW, FONT_FACE, FONT_SCALE_HUD, FONT_SCALE_BOX,
    FONT_SCALE_ALERT, THICKNESS_HUD, THICKNESS_BOX, BOX_CORNER_LENGTH,
    BOX_CORNER_THICKNESS, BOX_RECTANGLE_THICKNESS, KEY_QUIT, KEY_SCREENSHOT,
    KEY_TOGGLE_HUD, KEY_TOGGLE_BOX
)

def draw_semi_transparent_rect(img, x, y, w, h, color=COLOR_HUD_BG, alpha=0.55):
    """
    Draws a semi-transparent colored rectangle overlay onto the frame.
    """
    sub_img = img[y:y+h, x:x+w]
    rect = np.full(sub_img.shape, color, dtype=np.uint8)
    res = cv2.addWeighted(sub_img, 1 - alpha, rect, alpha, 0)
    img[y:y+h, x:x+w] = res


def draw_hud_box(img, x, y, w, h, confidence, index):
    """
    Draws a futuristic HUD-style bounding box around detected faces.
    """
    # Draw a thin base rectangle
    cv2.rectangle(img, (x, y), (x + w, y + h), COLOR_PRIMARY, BOX_RECTANGLE_THICKNESS)

    # Draw thick corner ticks
    length = min(BOX_CORNER_LENGTH, w // 2, h // 2)
    t = BOX_CORNER_THICKNESS
    
    # Top-Left Corner
    cv2.line(img, (x, y), (x + length, y), COLOR_SECONDARY, t)
    cv2.line(img, (x, y), (x, y + length), COLOR_SECONDARY, t)

    # Top-Right Corner
    cv2.line(img, (x + w, y), (x + w - length, y), COLOR_SECONDARY, t)
    cv2.line(img, (x + w, y), (x + w, y + length), COLOR_SECONDARY, t)

    # Bottom-Left Corner
    cv2.line(img, (x, y + h), (x + length, y + h), COLOR_SECONDARY, t)
    cv2.line(img, (x, y + h), (x, y + h - length), COLOR_SECONDARY, t)

    # Bottom-Right Corner
    cv2.line(img, (x + w, y + h), (x + w - length, y + h), COLOR_SECONDARY, t)
    cv2.line(img, (x + w, y + h), (x + w, y + h - length), COLOR_SECONDARY, t)

    # Draw confidence label tag above the box
    text = f"FACE {index:02d} | {int(confidence * 100)}%"
    (text_w, text_h), baseline = cv2.getTextSize(text, FONT_FACE, FONT_SCALE_BOX, THICKNESS_HUD)
    
    # Draw label box
    label_y = y - 8 if y - 8 - text_h > 0 else y + text_h + 8
    label_x = x
    
    # Draw background for the label
    draw_semi_transparent_rect(img, label_x, label_y - text_h - 4, text_w + 10, text_h + 8, COLOR_HUD_BG, alpha=0.7)
    # Highlight left side of label
    cv2.rectangle(img, (label_x, label_y - text_h - 4), (label_x + 2, label_y + 4), COLOR_SECONDARY, -1)
    
    # Draw text
    cv2.putText(img, text, (label_x + 6, label_y - 2), FONT_FACE, FONT_SCALE_BOX, COLOR_TEXT, THICKNESS_HUD, cv2.LINE_AA)


def draw_hud_landmarks(img, landmarks):
    """
    Draws subtle highlights on detected face landmarks (eyes, nose, mouth).
    """
    for lm in landmarks:
        cv2.circle(img, lm, 3, COLOR_GLOW, -1)
        # Small crosshairs for a sci-fi feel
        cv2.line(img, (lm[0] - 5, lm[1]), (lm[0] + 5, lm[1]), COLOR_GLOW, 1)
        cv2.line(img, (lm[0], lm[1] - 5), (lm[0], lm[1] + 5), COLOR_GLOW, 1)


def draw_hud_interface(img, faces_count, fps, alert_msg=None, show_hud=True, show_boxes=True):
    """
    Renders the overall HUD dashboard structure onto the image.
    """
    h, w, _ = img.shape

    # 1. Top HUD Dashboard Panel
    if show_hud:
        panel_h = 50
        draw_semi_transparent_rect(img, 0, 0, w, panel_h, COLOR_HUD_BG, alpha=0.6)
        
        # Cyber bottom border line for the top dashboard
        cv2.line(img, (0, panel_h), (w, panel_h), COLOR_PRIMARY, 1)
        # Small corner indicators on top dash
        cv2.line(img, (10, panel_h), (30, panel_h), COLOR_SECONDARY, 2)
        cv2.line(img, (w - 30, panel_h), (w - 10, panel_h), COLOR_SECONDARY, 2)

        # Title & Blinking indicator
        title_text = "REAL-TIME FACE DETECTION SYSTEM"
        cv2.putText(img, title_text, (20, 30), FONT_FACE, FONT_SCALE_HUD + 0.1, COLOR_TEXT, THICKNESS_HUD, cv2.LINE_AA)
        
        # Binds blinking state to clock milliseconds
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
        cv2.line(img, (0, b_panel_y), (w, b_panel_y), COLOR_PRIMARY, 1)

        # Build shortcut guides
        k_quit = KEY_QUIT.upper()
        k_snap = KEY_SCREENSHOT.upper()
        k_hud = KEY_TOGGLE_HUD.upper()
        k_box = KEY_TOGGLE_BOX.upper()
        
        help_text = f"[{k_quit}] EXIT    [{k_snap}] SNAPSHOT    [{k_hud}] TOGGLE HUD    [{k_box}] TOGGLE DETECTIONS"
        cv2.putText(img, help_text, (20, h - 12), FONT_FACE, FONT_SCALE_HUD - 0.05, COLOR_TEXT, THICKNESS_HUD, cv2.LINE_AA)

    # 3. Toast Notifications/Alert Messages
    if alert_msg:
        alert_w, alert_h = 420, 45
        alert_x = (w - alert_w) // 2
        alert_y = h - 90
        
        # Panel Background
        draw_semi_transparent_rect(img, alert_x, alert_y, alert_w, alert_h, COLOR_HUD_BG, alpha=0.85)
        # Bounding border
        cv2.rectangle(img, (alert_x, alert_y), (alert_x + alert_w, alert_y + alert_h), COLOR_SECONDARY, 1)
        # Left edge accent
        cv2.rectangle(img, (alert_x, alert_y), (alert_x + 4, alert_y + alert_h), COLOR_SECONDARY, -1)
        
        # Text positioning centered inside the alert box
        (tw, th), tb = cv2.getTextSize(alert_msg, FONT_FACE, FONT_SCALE_ALERT, THICKNESS_HUD)
        tx = alert_x + (alert_w - tw) // 2
        ty = alert_y + (alert_h + th) // 2
        cv2.putText(img, alert_msg, (tx, ty), FONT_FACE, FONT_SCALE_ALERT, COLOR_TEXT, THICKNESS_HUD, cv2.LINE_AA)
