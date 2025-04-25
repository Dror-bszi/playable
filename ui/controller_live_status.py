# ui/controller_live_status.py
from evdev import InputDevice, categorize, ecodes, list_devices
import threading

status = {
    "buttons": {},
    "l2_value": 0,
    "r2_value": 0,
    "left_joystick": (0, 0),
    "right_joystick": (0, 0)
}

def find_dualsense():
    for path in list_devices():
        dev = InputDevice(path)
        if "Wireless Controller" in dev.name or "DualSense" in dev.name:
            return dev
    return None

def start_controller_monitor():
    dev = find_dualsense()
    if not dev:
        print("[ERROR] DualSense not found via evdev.")
        return

    def monitor():
        for event in dev.read_loop():
            if event.type == ecodes.EV_KEY:
                key = ecodes.KEY[event.code]
                status["buttons"][key] = bool(event.value)
            elif event.type == ecodes.EV_ABS:
                if event.code == ecodes.ABS_Z:
                    status["l2_value"] = event.value
                elif event.code == ecodes.ABS_RZ:
                    status["r2_value"] = event.value
                elif event.code == ecodes.ABS_X:
                    x = event.value
                    status["left_joystick"] = (x, status["left_joystick"][1])
                elif event.code == ecodes.ABS_Y:
                    y = event.value
                    status["left_joystick"] = (status["left_joystick"][0], y)
                elif event.code == ecodes.ABS_RX:
                    x = event.value
                    status["right_joystick"] = (x, status["right_joystick"][1])
                elif event.code == ecodes.ABS_RY:
                    y = event.value
                    status["right_joystick"] = (status["right_joystick"][0], y)

    thread = threading.Thread(target=monitor, daemon=True)
    thread.start()

def get_status():
    return status
