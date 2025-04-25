from flask import Flask, render_template, request, redirect, url_for, Response, jsonify
import threading
import cv2
import time
import os
import logging
from logging.handlers import RotatingFileHandler

from ui import controller_bluetooth
from ui.controller_live_status import start_controller_monitor, get_status

# ─── Logging Configuration ───────────────────────────────
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, "playable_web.log")

handler = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=3)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)

app = Flask(__name__)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)
app.logger.propagate = False  # ⛔️ prevents duplicate or silent logs

werkzeug_logger = logging.getLogger("werkzeug")
werkzeug_logger.setLevel(logging.INFO)
werkzeug_logger.addHandler(handler)
werkzeug_logger.propagate = False

# ─── Start Controller Monitor ─────────────────────────────
start_controller_monitor()

status = "Waiting..."
shutdown_flag = False

# Bluetooth state
devices = []
connected_device = None

@app.route("/")
def dashboard():
    return render_template("index.html", status=status)

@app.route("/controller")
def controller():
    global devices, connected_device
    return render_template("controller.html", devices=devices, connected=connected_device)

@app.route("/controller_status_page")
def controller_status_page():
    return render_template("controller_status.html")

@app.route("/controller_status")
def controller_status_data():
    return jsonify(get_status())

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

@app.route("/video_feed")
def video_feed():
    def generate():
        cap = cv2.VideoCapture(0)
        while True:
            success, frame = cap.read()
            if not success:
                break
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/shutdown")
def shutdown():
    global shutdown_flag
    shutdown_flag = True
    return redirect(url_for('dashboard'))

def run_server():
    app.run(host='0.0.0.0', port=5000)

def set_web_status(message):
    global status
    status = message

def should_shutdown():
    return shutdown_flag
