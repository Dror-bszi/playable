# ui/controller_bluetooth.py
import subprocess
import re
import time
import os


def scan_devices():
    try:
        process = subprocess.Popen(
            ["bluetoothctl"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        process.stdin.write("scan on\n")
        process.stdin.flush()
        time.sleep(15)  # Increased scan duration

        process.stdin.write("scan off\n")
        process.stdin.write("devices\n")
        process.stdin.write("exit\n")
        process.stdin.flush()

        stdout, stderr = process.communicate(timeout=30)  # Increased timeout
        print("bluetoothctl output:\n", stdout)

        devices = []
        for line in stdout.splitlines():
            print("[DEBUG] LINE:", line)
            match = re.match(r"Device ([0-9A-F:]{17}) (.+)", line)
            if match:
                mac, name = match.groups()
                devices.append((mac, name))

        return devices if devices else []
    except subprocess.TimeoutExpired:
        return []
    except Exception as e:
        return []

def connect_device(mac):
    try:
        script_path = os.path.abspath("utils/pair_controller.expect")
        output = subprocess.check_output(
            ["expect", script_path, mac],
            stderr=subprocess.STDOUT,
            text=True,
            timeout=40
        )
        print("[DEBUG] expect output:", output)
        return "Pairing successful" in output or "Connection successful" in output
    except subprocess.CalledProcessError as e:
        print("[ERROR] Expect script failed:", e.output)
        return False