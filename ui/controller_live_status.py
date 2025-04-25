import threading
from evdev import InputDevice, categorize, ecodes, list_devices

status = {
    "connected": False,
    "device_path": None,
    "buttons": set(),
    "l2": 0,
    "r2": 0,
    "lx": 0,
    "ly": 0,
    "rx": 0,
    "ry": 0,
    "error": None
}

def _monitor_device(dev_path):
    global status
    try:
        dev = InputDevice(dev_path)
        status["connected"] = True
        status["error"] = None

        for event in dev.read_loop():
            try:
                if event.type == ecodes.EV_KEY:
                    key = ecodes.KEY[event.code]
                    if event.value == 1:
                        status["buttons"].add(key)
                    elif event.value == 0:
                        status["buttons"].discard(key)
                elif event.type == ecodes.EV_ABS:
                    code = event.code
                    value = event.value
                    if code == ecodes.ABS_Z:
                        status["l2"] = value
                    elif code == ecodes.ABS_RZ:
                        status["r2"] = value
                    elif code == ecodes.ABS_X:
                        status["lx"] = value
                    elif code == ecodes.ABS_Y:
                        status["ly"] = value
                    elif code == ecodes.ABS_RX:
                        status["rx"] = value
                    elif code == ecodes.ABS_RY:
                        status["ry"] = value
            except Exception as nested_e:
                status["error"] = f"event error: {str(nested_e)}"
    except Exception as e:
        status["connected"] = False
        status["error"] = str(e)

def start_controller_monitor():
    devices = [InputDevice(path) for path in list_devices()]
    for d in devices:
        if 'DualSense Wireless Controller' in d.name and 'Touchpad' not in d.name and 'Motion' not in d.name:
            status["device_path"] = d.path
            threading.Thread(target=_monitor_device, args=(d.path,), daemon=True).start()
            return True
    status["connected"] = False
    status["error"] = "DualSense controller not found"
    return False

def get_status():
    return {
        "connected": status["connected"],
        "device_path": status["device_path"],
        "buttons": list(status["buttons"]),
        "l2": status["l2"],
        "r2": status["r2"],
        "lx": status["lx"],
        "ly": status["ly"],
        "rx": status["rx"],
        "ry": status["ry"],
        "error": status["error"]
    }
