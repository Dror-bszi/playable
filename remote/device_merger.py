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

def start_device_merging(mapped_buttons):
    global MERGED_DEVICE_PATH

    real_device = find_dualsense_event()
    virtual_device = find_virtual_device()

    if real_device is None:
        return False, "❌ Could not find real DualSense device."

    if virtual_device is None:
        return False, "❌ Could not find virtual controller device."

    output_link = "/dev/input/by-id/merged-playable"

    try:
        # --- Build evsieve command ---
        cmd = [
            "evsieve",
            "--input", real_device, "grab",
            "--input", virtual_device, "grab",
        ]

        # Button names to event code mapping
        button_code_map = {
            "circle": 305,
            "cross": 304,
            "square": 308,
            "triangle": 307,
            "l1": 310,
            "r1": 311,
            "l2": 312,
            "r2": 313,
            "share": 314,
            "options": 315,
            "l3": 317,
            "r3": 318,
            "dpad_up": 544,
            "dpad_down": 545,
            "dpad_left": 546,
            "dpad_right": 547,
        }

        # Add allow rules for real controller buttons
        for button in mapped_buttons:
            code = button_code_map.get(button.lower())
            if code is not None:
                cmd += [
                    "--map",
                    f"input {real_device} type 1 code {code} input {real_device} type 1 code {code}"
                ]

        # Final merged output
        cmd += ["--output", f"create-link={output_link}"]

        # Start evsieve
        subprocess.Popen(cmd)
        print(f"[INFO] Merging {real_device} + {virtual_device} into {output_link} with mapped buttons: {mapped_buttons}")

        # Wait until merged link is created
        for _ in range(10):
            if os.path.exists(output_link):
                MERGED_DEVICE_PATH = output_link
                print(f"[INFO] Merged device ready at {MERGED_DEVICE_PATH}")
                grab_real_device(real_device)
                return True, "✅ Merged successfully with gesture mapping rules."

            time.sleep(0.5)

        return False, "❌ Merged device link was not created."

    except Exception as e:
        return False, f"❌ Error running evsieve: {e}"
