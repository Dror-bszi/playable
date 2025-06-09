import os
import sys
import time
import threading
import cv2
# --- NEW CAMERA (Picamera2) ---
from picamera2 import Picamera2
import numpy as np
import libcamera

from core.gestures import GestureDetector, default_gestures
from remote.output_bridge import press_button
from web.server import run_server, set_web_status, should_shutdown, update_current_elbow_raise, set_camera_index, set_shared_frame, is_play_mode

# --- Permissions Check ---
if os.geteuid() != 0:
    print("❌ ERROR: This script must be run with sudo -E python3 main.py")
    sys.exit(1)

# --- Globals ---
frame_lock = threading.Lock()
current_frame = None
picam2 = None

# --- Initialize Camera ---
def find_working_camera():
    global picam2
    try:
        # First, check if camera is detected
        print("[INFO] Checking for camera...")
        picam2 = Picamera2()
        
        # List available camera configurations
        print("[INFO] Available camera configurations:")
        for i, config in enumerate(picam2.sensor_modes):
            print(f"  Mode {i}: {config}")
            
        if not picam2.sensor_modes:
            print("❌ ERROR: No camera detected. Please check your camera connection.")
            return None
            
        # Configure for AI camera with optimized settings
        config = picam2.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"},
            lores={"size": (320, 240), "format": "YUV420"},
            encode="main"
        )
        
        # Enable AI camera features
        config["transform"] = libcamera.Transform(hflip=1, vflip=1)  # Flip if needed
        
        # Configure the camera
        picam2.configure(config)
        
        # Start the camera
        picam2.start()
        
        # Verify camera is working
        try:
            test_frame = picam2.capture_array()
            if test_frame is not None:
                print("[INFO] AI Camera initialized successfully.")
                return 0
            else:
                print("❌ ERROR: Camera initialized but failed to capture frame.")
                return None
        except Exception as e:
            print(f"❌ ERROR: Camera initialized but failed to capture: {e}")
            return None
            
    except Exception as e:
        print(f"❌ ERROR: Failed to initialize camera: {e}")
        print("Please check:")
        print("1. Camera is properly connected")
        print("2. Camera is enabled in raspi-config")
        print("3. You have the correct permissions")
        print("4. The camera ribbon cable is properly seated")
        return None

# --- Camera Worker (for Web GUI) ---
def camera_worker():
    print("[INFO] Starting camera worker for web interface...")
    while not should_shutdown():
        try:
            if picam2 is None:
                print("[WARN] Camera not initialized in camera worker")
                time.sleep(1)
                continue
                
            frame = picam2.capture_array()
            if frame is not None:
                # Convert from RGB888 to BGR for OpenCV
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                with frame_lock:
                    set_shared_frame(frame_bgr)
                time.sleep(0.03)  # ~30 FPS
            else:
                print("[WARN] No frame captured")
                time.sleep(0.1)
        except Exception as e:
            print(f"[WARN] Failed to capture frame in camera_worker: {e}")
            time.sleep(0.1)

# Adjustable global thresholds
delta_threshold = 0.05
min_normalized_raise = 0.05

def set_delta_threshold(value):
    global delta_threshold
    delta_threshold = value

def get_delta_threshold():
    return delta_threshold

def set_min_normalized_raise(value):
    global min_normalized_raise
    min_normalized_raise = value

def get_min_normalized_raise():
    return min_normalized_raise

# --- Gesture Detection Loop (Real-Time) ---
def gesture_detection_loop():
    try:
        os.nice(-10)
        print("[INFO] Gesture Detection Thread priority increased (nice -10).")
    except Exception as e:
        print(f"[WARN] Failed to set nice priority: {e}")

    if picam2 is None:
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
    while not ready and retries < 30 and not should_shutdown():
        try:
            frame = picam2.capture_array()
            if frame is not None:
                ready = True
        except Exception:
            retries += 1
            time.sleep(0.1)

    if not ready:
        print("❌ ERROR: Camera not ready after multiple attempts.")
        return

    print("[INFO] Camera ready")

    gesture_active = {gesture: False for gesture in default_gestures}

    while not should_shutdown():
        try:
            frame = picam2.capture_array()
        except Exception as e:
            print(f"[WARN] Failed to read frame: {e}")
            time.sleep(0.01)
            continue

        if frame is None:
            continue
        set_shared_frame(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        
        gesture_name = "left_elbow_raised_forward"
        is_detected = detector.is_elbow_raised_forward(frame)
        button_name = "square"

        if is_detected and not gesture_active.get(gesture_name, False):
            print(f"[GESTURE] {gesture_name} detected! Pressing {button_name}")
            press_button(button_name)
            gesture_active[gesture_name] = True

        elif not is_detected and gesture_active.get(gesture_name, False):
            gesture_active[gesture_name] = False

# --- Main ---
if __name__ == "__main__":
    print("[INFO] Starting PlayAble...")
    
    # Initialize camera
    camera_index = find_working_camera()
    if camera_index is None:
        print("❌ ERROR: Camera initialization failed. Running in UI-only mode.")
    set_camera_index(camera_index)

    # Start Web server
    print("[INFO] Starting web server...")
    threading.Thread(target=run_server, daemon=True).start()

    # Start gesture detection
    print("[INFO] Starting gesture detection...")
    threading.Thread(target=gesture_detection_loop, daemon=True).start()

    # Start camera worker for web interface
    print("[INFO] Starting camera worker...")
    threading.Thread(target=camera_worker, daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] PlayAble shutting down...")
        if picam2 is not None:
            picam2.stop()
