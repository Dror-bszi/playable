import os
import threading
import time
from evdev import InputDevice, ecodes, list_devices
from remote.device_merger import MERGED_DEVICE_PATH

# Global status dictionaries
real_status = {
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

virtual_status = {
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

merged_status = {
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

def _monitor_device(dev_path, status_obj, name):
    try:
        dev = InputDevice(dev_path)
        print(f"[INFO] Monitoring device ({name}): {dev_path}")
        status_obj["connected"] = True
        status_obj["device_path"] = dev_path

        for event in dev.read_loop():
            if event.type == ecodes.EV_KEY:
                try:
                    key = ecodes.KEY[event.code]
                except KeyError:
                    key = f"KEY_{event.code}"

                if event.value == 1:
                    status_obj["buttons"].add(key)
                elif event.value == 0:
                    status_obj["buttons"].discard(key)

            elif event.type == ecodes.EV_ABS:
                code = event.code
                value = event.value

                if code == ecodes.ABS_Z:
                    status_obj["l2"] = value
                elif code == ecodes.ABS_RZ:
                    status_obj["r2"] = value
                elif code == ecodes.ABS_X:
                    status_obj["lx"] = value
                elif code == ecodes.ABS_Y:
                    status_obj["ly"] = value
                elif code == ecodes.ABS_RX:
                    status_obj["rx"] = value
                elif code == ecodes.ABS_RY:
                    status_obj["ry"] = value
                elif code == ecodes.ABS_HAT0X:
                    if value == -1:
                        status_obj["buttons"].add("DPAD_LEFT")
                        status_obj["buttons"].discard("DPAD_RIGHT")
                    elif value == 1:
                        status_obj["buttons"].add("DPAD_RIGHT")
                        status_obj["buttons"].discard("DPAD_LEFT")
                    else:
                        status_obj["buttons"].discard("DPAD_LEFT")
                        status_obj["buttons"].discard("DPAD_RIGHT")
                elif code == ecodes.ABS_HAT0Y:
                    if value == -1:
                        status_obj["buttons"].add("DPAD_UP")
                        status_obj["buttons"].discard("DPAD_DOWN")
                    elif value == 1:
                        status_obj["buttons"].add("DPAD_DOWN")
                        status_obj["buttons"].discard("DPAD_UP")
                    else:
                        status_obj["buttons"].discard("DPAD_UP")
                        status_obj["buttons"].discard("DPAD_DOWN")

    except Exception as e:
        print(f"[ERROR] Monitoring {dev_path} failed: {str(e)}")
        status_obj["connected"] = False
        status_obj["error"] = str(e)

def _wait_for_device(dev_path, status_obj, name):
    for _ in range(20):  # 20 seconds
        if dev_path and os.path.exists(dev_path):
            threading.Thread(target=_monitor_device, args=(dev_path, status_obj, name), daemon=True).start()
            print(f"[INFO] Started monitor thread for {name}: {dev_path}")
            return
        time.sleep(1)
    print(f"[WARN] No {name} found after waiting.")

def start_controller_monitor():
    devices = [InputDevice(path) for path in list_devices()]
    real_found = False
    virtual_found = False

    for dev in devices:
        name = dev.name
        if 'DualSense Wireless Controller' in name and 'Touchpad' not in name and 'Motion' not in name:
            threading.Thread(target=_monitor_device, args=(dev.path, real_status, "Real Controller"), daemon=True).start()
            real_found = True
        elif 'py-evdev-uinput' in name:
            threading.Thread(target=_monitor_device, args=(dev.path, virtual_status, "Virtual Controller"), daemon=True).start()
            virtual_found = True

    if not real_found:
        real_status["connected"] = False
        real_status["error"] = "No real DualSense found."

    if not virtual_found:
        virtual_status["connected"] = False
        virtual_status["error"] = "No virtual device found."

    # Merged controller (wait separately)
    if MERGED_DEVICE_PATH:
        threading.Thread(target=_wait_for_device, args=(MERGED_DEVICE_PATH, merged_status, "Merged Controller"), daemon=True).start()

def get_status():
    return {
        "connected": real_status["connected"],
        "device_path": real_status["device_path"],
        "buttons": list(real_status["buttons"]),
        "l2": real_status["l2"],
        "r2": real_status["r2"],
        "lx": real_status["lx"],
        "ly": real_status["ly"],
        "rx": real_status["rx"],
        "ry": real_status["ry"],
        "error": real_status["error"],
    }

def get_virtual_status():
    return {
        "connected": virtual_status["connected"],
        "device_path": virtual_status["device_path"],
        "buttons": list(virtual_status["buttons"]),
        "l2": virtual_status["l2"],
        "r2": virtual_status["r2"],
        "lx": virtual_status["lx"],
        "ly": virtual_status["ly"],
        "rx": virtual_status["rx"],
        "ry": virtual_status["ry"],
        "error": virtual_status["error"],
    }

def get_merged_status():
    return {
        "connected": merged_status["connected"],
        "device_path": merged_status["device_path"],
        "buttons": list(merged_status["buttons"]),
        "l2": merged_status["l2"],
        "r2": merged_status["r2"],
        "lx": merged_status["lx"],
        "ly": merged_status["ly"],
        "rx": merged_status["rx"],
        "ry": merged_status["ry"],
        "error": merged_status["error"],
    }
