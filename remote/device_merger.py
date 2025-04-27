import os
import subprocess
import time

# Global variable to store merged device path
MERGED_DEVICE_PATH = None

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

def start_device_merging():
    global MERGED_DEVICE_PATH

    real_device = find_dualsense_event()
    virtual_device = find_virtual_device()

    if real_device is None:
        print("❌ ERROR: Could not find real DualSense device.")
        return False

    if virtual_device is None:
        print("❌ ERROR: Could not find virtual controller device.")
        return False

    output_link = "/dev/input/by-id/merged-playable"

    try:
        cmd = [
            "evsieve",
            "--input", real_device, "grab", "allow=type:1",
            "--input", virtual_device, "grab",
            "--output", f"create-link={output_link}"
        ]

        subprocess.Popen(cmd)
        print(f"[INFO] Started evsieve merging {real_device} + {virtual_device} into {output_link}")

        for _ in range(10):
            if os.path.exists(output_link):
                MERGED_DEVICE_PATH = output_link
                print(f"[INFO] Merged device ready at {MERGED_DEVICE_PATH}")
                grab_real_device(real_device)
                return True
            time.sleep(0.5)

        print("❌ ERROR: Merged device link was not created.")
        return False

    except Exception as e:
        print(f"❌ ERROR running evsieve: {e}")
        return False
