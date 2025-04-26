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
BTN_CIRCLE = 305  # Manual definition because some evdev versions don't have BTN_CIRCLE
TEST_MODE = True  # Set to False to disable test loop
REAL_DUALSENSE_PATH = "/dev/input/event8"
VIRTUAL_DEVICE_PATH = "/dev/input/event4"
MERGED_DEVICE_LINK = "/dev/input/by-id/merged-playable"

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
time.sleep(1)  # Give some time for event4 to appear

# ─── Start evsieve to merge real + virtual ────────────────────
def start_evsieve_merge():
    if not os.path.exists(REAL_DUALSENSE_PATH):
        print(f"❌ ERROR: {REAL_DUALSENSE_PATH} not found. Connect your real controller!")
        sys.exit(1)
    if not os.path.exists(VIRTUAL_DEVICE_PATH):
        print(f"❌ ERROR: {VIRTUAL_DEVICE_PATH} not found. Virtual controller not created!")
        sys.exit(1)

    cmd = [
        "evsieve",
        "--input", REAL_DUALSENSE_PATH, "grab",
        "--input", VIRTUAL_DEVICE_PATH, "grab",
        "--output", "create-link=" + MERGED_DEVICE_LINK
    ]

    print("[INFO] Starting evsieve to merge controllers...")
    subprocess.Popen(cmd)
    print(f"[INFO] Merged device will appear at {MERGED_DEVICE_LINK}")

start_evsieve_merge()

# ─── Initialize Camera ───────────────────────────────────────
cap = cv2.VideoCapture(0)

# ─── Start Web Server ─────────────────────────────────────────
threading.Thread(target=run_server, daemon=True).start()

# ─── Gesture Detection Loop ───────────────────────────────────
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

threading.Thread(target=gesture_detection_loop, daemon=True).start()

# ─── Emulate Circle Button ────────────────────────────────────
def emulate_circle_press():
    print("[INFO] Emulating CIRCLE press...")
    ui.write(e.EV_KEY, BTN_CIRCLE, 1)  # Press
    ui.syn()
    time.sleep(0.1)
    ui.write(e.EV_KEY, BTN_CIRCLE, 0)  # Release
    ui.syn()
    print("[INFO] Circle Press Complete!")

# ─── Main Loop for Testing ────────────────────────────────────
if __name__ == "__main__" and TEST_MODE:
    while True:
        emulate_circle_press()
        time.sleep(5)
