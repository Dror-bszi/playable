# core/gestures.py
import mediapipe as mp
import cv2

# --- Default Gestures ---
default_gestures = [
    "left_elbow_raised_forward",
    "mouth_open",
    "head_tilt_right",
    "right_elbow_raised_forward",
]

class GestureDetector:
    def __init__(self):
        self.pose = mp.solutions.pose.Pose()
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
        self.reference_points = {}

    def calibrate(self, frame):
        """Calibrates the reference points for all gestures."""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pose_results = self.pose.process(rgb)
        success = False                        
        success = True

        return success

    def is_elbow_raised_forward(self, frame, threshold=0.10):
        "Detects if right elbow is raised forward, normalized to shoulder distance."
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pose_results = self.pose.process(rgb)

        if pose_results.pose_landmarks:
            landmarks = pose_results.pose_landmarks.landmark
            # Get shoulders and elbow
            shoulder_right = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER]
            shoulder_left = landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER]
            elbow_left = landmarks[mp.solutions.pose.PoseLandmark.LEFT_ELBOW]

            # Calculate shoulder-to-shoulder distance (scale reference)
            shoulder_distance = abs(shoulder_right.x - shoulder_left.x)

            if shoulder_distance > 0:
                normalized_raise = (shoulder_right.y - elbow_left.y) / shoulder_distance
                return normalized_raise >= threshold
            else:
                return False

        return False
