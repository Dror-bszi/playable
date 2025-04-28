# core/gestures.py
import mediapipe as mp
import cv2
import time

# --- Default Gestures ---
default_gestures = [
    "left_elbow_raised_forward",
    "mouth_open",
    "head_tilt_right",
    "right_elbow_raised_forward",
]

class GestureDetector:
    def __init__(self):
        self.pose = mp.solutions.pose.Pose(model_complexity=0)  # Faster, lightweight model
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
        self.reference_points = {}

        # For fast movement detection
        self.last_elbow_y = None
        self.last_detection_time = time.time()

    def calibrate(self, frame):
        """Dummy calibrate for compatibility."""
        return True

    def is_elbow_raised_forward(self, frame, threshold=0.10):
        """
        Traditional method: Is the left elbow raised forward (above threshold).
        Normalized by shoulder-to-shoulder distance.
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
                return False  # Avoid division by near-zero

            normalized_raise = (shoulder_right.y - elbow_left.y) / shoulder_distance

            return normalized_raise >= threshold

        except (AttributeError, IndexError):
            return False

    def is_elbow_raised_fast(self, frame, delta_threshold=0.03, min_interval=0.1):
        """
        Fast detection: Detect sudden elbow raise based on frame-to-frame delta.
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
                return False

            normalized_elbow_y = (shoulder_right.y - elbow_left.y) / shoulder_distance

            if self.last_elbow_y is not None:
                delta = normalized_elbow_y - self.last_elbow_y

                now = time.time()
                if delta >= delta_threshold and (now - self.last_detection_time) >= min_interval:
                    self.last_elbow_y = normalized_elbow_y
                    self.last_detection_time = now
                    return True

            self.last_elbow_y = normalized_elbow_y

        except (AttributeError, IndexError):
            return False

        return False
