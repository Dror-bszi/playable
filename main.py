from core.gestures import GestureDetector
from core.mappings import get_button_for_gesture
from web.server import run_server, set_web_status, should_shutdown
import cv2
import threading
import time
import os
import sys
import subprocess
from evdev import UInput, ecodes as e

# ─── Constants ───────────────────────────────────────────────
BTN_CIRCLE = 305

# ─── Permissions and Module Checks ────────────────────────────
if os.geteuid() != 0:
    print("❌ ERROR: This script must be run with sudo -E python3 main.py")
    sys.exit(1)

def load_uinput_module():
    try:
        subprocess.run(["modprobe", "uinput"], check=True)
        print("[INFO] uinput kernel module loaded successfully!")
    except subprocess.CalledProcessError:
        print("❌ ERROR: Failed to load uinput module!")
        sys.exit(1)

load_uinput_module()

# ─── Create Virtual Controller ───────────────────────────────
capabilities = {
    e.EV_KEY: [BTN_CIRCLE],
}
ui = UInput(capabilities)
print("[INFO] Virtual controller created.")
time.sleep(1)

# ─── Initialize Camera ───────────────────────────────────────
cap = find_working_camera()

def find_working_camera():
    for i in range(3):  # check /dev/video0, /dev/video1, /dev/video2
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"[INFO] Found working camera at index {i} (/dev/video{i})")
            return cap
        cap.release()
    print("❌ ERROR: No working camera found.")
    return None

# ─── Start Web Server ─────────────────────────────────────────
threading.Thread(target=run_server, daemon=True).start()

# ─── Gesture Detection Loop ───────────────────────────────────
def gesture_detection_loop():
    if cap is not None:
        print("[INFO] Starting gesture detection...")
        detector = GestureDetector()

        set_web_status("Calibrate: Hold rest position...")
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            if detector.calibrate(frame):
                set_web_status("Calibration complete!")
                break

        gesture_active = False
        set_web_status("Start gesture detection")

        while True:
            if should_shutdown():
                break

            ret, frame = cap.read()
            if not ret:
                continue

            elbow_raised = detector.is_elbow_raised_forward(frame)
            if elbow_raised and not gesture_active:
                button = get_button_for_gesture("elbow_raised")
                if button:
                    set_web_status(f"Pressed: {button.upper()}")
                    emulate_circle_press()
                gesture_active = True

            elif (not elbow_raised) and gesture_active:
                gesture_active = False
                set_web_status("Waiting for gesture...")

        cap.release()
        cv2.destroyAllWindows()
    else:
        set_web_status("❌ Camera not found. Running in UI-only mode.")
        while True:
            if should_shutdown():
                break
if __name__ == "__main__":
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] PlayAble shutting down...")


threading.Thread(target=gesture_detection_loop, daemon=True).start()

# ─── Emulate Circle Button ────────────────────────────────────
def emulate_circle_press():
    print("[INFO] Emulating CIRCLE press...")
    ui.write(e.EV_KEY, BTN_CIRCLE, 1)
    ui.syn()
    time.sleep(0.1)
    ui.write(e.EV_KEY, BTN_CIRCLE, 0)
    ui.syn()
    print("[INFO] Circle Press Complete!")
