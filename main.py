from core.gestures import GestureDetector
from core.mappings import get_button_for_gesture
from web.server import run_server, set_web_status, should_shutdown
import cv2
import threading
import time
import os
import sys

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

    # Calibration phase
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

    # Main detection loop
    gesture_active = False
    set_web_status("Start gesture detection")

    while not should_shutdown():
        ret, frame = cap.read()
        if not ret or frame is None:
            print("[WARN] Failed to read frame.")
            time.sleep(0.5)
            continue

        elbow_raised = detector.is_elbow_raised_forward(frame)
        if elbow_raised and not gesture_active:
            button = get_button_for_gesture("elbow_raised")
            if button:
                set_web_status(f"Pressed: {button.upper()}")
                emulate_circle_press()
            gesture_active = True
        elif not elbow_raised and gesture_active:
            gesture_active = False
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
