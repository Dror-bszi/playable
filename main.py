from core.gestures import GestureDetector
from core.mappings import get_button_for_gesture
from ui.visualizer import ButtonVisualizer
import cv2

cap = cv2.VideoCapture(0)
detector = GestureDetector()
ui = ButtonVisualizer()

ui.set_status("Calibrate: Hold rest position...")
while True:
    ret, frame = cap.read()
    if not ret:
        continue
    if detector.calibrate(frame):
        ui.set_status("Calibration complete!")
        break

gesture_active = False
ui.set_status("Start gesture detection")

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    elbow_raised = detector.is_elbow_raised_forward(frame)
    if elbow_raised and not gesture_active:
        button = get_button_for_gesture("elbow_raised")
        if button:
            ui.set_button(button)
        gesture_active = True

    elif not elbow_raised and gesture_active:
        gesture_active = False
        ui.set_status("Waiting for gesture...")

    cv2.imshow("Gesture Detection", frame)
    ui.update()

    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
ui.close()