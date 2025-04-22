from core.gestures import GestureDetector
from core.mappings import get_button_for_gesture
from web.server import run_server, set_web_status
import cv2
import threading

cap = cv2.VideoCapture(0)
detector = GestureDetector()

# Start web server in background
threading.Thread(target=run_server, daemon=True).start()

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
    ret, frame = cap.read()
    if not ret:
        continue

    elbow_raised = detector.is_elbow_raised_forward(frame)
    if elbow_raised and not gesture_active:
        button = get_button_for_gesture("elbow_raised")
        if button:
            set_web_status(f"Pressed: {button.upper()}")
        gesture_active = True

    elif not elbow_raised and gesture_active:
        gesture_active = False
        set_web_status("Waiting for gesture...")

    cv2.imshow("Gesture Detection", frame)
    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()