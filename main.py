from core.gestures import GestureDetector
from core.mappings import get_button_for_gesture
from web.server import run_server, set_web_status, should_shutdown
import cv2
import threading
import time
import os
import sys

from web.server import gesture_mappings  # Add this import!
from remote.controller_bridge import emulate_circle_press
  # load_uinput already handled there

# ─── Permissions Check ───────────────────────────────────────
if os.geteuid() != 0:
    print("❌ ERROR: This script must be run with sudo -E python3 main.py")
    sys.exit(1)

# ─── Initialize Camera ───────────────────────────────────────
def find_working_camera():
    for i in range(3):  # check /dev/video0, /dev/video1, /dev/video2
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"[INFO] Found working camera at index {i} (/dev/video{i})")
            return cap
        cap.release()
    print("❌ ERROR: No working camera found.")
    return None

cap = find_working_camera()

# ─── Start Web Server ─────────────────────────────────────────
threading.Thread(target=run_server, daemon=True).start()

# ─── Gesture Detection Loop ───────────────────────────────────
def gesture_detection_loop():
    global cap
    if cap is None:
        set_web_status("❌ No camera available. Running in UI-only mode.")
        while not should_shutdown():
            time.sleep(1)
        return

    print("[INFO] Starting gesture detection...")
    detector = GestureDetector()

    set_web_status("Calibrate: Hold rest position...")

    # ─── Calibration Phase ───────────────────────
    calibrated = False
    while not calibrated and not should_shutdown():
        ret, frame = cap.read()
        if not ret or frame is None:
            print("[WARN] Failed to read frame during calibration.")
            time.sleep(0.5)
            continue
        calibrated = detector.calibrate(frame)

    if not calibrated:
        print("❌ Calibration failed.")
        return

    set_web_status("Calibration complete!")

    # ─── Main Detection Loop ─────────────────────
    gesture_active = {gesture: False for gesture in GESTURE_TO_BUTTON.keys()}

    set_web_status("Start gesture detection")

    while not should_shutdown():
        ret, frame = cap.read()
        if not ret or frame is None:
            print("[WARN] Failed to read frame.")
            time.sleep(0.5)
            continue

        for gesture_name, assigned_button in GESTURE_TO_BUTTON.items():
            if assigned_button is None:
                continue  # Skip gestures not mapped to buttons

            # Check the gesture dynamically:
            is_detected = False
            if gesture_name == "left_elbow_raised_forward":
                is_detected = detector.is_left_elbow_raised_forward(frame)
            elif gesture_name == "mouth_open":
                is_detected = detector.is_mouth_open(frame)
            elif gesture_name == "head_tilt_right":
                is_detected = detector.is_head_tilt_right(frame)
            elif gesture_name == "right_elbow_raised_forward":
                is_detected = detector.is_right_elbow_raised_forward(frame)

            if is_detected and not gesture_active[gesture_name]:
                set_web_status(f"Pressed: {assigned_button.upper()}")
                emulate_circle_press()  # Later replace to send the correct button
                gesture_active[gesture_name] = True

            elif not is_detected and gesture_active[gesture_name]:
                gesture_active[gesture_name] = False
                set_web_status("Waiting for gesture...")

    cap.release()
    cv2.destroyAllWindows()

# ─── Start Gesture Detection Thread ───────────────────────────
threading.Thread(target=gesture_detection_loop, daemon=True).start()

# ─── Main Blocking Loop ───────────────────────────────────────
if __name__ == "__main__":
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] PlayAble shutting down...")
