import os
import threading
import time
from evdev import InputDevice, ecodes, list_devices
from remote.device_merger import MERGED_DEVICE_PATH

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
        print(f"[INFO] Monitoring device: {dev_path}")
        status["connected"] = True
        if not status["device_path"]:
            status["device_path"] = dev_path

        for event in dev.read_loop():
            if event.type == ecodes.EV_KEY:
                try:
                    key = ecodes.KEY[event.code]
                except KeyError:
                    key = f"KEY_{event.code}"

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
                elif code == ecodes.ABS_HAT0X:
                    if value == -1:
                        status["buttons"].add("DPAD_LEFT")
                        status["buttons"].discard("DPAD_RIGHT")
                    elif value == 1:
                        status["buttons"].add("DPAD_RIGHT")
                        status["buttons"].discard("DPAD_LEFT")
                    else:
                        status["buttons"].discard("DPAD_LEFT")
                        status["buttons"].discard("DPAD_RIGHT")
                elif code == ecodes.ABS_HAT0Y:
                    if value == -1:
                        status["buttons"].add("DPAD_UP")
                        status["buttons"].discard("DPAD_DOWN")
                    elif value == 1:
                        status["buttons"].add("DPAD_DOWN")
                        status["buttons"].discard("DPAD_UP")
                    else:
                        status["buttons"].discard("DPAD_UP")
                        status["buttons"].discard("DPAD_DOWN")

    except Exception as e:
        print(f"[ERROR] Monitoring {dev_path} failed: {str(e)}")
        status["connected"] = False
        status["error"] = str(e)

def _wait_for_merged_device():
    """
    Wait for the merged device to appear and monitor it.
    """
    global MERGED_DEVICE_PATH
    for _ in range(20):  # Try for 20 seconds
        if MERGED_DEVICE_PATH and os.path.exists(MERGED_DEVICE_PATH):
            threading.Thread(target=_monitor_device, args=(MERGED_DEVICE_PATH,), daemon=True).start()
            print(f"[INFO] Started monitor thread for merged device: {MERGED_DEVICE_PATH}")
            return
        time.sleep(1)
    print("[WARN] No merged controller found after waiting.")

def start_controller_monitor():
    found = False

    # --- Real DualSense
    devices = [InputDevice(path) for path in list_devices()]
    for d in devices:
        if 'DualSense Wireless Controller' in d.name and 'Touchpad' not in d.name and 'Motion' not in d.name:
            threading.Thread(target=_monitor_device, args=(d.path,), daemon=True).start()
            found = True
            print(f"[INFO] Started monitor thread for real DualSense: {d.path}")
            break

    # --- Monitor Merged Device after it appears
    threading.Thread(target=_wait_for_merged_device, daemon=True).start()

    if not found:
        status["connected"] = False
        status["error"] = "No DualSense found"

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
