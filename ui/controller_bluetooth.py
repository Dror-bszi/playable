# ui/controller_bluetooth.py
import subprocess
import re
import time

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
                devices.append((mac, name))  # Now include all devices, not only controllers

        return devices if devices else [("N/A", "⚠️ No devices found")]
    except subprocess.TimeoutExpired:
        return [("N/A", "⚠️ Scan timed out")]
    except Exception as e:
        return [("N/A", f"⚠️ Error: {str(e)}")]

def connect_device(mac):
    subprocess.run(f'echo -e "connect {mac}\ntrust {mac}\nexit" | bluetoothctl', shell=True)
    return True
