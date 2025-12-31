import cv2
import time
import numpy as np
from typing import Optional, Tuple

from hand_tracking import HandTracker
from gesture_controller import fingers_up, is_pinch, distance
from canvas import Canvas

# ---------------- CONFIG ----------------
WIDTH, HEIGHT = 1280, 720
FPS_TARGET = 30
FRAME_TIME = 1.0 / FPS_TARGET

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
cap.set(cv2.CAP_PROP_FPS, FPS_TARGET)

if not cap.isOpened():
    print("Error: Could not open camera")
    print("\nTroubleshooting:")
    print("  1. Check if camera is being used by another app")
    print("  2. Try different camera index: cv2.VideoCapture(1)")
    print("  3. Check camera permissions")
    exit(1)

try:
    tracker = HandTracker(mode='performance')
except Exception as e:
    print(f"\nFailed to initialize hand tracker: {e}")
    print("\nTo fix this, run one of these commands:")
    print("   python setup.py        (recommended - full setup)")
    print("   python download_model.py   (just download model)")
    cap.release()
    exit(1)

canvas = Canvas(WIDTH, HEIGHT)

DEBUG_MODE = False
show_stats = False
show_instructions = False

# ---------------- UI CONFIG ----------------
UI_HEIGHT = 90
BUTTON_HEIGHT = 60
BUTTON_WIDTH = 100
MARGIN = 15
START_Y = 15

COLORS = [
    ("BLUE", (255, 0, 0)),
    ("GREEN", (0, 255, 0)),
    ("RED", (0, 0, 255)),
    ("YELLOW", (0, 255, 255)),
    ("PURPLE", (255, 0, 255)),
    ("ORANGE", (0, 165, 255)),
    ("CYAN", (255, 255, 0)),
    ("WHITE", (255, 255, 255))
]

color_index = 0
canvas.current_color = COLORS[color_index][1]

current_tool = "DRAW"
gesture_cooldown = 0
button_click_cooldown = 0

DRAWING_ZONE_Y = UI_HEIGHT + 10

# ---------------- UI HELPERS ----------------
def draw_button(img: np.ndarray, x: int, y: int, w: int, h: int,
                text: str, color: Tuple[int, int, int],
                active: bool = False, hover: bool = False) -> None:
    shadow_offset = 3
    cv2.rectangle(img, (x+shadow_offset, y+shadow_offset),
                  (x+w+shadow_offset, y+h+shadow_offset), (20, 20, 20), -1)

    if hover:
        btn_color = tuple(min(c + 30, 255) for c in color)
    else:
        btn_color = color

    cv2.rectangle(img, (x, y), (x+w, y+h), btn_color, -1)

    if active:
        cv2.rectangle(img, (x-2, y-2), (x+w+2, y+h+2), (255, 255, 255), 3)
        cv2.rectangle(img, (x, y), (x+w, y+h), (200, 200, 200), 2)

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5 if len(text) > 6 else 0.6
    text_size = cv2.getTextSize(text, font, font_scale, 2)[0]
    text_x = x + (w - text_size[0]) // 2
    text_y = y + (h + text_size[1]) // 2

    cv2.putText(img, text, (text_x+1, text_y+1), font, font_scale, (0, 0, 0), 2)
    cv2.putText(img, text, (text_x, text_y), font, font_scale, (255, 255, 255), 2)


def is_hovering_button(x: int, y: int, btn_x: int, btn_y: int,
                       btn_w: int, btn_h: int) -> bool:
    return btn_x <= x <= btn_x + btn_w and btn_y <= y <= btn_y + btn_h


def draw_ui(img: np.ndarray, hover_x: Optional[int] = None,
            hover_y: Optional[int] = None) -> None:
    overlay = img.copy()
    cv2.rectangle(overlay, (0, 0), (WIDTH, UI_HEIGHT), (30, 30, 30), -1)
    cv2.addWeighted(overlay, 0.85, img, 0.15, 0, img)

    cv2.line(img, (0, UI_HEIGHT), (WIDTH, UI_HEIGHT), (100, 100, 100), 2)

    x = MARGIN

    for i, (name, color) in enumerate(COLORS):
        is_hover = False
        if hover_x is not None and hover_y is not None:
            is_hover = is_hovering_button(hover_x, hover_y, x, START_Y, BUTTON_WIDTH, BUTTON_HEIGHT)

        is_active = (i == color_index and current_tool == "DRAW")

        draw_button(
            img, x, START_Y, BUTTON_WIDTH, BUTTON_HEIGHT,
            name, color, active=is_active, hover=is_hover
        )
        x += BUTTON_WIDTH + MARGIN

    is_hover = False
    if hover_x is not None and hover_y is not None:
        is_hover = is_hovering_button(hover_x, hover_y, x, START_Y, BUTTON_WIDTH, BUTTON_HEIGHT)

    draw_button(img, x, START_Y, BUTTON_WIDTH, BUTTON_HEIGHT,
                "ERASER", (100, 100, 100),
                active=(current_tool == "ERASE"), hover=is_hover)
    x += BUTTON_WIDTH + MARGIN

    is_hover = False
    if hover_x is not None and hover_y is not None:
        is_hover = is_hovering_button(hover_x, hover_y, x, START_Y, BUTTON_WIDTH, BUTTON_HEIGHT)

    draw_button(img, x, START_Y, BUTTON_WIDTH, BUTTON_HEIGHT,
                "CLEAR", (180, 0, 0), hover=is_hover)
    x += BUTTON_WIDTH + MARGIN

    is_hover = False
    if hover_x is not None and hover_y is not None:
        is_hover = is_hovering_button(hover_x, hover_y, x, START_Y, BUTTON_WIDTH, BUTTON_HEIGHT)

    draw_button(img, x, START_Y, BUTTON_WIDTH, BUTTON_HEIGHT,
                "UNDO", (0, 120, 180), hover=is_hover)


def check_buttons(x: int, y: int) -> bool:
    global color_index, current_tool, button_click_cooldown

    if button_click_cooldown > 0:
        return False

    if y < START_Y or y > START_Y + BUTTON_HEIGHT:
        return False

    pos = MARGIN

    for i in range(len(COLORS)):
        if pos <= x <= pos + BUTTON_WIDTH:
            color_index = i
            canvas.current_color = COLORS[color_index][1]
            current_tool = "DRAW"
            button_click_cooldown = 15
            return True
        pos += BUTTON_WIDTH + MARGIN

    if pos <= x <= pos + BUTTON_WIDTH:
        current_tool = "ERASE"
        button_click_cooldown = 15
        return True
    pos += BUTTON_WIDTH + MARGIN

    if pos <= x <= pos + BUTTON_WIDTH:
        canvas.clear()
        button_click_cooldown = 15
        return True
    pos += BUTTON_WIDTH + MARGIN

    if pos <= x <= pos + BUTTON_WIDTH:
        canvas.undo()
        button_click_cooldown = 15
        return True

    return False


def draw_cursor(img: np.ndarray, x: int, y: int,
                is_drawing: bool = False, is_eraser: bool = False) -> None:
    if is_eraser:
        cv2.circle(img, (x, y), canvas.eraser_thickness // 2, (100, 100, 100), 2)
        cv2.circle(img, (x, y), 5, (150, 150, 150), -1)
    elif is_drawing:
        cv2.circle(img, (x, y), canvas.brush_thickness // 2, canvas.current_color, 2)
        cv2.circle(img, (x, y), 3, canvas.current_color, -1)
    else:
        cv2.circle(img, (x, y), 8, (255, 255, 255), 2)
        cv2.circle(img, (x, y), 3, (0, 200, 255), -1)


def draw_info_panel(img: np.ndarray) -> None:
    info_bg = img.copy()
    panel_height = 100
    cv2.rectangle(info_bg, (WIDTH - 300, HEIGHT - panel_height),
                  (WIDTH - 10, HEIGHT - 10), (30, 30, 30), -1)
    cv2.addWeighted(info_bg, 0.8, img, 0.2, 0, img)

    y_offset = HEIGHT - panel_height + 25
    font = cv2.FONT_HERSHEY_SIMPLEX

    tool_text = f"Tool: {current_tool}"
    cv2.putText(img, tool_text, (WIDTH - 285, y_offset), font, 0.5, (255, 255, 255), 1)

    y_offset += 20
    color_name = COLORS[color_index][0]
    cv2.putText(img, f"Color: {color_name}", (WIDTH - 285, y_offset), font, 0.5, (255, 255, 255), 1)
    cv2.circle(img, (WIDTH - 100, y_offset - 7), 10, canvas.current_color, -1)
    cv2.circle(img, (WIDTH - 100, y_offset - 7), 11, (255, 255, 255), 1)

    y_offset += 20
    size = canvas.eraser_thickness if current_tool == "ERASE" else canvas.brush_thickness
    cv2.putText(img, f"Size: {size}px", (WIDTH - 285, y_offset), font, 0.5, (255, 255, 255), 1)


def draw_instructions(img: np.ndarray) -> None:
    instructions = [
        ("Gestures:", (255, 255, 0)),
        ("  Open palm (5 fingers) - Clear", (200, 200, 200)),
        ("  Index finger - Draw/Click", (200, 200, 200)),
        ("  Pinch - Eraser mode", (200, 200, 200)),
        ("  3 fingers - Next color", (200, 200, 200)),
        ("  Thumb + Pinky - Undo", (200, 200, 200)),
        ("", (0, 0, 0)),
        ("Keys:", (255, 255, 0)),
        ("  D - Debug | S - Stats", (200, 200, 200)),
        ("  I - Instructions | ESC - Exit", (200, 200, 200))
    ]

    overlay = img.copy()
    panel_width = 350
    panel_height = len(instructions) * 25 + 30
    start_x = WIDTH - panel_width - 20
    start_y = 120

    cv2.rectangle(overlay, (start_x, start_y),
                  (start_x + panel_width, start_y + panel_height),
                  (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.85, img, 0.15, 0, img)

    cv2.rectangle(img, (start_x, start_y),
                  (start_x + panel_width, start_y + panel_height),
                  (100, 100, 100), 2)

    y_offset = start_y + 25
    for text, color in instructions:
        if text:
            cv2.putText(img, text, (start_x + 15, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        y_offset += 25


# ---------------- MAIN LOOP ----------------
print("Air Canvas Pro - Enhanced Edition")
print("=" * 60)
print("Gestures:")
print("  Open palm (5 fingers) - Clear canvas")
print("  Index finger - Draw/Click buttons")
print("  Pinch (thumb+index) - Eraser mode")
print("  Three fingers - Cycle colors")
print("  Thumb + Pinky - Undo")
print("  Thumb-Index distance - Adjust brush size")
print("\nKeyboard Shortcuts:")
print("  ESC - Exit  |  D - Debug  |  S - Stats  |  I - Instructions")
print("  R - Reset Stats  |  H - Help")
print("=" * 60)

fps_counter = 0
fps_start_time = time.time()
current_fps = 0

try:
    while True:
        frame_start = time.time()

        success, img = cap.read()
        if not success:
            print("Failed to read from camera")
            break

        img = cv2.flip(img, 1)

        fps_counter += 1
        if time.time() - fps_start_time >= 1.0:
            current_fps = fps_counter
            fps_counter = 0
            fps_start_time = time.time()

        tracker.detect(img)
        lm = tracker.get_landmarks(img)

        hover_x: Optional[int] = None
        hover_y: Optional[int] = None
        is_drawing = False
        is_eraser_mode = False

        if lm:
            fingers = fingers_up(lm)
            x, y = lm[8][1], lm[8][2]
            thumb = lm[4][1:]
            index = lm[8][1:]

            hover_x, hover_y = x, y

            d = distance(thumb, index)
            new_size = int(max(4, min(40, d / 3)))
            canvas.set_brush_size(new_size)

            in_ui_zone = y < DRAWING_ZONE_Y

            if fingers[1] and not fingers[2] and in_ui_zone:
                check_buttons(x, y)

            elif gesture_cooldown == 0:
                if all(fingers):
                    canvas.clear()
                    gesture_cooldown = 30

                elif fingers[1] and fingers[2] and fingers[3] and not fingers[0] and not fingers[4]:
                    color_index = (color_index + 1) % len(COLORS)
                    canvas.current_color = COLORS[color_index][1]
                    current_tool = "DRAW"
                    gesture_cooldown = 20

                elif fingers[0] and fingers[4] and not fingers[1] and not fingers[2] and not fingers[3]:
                    canvas.undo()
                    gesture_cooldown = 20

            if fingers[1] and not fingers[2] and not in_ui_zone:
                is_eraser_mode = (current_tool == "ERASE") or is_pinch(lm, threshold=35)
                canvas.draw(x, y, eraser=is_eraser_mode)
                is_drawing = True
            else:
                canvas.reset()

        else:
            canvas.reset()

        if gesture_cooldown > 0:
            gesture_cooldown -= 1
        if button_click_cooldown > 0:
            button_click_cooldown -= 1

        # ---------------- MERGE CANVAS ----------------
        gray = cv2.cvtColor(canvas.canvas, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)

        img_bg = cv2.bitwise_and(img, img, mask=mask_inv)
        canvas_fg = cv2.bitwise_and(canvas.canvas, canvas.canvas, mask=mask)
        img = cv2.add(img_bg, canvas_fg)

        draw_ui(img, hover_x, hover_y)

        if DEBUG_MODE and lm is not None:
            tracker.draw_landmarks(img, lm, draw_connections=True)

            bbox = tracker.get_hand_bbox(lm)
            if bbox:
                bx, by, bw, bh = bbox
                cv2.rectangle(img, (bx, by), (bx+bw, by+bh), (255, 255, 0), 2)

            handedness = tracker.get_handedness()
            if handedness:
                cv2.putText(img, f"Hand: {handedness}", (20, 150),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        if hover_x is not None and hover_y is not None:
            draw_cursor(img, hover_x, hover_y, is_drawing, is_eraser_mode)

        draw_info_panel(img)

        if show_stats:
            stats = tracker.get_statistics()
            y_pos = 120
            cv2.putText(img, f"Detection Rate: {stats['success_rate']:.1f}%",
                       (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            y_pos += 20
            cv2.putText(img, f"Stable: {stats['currently_stable']}",
                       (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            y_pos += 20
            cv2.putText(img, f"Confidence: {stats['confidence']:.2f}",
                       (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        if show_instructions:
            draw_instructions(img)

        fps_color = (0, 255, 0) if current_fps >= 25 else (0, 165, 255)
        cv2.putText(img, f"FPS: {current_fps}", (20, HEIGHT - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, fps_color, 2)

        cv2.imshow("Air Canvas Pro - Enhanced", img)

        elapsed = time.time() - frame_start
        if elapsed < FRAME_TIME:
            wait_time = int((FRAME_TIME - elapsed) * 1000)
            key = cv2.waitKey(max(1, wait_time)) & 0xFF
        else:
            key = cv2.waitKey(1) & 0xFF

        if key == 27:
            break
        elif key == ord('d') or key == ord('D'):
            DEBUG_MODE = not DEBUG_MODE
            print(f"Debug mode: {'ON' if DEBUG_MODE else 'OFF'}")
        elif key == ord('s') or key == ord('S'):
            show_stats = not show_stats
            print(f"Stats display: {'ON' if show_stats else 'OFF'}")
        elif key == ord('i') or key == ord('I'):
            show_instructions = not show_instructions
            print(f"Instructions: {'ON' if show_instructions else 'OFF'}")
        elif key == ord('r') or key == ord('R'):
            tracker.reset_statistics()
            print("Statistics reset")
        elif key == ord('h') or key == ord('H'):
            print("\n" + "="*60)
            print("KEYBOARD SHORTCUTS:")
            print("  ESC - Exit application")
            print("  D   - Toggle debug mode (show hand landmarks)")
            print("  S   - Toggle statistics display")
            print("  I   - Toggle instructions overlay")
            print("  R   - Reset tracking statistics")
            print("  H   - Show this help")
            print("="*60 + "\n")

except KeyboardInterrupt:
    print("\nInterrupted by user")
except Exception as e:
    print(f"\nError occurred: {e}")
    import traceback
    traceback.print_exc()
finally:
    cap.release()
    cv2.destroyAllWindows()
    tracker.cleanup()
    print("Air Canvas closed. Thanks for creating!")