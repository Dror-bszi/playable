# ui/controller_live_status.py
from pydualsense import pydualsense
import threading
import time

status = {
    "buttons": {},
    "l2_value": 0,
    "r2_value": 0,
    "left_joystick": (0, 0),
    "right_joystick": (0, 0)
}

def start_controller_monitor():
    ds = pydualsense()
    ds.init()

    def on_state():
        status["buttons"] = {
            "cross": ds.cross,
            "circle": ds.circle,
            "square": ds.square,
            "triangle": ds.triangle,
            "l1": ds.l1,
            "r1": ds.r1,
            "l2": ds.l2,
            "r2": ds.r2,
            "options": ds.options,
            "share": ds.share
        }
        status["l2_value"] = ds.L2
        status["r2_value"] = ds.R2
        status["left_joystick"] = (ds.LX, ds.LY)
        status["right_joystick"] = (ds.RX, ds.RY)

    ds.setLedOption(pydualsense.LedOption.PulseBlue)
    ds.update += on_state

    thread = threading.Thread(target=ds.listen, daemon=True)
    thread.start()

def get_status():
    return status
