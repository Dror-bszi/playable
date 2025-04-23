# ui/controller_bluetooth.py
import subprocess
import re


def scan_devices():
    try:
        result = subprocess.run(["sudo", "hcitool", "scan"], capture_output=True, text=True, timeout=10)
        print("Raw stdout:", result.stdout)
        print("Raw stderr:", result.stderr)
        devices = []
        for line in result.stdout.splitlines()[1:]:
            match = re.match(r"([0-9A-F:]{17})\s+(.+)", line)
            if match:
                mac, name = match.groups()
                if "DualSense" in name or "Wireless" in name or "Controller" in name:
                    devices.append((mac, name))
        return devices
    except subprocess.TimeoutExpired:
        print("Scan timed out")
        return []

def connect_device(mac):
    """Connects and trusts the given Bluetooth MAC address using bluetoothctl."""
    subprocess.run(f'echo -e "connect {mac}\ntrust {mac}\nexit" | bluetoothctl', shell=True)
    return True
