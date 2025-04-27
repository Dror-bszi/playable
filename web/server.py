from flask import Flask, render_template, request, redirect, url_for, Response, jsonify
import threading
import cv2
import time
import os
import logging
import subprocess
from logging.handlers import RotatingFileHandler
from remote.device_merger import start_device_merging
from ui import controller_bluetooth
from ui.controller_live_status import start_controller_monitor, get_status

# ─── Create Flask App Immediately ───────────────────────────
app = Flask(__name__)

# ─── Global Variables ───────────────────────────────────────
camera_index = 0  # Default fallback
status = "Waiting..."
shutdown_flag = False
devices = []
connected_device = None
gesture_mappings = {}

gesture_mappings["circle"] = "mouth_open"
print("[SETUP] Hardcoded mapping: circle ➔ mouth_open")

# ─── Setter Functions ───────────────────────────────────────
def set_camera_index(index):
    global camera_index
    camera_index = index

def set_web_status(message):
    global status
    status = message

def should_shutdown():
    return shutdown_flag

# ─── Logging Configuration ──────────────────────────────────
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, "playable_web.log")

handler = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=3)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)

app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)
app.logger.propagate = False

werkzeug_logger = logging.getLogger("werkzeug")
werkzeug_logger.setLevel(logging.INFO)
werkzeug_logger.addHandler(handler)
werkzeug_logger.propagate = False

# ─── Start Controller Monitor ───────────────────────────────
start_controller_monitor()

# ─── Web Routes ─────────────────────────────────────────────

@app.route("/")
def dashboard():
    return render_template("index.html", status=status)

@app.route("/video_feed")
def video_feed():
    def generate():
        cap = cv2.VideoCapture(camera_index)
        while True:
            success, frame = cap.read()
            if not success:
                break
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        cap.release()
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/controller")
def controller():
    return render_template("controller.html", devices=devices, connected=connected_device)

@app.route("/controller_status_page")
def controller_status_page():
    return render_template("controller_status.html")

@app.route("/controller_status")
def controller_status_data():
    return jsonify(get_status())

@app.route("/save_mapping", methods=["POST"])
def save_mapping():
    global gesture_mappings
    data = request.get_json()
    button = data.get("button")
    gesture = data.get("gesture")
    if button and gesture:
        gesture_mappings[button] = gesture
        print(f"[MAPPING] Saved: {button} mapped to {gesture}")
        return "OK", 200
    return "Bad Request", 400


@app.route("/controller_mapping")
def controller_mapping():
    return render_template("mapping.html")

@app.route("/scan_bluetooth", methods=["POST"])
def scan():
    global devices
    devices = controller_bluetooth.scan_devices()
    return redirect("/controller")

@app.route("/connect_bluetooth", methods=["POST"])
def connect():
    global connected_device
    mac = request.form.get("device")
    success = controller_bluetooth.connect_device(mac)
    connected_device = mac if success else None
    return redirect("/controller")

@app.route("/shutdown", methods=["POST"])
def shutdown():
    global shutdown_flag
    shutdown_flag = True
    return redirect(url_for('dashboard'))

@app.route("/start_merge", methods=["POST"])
def start_merge():
    try:
        # Find all buttons that have gestures mapped
        mapped_buttons = list(gesture_mappings.keys())

        success, message = start_device_merging(mapped_buttons)
        if success:
            set_web_status("✅ Merge completed successfully!")
        else:
            set_web_status(f"❌ Merge failed: {message}")
    except Exception as e:
        set_web_status(f"❌ Error: {str(e)}")

    return redirect(url_for('dashboard'))

@app.route("/chiaki_connect")
def chiaki_connect():
    return render_template("chiaki_connect.html")

@app.route("/start_chiaki", methods=["POST"])
def start_chiaki():
    ps5_ip = request.form.get("ps5_ip")
    psn_id = request.form.get("psn_id")
    pin = request.form.get("pin")

    if not all([ps5_ip, psn_id, pin]):
        return "❌ Missing data. Please fill all fields."

    try:
        cmd = [
            "chiaki",
            "--host", ps5_ip,
            "--psn-account-id", psn_id,
            "--pin", pin
        ]
        subprocess.Popen(cmd)
        return "✅ Chiaki started! You can go back to the dashboard."
    except Exception as e:
        return f"❌ Error starting Chiaki: {str(e)}"
    

# ─── Run Server ─────────────────────────────────────────────
def run_server():

    app.run(host='0.0.0.0', port=5000)

