from flask import Flask, render_template, Response, redirect, url_for, request
import threading
import ui.controller_bluetooth as controller_bluetooth

app = Flask(__name__)
status = "Waiting..."
shutdown_flag = False

@app.route("/")
def index():
    return render_template("index.html", status=status)

@app.route("/video_feed")
def video_feed():
    def generate():
        import cv2
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
    return redirect(url_for('index'))

@app.route("/controller")
def controller_page():
    return render_template("controller.html", devices=[], platform=controller_bluetooth.get_platform())

@app.route("/scan_bluetooth", methods=["POST"])
def scan_bluetooth():
    devices = controller_bluetooth.scan_devices()
    if not devices:
        devices = [("N/A", "⚠️ Scan timed out or no controller found")]
    return render_template("controller.html", devices=devices)

@app.route("/connect_bluetooth", methods=["POST"])
def connect_bluetooth():
    device = request.form.get("device")
    controller_bluetooth.connect_device(device)
    devices = controller_bluetooth.scan_devices()  # Re-scan after connect
    return render_template("controller.html", devices=devices, platform=controller_bluetooth.get_platform(), connected=device)

def run_server():
    app.run(host='0.0.0.0', port=5000)

def set_web_status(message):
    global status
    status = message

def should_shutdown():
    return shutdown_flag
