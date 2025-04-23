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
                devices.append((mac, name))

        return devices if devices else []
    except subprocess.TimeoutExpired:
        return []
    except Exception as e:
        return []

def connect_device(mac):
    result = subprocess.run(
        f'echo -e "connect {mac}\ntrust {mac}\nexit" | bluetoothctl',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    print("[DEBUG] connect_device output:", result.stdout)
    return "Connection successful" in result.stdout or "Connection successful" in result.stderr