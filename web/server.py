# web/server.py
from flask import Flask, render_template, Response
import threading

app = Flask(__name__)
status = "Waiting..."

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


def run_server():
    app.run(host='0.0.0.0', port=5000)

def set_web_status(message):
    global status
    status = message
