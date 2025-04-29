# core/gestures.py
import mediapipe as mp
import cv2
import time
from web.server import update_current_elbow_raise  # 🛠 Corrected import!

# --- Import thresholds from main.py (or fallback for testing) ---
try:
    from main import get_delta_threshold, get_min_normalized_raise
except ImportError:
    def get_delta_threshold():
        return 0.05
    def get_min_normalized_raise():
        return 0.05

# --- Default Gestures ---
default_gestures = [
    "left_elbow_raised_forward",
    "mouth_open",
    "head_tilt_right",
    "right_elbow_raised_forward",
]

class GestureDetector:
    def __init__(self):
        self.pose = mp.solutions.pose.Pose(model_complexity=0)  # Lightweight model
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
        self.reference_points = {}

        self.last_elbow_y = None
        self.last_detection_time = time.time()

    def calibrate(self, frame):
        """Dummy calibrate (kept for compatibility)."""
        return True

    def is_elbow_raised_forward(self, frame, min_interval=0.1):
        """
        Detect fast left elbow raise based on delta between frames,
        using global adjustable thresholds.
        """
        if frame is None:
            return False

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pose_results = self.pose.process(rgb)

        if not pose_results.pose_landmarks:
            return False

        landmarks = pose_results.pose_landmarks.landmark
        try:
            shoulder_right = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER]
            shoulder_left = landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER]
            elbow_left = landmarks[mp.solutions.pose.PoseLandmark.LEFT_ELBOW]

            shoulder_distance = abs(shoulder_right.x - shoulder_left.x)

            if shoulder_distance < 1e-5:
                return False  # Avoid division by almost zero

            normalized_elbow_y = (shoulder_right.y - elbow_left.y) / shoulder_distance
            update_current_elbow_raise(normalized_elbow_y)  # 🛠 Update live value!

            threshold = get_delta_threshold()
            min_raise = get_min_normalized_raise()

            if self.last_elbow_y is not None:
                delta = normalized_elbow_y - self.last_elbow_y
                now = time.time()

                if (
                    normalized_elbow_y > min_raise and
                    delta >= threshold and
                    (now - self.last_detection_time) >= min_interval
                ):
                    self.last_elbow_y = normalized_elbow_y
                    self.last_detection_time = now
                    return True

            self.last_elbow_y = normalized_elbow_y

        except (AttributeError, IndexError):
            return False

        return False
