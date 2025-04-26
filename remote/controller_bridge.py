import subprocess
import sys
from evdev import UInput, ecodes as e
import time

BTN_CIRCLE = 305
# Global variable to store merged device path
MERGED_DEVICE_PATH = None


import os
import subprocess
import time

# Global variable to store merged device path
MERGED_DEVICE_PATH = None

import os
import subprocess
import time

# Global variable to store merged device path
MERGED_DEVICE_PATH = None

def find_dualsense_event():
    """
    Automatically find the correct DualSense event.
    Ignore touchpad and motion sensors.
    """
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
    """
    Find the virtual controller created (uinput device).
    """
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

def start_evsieve_merge():
    """
    Merge real DualSense + Virtual Device.
    Grab real DualSense to block direct communication.
    Save output link to MERGED_DEVICE_PATH.
    """
    global MERGED_DEVICE_PATH

    real_device = find_dualsense_event()
    virtual_device = find_virtual_device()

    if real_device is None:
        print("❌ ERROR: Could not find real DualSense device.")
        return False

    if virtual_device is None:
        print("❌ ERROR: Could not find virtual input device.")
        return False

    output_link = "/dev/input/by-id/merged-playable"

    # Start evsieve
    try:
        cmd = [
            "evsieve",
            "--input", real_device, "grab",
            "--input", virtual_device, "grab",
            "--output", f"create-link={output_link}"
        ]
        subprocess.Popen(cmd)
        print(f"[INFO] Started evsieve merging {real_device} + {virtual_device} into {output_link}")

        # Wait for link to be created
        for _ in range(10):
            if os.path.exists(output_link):
                MERGED_DEVICE_PATH = output_link
                print(f"[INFO] Merged controller available at {MERGED_DEVICE_PATH}")

                # ⚡ After successful merge: Grab real DualSense manually too
                grab_real_device(real_device)
                return True

        print("❌ ERROR: Merged device link was not created.")
        return False

    except Exception as e:
        print(f"❌ ERROR starting evsieve: {e}")
        return False

def grab_real_device(real_device_path):
    """
    Grab the real DualSense device to block any other process from using it.
    """
    try:
        subprocess.run(["evtest", "--grab", real_device_path], check=True)
        print(f"[INFO] Grabbed {real_device_path} successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: Failed to grab {real_device_path}: {e}")



# ─── Load UInput Kernel Module ───────────────────────────────
def load_uinput_module():
    try:
        subprocess.run(["modprobe", "uinput"], check=True)
        print("[INFO] uinput kernel module loaded successfully!")
    except subprocess.CalledProcessError:
        print("❌ ERROR: Failed to load uinput module!")
        sys.exit(1)

# ─── Create Virtual Controller ───────────────────────────────
def create_virtual_controller():
    capabilities = {
        e.EV_KEY: [BTN_CIRCLE],
    }
    ui = UInput(capabilities)
    print("[INFO] Virtual controller created.")
    time.sleep(1)
    return ui

# ─── Emulate Circle Button ───────────────────────────────────
def emulate_circle_press():
    global ui
    print("[INFO] Emulating CIRCLE press...")
    ui.write(e.EV_KEY, BTN_CIRCLE, 1)
    ui.syn()
    time.sleep(0.1)
    ui.write(e.EV_KEY, BTN_CIRCLE, 0)
    ui.syn()
    print("[INFO] Circle Press Complete!")

# Initialize once when importing
load_uinput_module()
ui = create_virtual_controller()
