import os
import sys
import time
import cv2
import threading

from core.gestures import GestureDetector, default_gestures
from remote.output_bridge import press_button
from web.server import run_server, set_web_status, should_shutdown, gesture_mappings, set_camera_index, set_shared_frame, is_play_mode

# --- Permissions Check ---
if os.geteuid() != 0:
    print("❌ ERROR: This script must be run with sudo -E python3 main.py")
    sys.exit(1)

# --- Globals ---
frame_lock = threading.Lock()
current_frame = None
cap = None

# --- Initialize Camera ---
def find_working_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ ERROR: No working camera found.")
        return None, None

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print(f"[INFO] Camera opened at resolution: {int(actual_width)}x{int(actual_height)}")

    return cap, 0

# --- Camera Worker (for Web GUI) ---
def camera_worker():
    global cap
    while not should_shutdown():
        if cap is not None:
            ret, frame = cap.read()
            if ret:
                with frame_lock:
                    set_shared_frame(frame.copy())  # only for Web
        else:
            time.sleep(1)

# --- Gesture Detection Loop (Real-Time) ---
def gesture_detection_loop():
    global cap
    if cap is None:
        set_web_status("❌ No camera available. Running in UI-only mode.")
        while not should_shutdown():
            time.sleep(1)
        return

    print("[INFO] Starting gesture detection...")
    detector = GestureDetector()

    # --- WAIT FOR CAMERA TO BECOME READY ---
    print("[INFO] Waiting for camera to become ready...")
    ready = False
    retries = 0
    while not ready and retries < 30 and not should_shutdown():  # wait up to ~3 seconds
        ret, frame = cap.read()
        if ret and frame is not None:
            ready = True
        else:
            retries += 1
            time.sleep(0.1)

    if not ready:
        print("❌ ERROR: Camera not ready after multiple attempts.")
        return

    print("[INFO] Camera ready")

    gesture_active = {gesture: False for gesture in default_gestures}

    while not should_shutdown():
        ret, frame = cap.read()
        if not ret or frame is None:
            print("[WARN] Failed to read frame.")
            time.sleep(0.5)
            continue

        gesture_name = "left_elbow_raised_forward"
        is_detected = detector.is_elbow_raised_forward(frame)
        button_name = "circle"

        if is_detected and not gesture_active.get(gesture_name, False):
            print(f"[GESTURE] {gesture_name} detected! Pressing {button_name}")
            set_web_status(f"Pressed: {button_name.upper()}")
            press_button(button_name)
            gesture_active[gesture_name] = True

        elif not is_detected and gesture_active.get(gesture_name, False):
            gesture_active[gesture_name] = False
            set_web_status("Waiting for gesture...")

# --- Main ---
if __name__ == "__main__":
    cap, camera_index = find_working_camera()
    set_camera_index(camera_index)

        # Start Web server first
    threading.Thread(target=run_server, daemon=True).start()

    # Always start Gesture Detection (needed in both modes)
    threading.Thread(target=gesture_detection_loop, daemon=True).start()

    # Start extra threads only if not in Play Mode
    
    #threading.Thread(target=camera_worker, daemon=True).start()
        # (In future: also start other non-critical threads here)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] PlayAble shutting down...")
        if cap is not None:
            cap.release()
        cv2.destroyAllWindows()
