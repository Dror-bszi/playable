import os
import subprocess
import time

# Global variable to store merged device path
MERGED_DEVICE_PATH = None

# Mapping from button names (used in gesture mapping) to Linux KEY codes
BUTTON_TO_KEY = {
    "cross": "KEY_CROSS",
    "circle": "KEY_CIRCLE",
    "triangle": "KEY_TRIANGLE",
    "square": "KEY_SQUARE",
    "l1": "KEY_L",
    "r1": "KEY_R",
    "l2": "KEY_L2",
    "r2": "KEY_R2",
    "share": "KEY_SHARE",
    "options": "KEY_OPTIONS",
    "l3": "KEY_THUMBL",
    "r3": "KEY_THUMBR",
    "dpad_up": "KEY_DPAD_UP",
    "dpad_down": "KEY_DPAD_DOWN",
    "dpad_left": "KEY_DPAD_LEFT",
    "dpad_right": "KEY_DPAD_RIGHT"
}

def find_dualsense_event():
    try:
        base_path = "/dev/input/"
        for device in os.listdir(base_path):
            if device.startswith("event"):
                device_path = os.path.join(base_path, device)
                with open(f"/sys/class/input/{device}/device/name", "r") as f:
                    name = f.read().strip()
                    if "DualSense Wireless Controller" in name and "Touchpad" not in name and "Motion Sensors" not in name:
                        return device_path
    except Exception as e:
        print(f"❌ ERROR finding DualSense event: {e}")
    return None

def find_virtual_device():
    try:
        base_path = "/dev/input/"
        for device in os.listdir(base_path):
            if device.startswith("event"):
                device_path = os.path.join(base_path, device)
                with open(f"/sys/class/input/{device}/device/name", "r") as f:
                    name = f.read().strip()
                    if "py-evdev-uinput" in name:
                        return device_path
    except Exception as e:
        print(f"❌ ERROR finding virtual device: {e}")
    return None

def grab_real_device(real_device_path):
    try:
        subprocess.run(["evtest", "--grab", real_device_path], check=True)
        print(f"[INFO] Grabbed {real_device_path} successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR grabbing {real_device_path}: {e}")

def kill_old_evsieve():
    try:
        subprocess.run(["pkill", "evsieve"], check=True)
        print("[INFO] Old evsieve processes killed.")
    except subprocess.CalledProcessError:
        print("[INFO] No existing evsieve processes running.")

def start_device_merging(blocked_buttons):
    global MERGED_DEVICE_PATH

    real_device = find_dualsense_event()
    virtual_device = find_virtual_device()

    if real_device is None:
        return False, "Could not find real DualSense device."

    if virtual_device is None:
        return False, "Could not find virtual input device."

    output_link = "/dev/input/by-id/merged-playable"

    # Kill old evsieve
    kill_old_evsieve()

    try:
        # Build evsieve command
        cmd = [
            "evsieve",
            "--input", real_device, "grab"
        ]

        # Add block rules
        for btn in blocked_buttons:
            key_name = BUTTON_TO_KEY.get(btn.lower())
            if key_name:
                cmd += ["block", key_name]
            else:
                print(f"[WARN] No mapping for button '{btn}'")

        cmd += ["--input", virtual_device, "grab", "--output", f"create-link={output_link}"]

        subprocess.Popen(cmd)
        print(f"[INFO] Started merging {real_device} + {virtual_device} with blocks into {output_link}")

        # Wait for merged device to appear
        for _ in range(10):
            if os.path.exists(output_link):
                MERGED_DEVICE_PATH = output_link
                print(f"[INFO] Merged controller ready at {MERGED_DEVICE_PATH}")

                grab_real_device(real_device)
                return True, "Merge successful."
            time.sleep(0.5)

        return False, "Merged device link was not created."

    except Exception as e:
        return False, f"Error running evsieve: {e}"
