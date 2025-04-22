# core/gestures.py
import mediapipe as mp
import cv2

class GestureDetector:
    def __init__(self):
        self.pose = mp.solutions.pose.Pose()
        self.reference_points = {}  # Stores calibration Z-values

    def calibrate(self, frame):
        """Captures the reference Z position of the left elbow."""
        results = self._process(frame)
        if results and results.pose_landmarks:
            elbow = results.pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_ELBOW]
            self.reference_points["left_elbow_z"] = elbow.z
            return True
        return False

    def is_elbow_raised_forward(self, frame, threshold_cm=0.10):
        """Returns True if the left elbow is raised forward by threshold_cm (~10cm)."""
        results = self._process(frame)
        if results and results.pose_landmarks and "left_elbow_z" in self.reference_points:
            current_z = results.pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_ELBOW].z
            delta = self.reference_points["left_elbow_z"] - current_z
            return delta >= threshold_cm
        return False

    def _process(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return self.pose.process(rgb)