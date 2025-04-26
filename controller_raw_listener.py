# controller_raw_listener.py
from evdev import InputDevice, categorize, list_devices, ecodes
import time

def find_controller():
    devices = [InputDevice(path) for path in list_devices()]
    for device in devices:
        if "DualSense" in device.name or "Wireless Controller" in device.name:
            print(f"[INFO] Found controller at", device.path)
            return device
    print("[ERROR] Controller not found!")
    return None

def controller_raw_listener(device):
    print("[INFO] Listening for raw controller events...")
    for event in device.read_loop():
        if event.type in [ecodes.EV_KEY, ecodes.EV_ABS]:
            print(f"[RAW EVENT] Type={event.type} Code={event.code} Value={event.value}")

if __name__ == "__main__":
    controller = find_controller()
    if controller:
        controller_raw_listener(controller)
