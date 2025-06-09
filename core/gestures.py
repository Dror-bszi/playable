# core/gestures.py
import mediapipe as mp
import cv2
import time
import numpy as np
from web.server import update_current_elbow_raise

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
        # Use the lightweight model for better performance on Pi Zero 2W
        self.pose = mp.solutions.pose.Pose(
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.reference_points = {}
        self.last_elbow_y = None
        self.last_detection_time = time.time()
        
        # Initialize frame processing optimization
        self.frame_count = 0
        self.process_every_n_frames = 2  # Process every 2nd frame for better performance

    def process_frame(self, frame):
        """Optimize frame processing for AI camera."""
        if frame is None:
            return None
            
        # Convert to RGB (AI camera provides RGB888)
        rgb = frame if frame.shape[2] == 3 else cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Skip frames for better performance
        self.frame_count += 1
        if self.frame_count % self.process_every_n_frames != 0:
            return None
            
        return rgb

    def is_elbow_raised_forward(self, frame, min_interval=0.1):
        """
        Detect fast left elbow *side raise* with optimized processing for AI camera.
        """
        rgb = self.process_frame(frame)
        if rgb is None:
            return False

        pose_results = self.pose.process(rgb)

        if not pose_results.pose_landmarks:
            return False

        landmarks = pose_results.pose_landmarks.landmark
        try:
            shoulder_right = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER]
            shoulder_left = landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER]
            elbow_left = landmarks[mp.solutions.pose.PoseLandmark.LEFT_ELBOW]

            # Calculate shoulder distance for normalization
            shoulder_distance = abs(shoulder_right.x - shoulder_left.x)
            if shoulder_distance < 1e-5:
                return False

            # Normalize based on x movement
            normalized_elbow_x = (elbow_left.x - shoulder_left.x) / shoulder_distance
            update_current_elbow_raise(normalized_elbow_x)

            threshold = get_delta_threshold()
            min_raise = get_min_normalized_raise()

            if self.last_elbow_y is not None:
                delta = normalized_elbow_x - self.last_elbow_y
                now = time.time()

                if (
                    normalized_elbow_x > min_raise and
                    delta >= threshold and
                    (now - self.last_detection_time) >= min_interval
                ):
                    self.last_elbow_y = normalized_elbow_x
                    self.last_detection_time = now
                    return True

            self.last_elbow_y = normalized_elbow_x

        except (AttributeError, IndexError):
            return False

        return False
