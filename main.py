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

BTN_CIRCLE = e.BTN_CIRCLE  # evdev constant
TEST_MODE = True           # Set to False later to disable test loop

# ─── Permissions and Module Checks ─────────────────────────────

# Check for sudo/root
if os.geteuid() != 0:
    print("❌ ERROR: This script must be run with sudo -E python3 main.py")
    sys.exit(1)

# Try to load uinput kernel module
def load_uinput_module():
    try:
        subprocess.run(["modprobe", "uinput"], check=True)
        print("[INFO] uinput kernel module loaded successfully!")
    except subprocess.CalledProcessError:
        print("❌ ERROR: Failed to load uinput module!")
        sys.exit(1)

load_uinput_module()

# ─── Initialize Virtual Input Device ──────────────────────────

capabilities = {
    e.EV_KEY: [BTN_CIRCLE],
}

ui = UInput(capabilities)
time.sleep(1)  # Give time for virtual device to register

# ─── Initialize Camera ─────────────────────────────────────────

cap = cv2.VideoCapture(0)

# Start web server in background
threading.Thread(target=run_server, daemon=True).start()

# ─── Gesture Detection Loop ────────────────────────────────────

def gesture_detection_loop():
    if cap.isOpened():
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
                    # (Later: call emulate_circle_press() here)
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

# Start gesture detection loop in background
threading.Thread(target=gesture_detection_loop, daemon=True).start()

# ─── Local Circle Emulation ────────────────────────────────────

def emulate_circle_press():
    print("[INFO] Emulating CIRCLE press...")
    ui.write(e.EV_KEY, BTN_CIRCLE, 1)  # Press
    ui.syn()
    time.sleep(0.1)
    ui.write(e.EV_KEY, BTN_CIRCLE, 0)  # Release
    ui.syn()
    print("[INFO] Circle Press Complete!")

# ─── Main Loop ─────────────────────────────────────────────────

if __name__ == "__main__" and TEST_MODE:
    while True:
        emulate_circle_press()
        time.sleep(5)
