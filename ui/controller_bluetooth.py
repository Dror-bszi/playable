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
        time.sleep(5)

        process.stdin.write("scan off\n")
        process.stdin.write("devices\n")
        process.stdin.write("exit\n")
        process.stdin.flush()

        stdout, stderr = process.communicate(timeout=10)
        print("bluetoothctl output:\n", stdout)

        devices = []
        for line in stdout.splitlines():
            print("[DEBUG] LINE:", line)
            match = re.match(r"Device ([0-9A-F:]{17}) (.+)", line)
            if match:
                mac, name = match.groups()
                if any(keyword in name.lower() for keyword in ["dualsense", "wireless", "controller"]):
                    devices.append((mac, name))
        return devices if devices else [("N/A", "⚠️ No relevant controller found")]
    except subprocess.TimeoutExpired:
        return [("N/A", "⚠️ Scan timed out")]
    except Exception as e:
        return [("N/A", f"⚠️ Error: {str(e)}")]

def connect_device(mac):
    subprocess.run(f'echo -e "connect {mac}\ntrust {mac}\nexit" | bluetoothctl', shell=True)
    return True
