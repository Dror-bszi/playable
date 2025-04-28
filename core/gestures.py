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
        face_results = self.face_mesh.process(rgb)

        success = False

        if pose_results.pose_landmarks:
            elbow = pose_results.pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_ELBOW]
            nose = pose_results.pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.NOSE]
            self.reference_points["left_elbow_y"] = elbow.y
            self.reference_points["nose_x"] = nose.x
            success = True

        if face_results.multi_face_landmarks:
            landmarks = face_results.multi_face_landmarks[0].landmark
            top_lip = landmarks[13]  # Upper lip center
            bottom_lip = landmarks[14]  # Lower lip center
            initial_mouth_distance = abs(top_lip.y - bottom_lip.y)
            self.reference_points["mouth_open_dist"] = initial_mouth_distance
            success = True

        return success

    def is_elbow_raised_forward(self, frame, threshold=0.10):
        """Detects if left elbow is raised forward."""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pose_results = self.pose.process(rgb)

        if pose_results.pose_landmarks and "left_elbow_y" in self.reference_points:
            current_y = pose_results.pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_ELBOW].y
            delta = self.reference_points["left_elbow_y"] - current_y
            return delta >= threshold
        return False

    def is_mouth_open(self, frame, threshold=0.05):
        """Detects if mouth is open."""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_results = self.face_mesh.process(rgb)

        if face_results.multi_face_landmarks and "mouth_open_dist" in self.reference_points:
            landmarks = face_results.multi_face_landmarks[0].landmark
            top_lip = landmarks[13]
            bottom_lip = landmarks[14]
            current_distance = abs(top_lip.y - bottom_lip.y)
            delta = current_distance - self.reference_points["mouth_open_dist"]
            return delta >= threshold
        return False

    def is_head_tilted_right(self, frame, threshold=0.1):
        """Detects if head tilted to the right."""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pose_results = self.pose.process(rgb)

        if pose_results.pose_landmarks and "nose_x" in self.reference_points:
            current_x = pose_results.pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.NOSE].x
            delta = current_x - self.reference_points["nose_x"]
            return delta >= threshold
        return False
