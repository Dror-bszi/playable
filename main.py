from core.gestures import GestureDetector
from core.mappings import get_button_for_gesture
from web.server import run_server, set_web_status, should_shutdown
from remote.input_bridge import send_button_press
import cv2
import threading
import time

TEST_MODE = True  # Set to False later to disable test loop

cap = cv2.VideoCapture(0)

# Start web server in background
threading.Thread(target=run_server, daemon=True).start()

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
                    send_button_press(button)  # Send button when gesture detected
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

# Test Mode: Press CIRCLE every 5 seconds
if __name__ == "__main__" and TEST_MODE:
    while True:
        print("[INFO] Pressing CIRCLE button...")
        send_button_press("circle")
        time.sleep(5)
