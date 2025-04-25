from flask import Flask, render_template, request, redirect, url_for, Response, jsonify
import threading
import cv2
import time
from ui import controller_bluetooth

app = Flask(__name__)

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

@app.route("/live_input")
def live_input():
    return render_template("controller_status.html")

from evdev import InputDevice, categorize, ecodes, list_devices

@app.route("/controller_status")
def controller_status():
    try:
        devices = [InputDevice(path) for path in list_devices()]
        controller = None
        for d in devices:
            if 'DualSense Wireless Controller' in d.name and 'Touchpad' not in d.name and 'Motion' not in d.name:
                controller = d
                break

        if not controller:
            return jsonify({"connected": False, "error": "No DualSense controller found"})

        # Open the device in non-blocking mode and get basic data
        info = {
            "connected": True,
            "device_path": controller.path,
            "name": controller.name,
            "inputs": []
        }

        # We won't listen in real-time here — just return metadata
        return jsonify(info)

    except Exception as e:
        return jsonify({"connected": False, "error": str(e)})


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
