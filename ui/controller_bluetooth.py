# ui/controller_bluetooth.py
import subprocess
import re

def scan_devices():
    """Scans for Bluetooth devices using hcitool."""
    try:
        output = subprocess.check_output(["hcitool", "scan"], timeout=10, text=True)
        devices = []
        for line in output.splitlines()[1:]:  # Skip header
            match = re.match(r"([0-9A-F:]{17})\s+(.+)", line)
            if match:
                mac, name = match.groups()
                if "DualSense" in name or "Wireless" in name or "Controller" in name:
                    devices.append((mac, name))
        return devices
    except subprocess.TimeoutExpired:
        return []

def connect_device(mac):
    """Connects and trusts the given Bluetooth MAC address using bluetoothctl."""
    subprocess.run(f'echo -e "connect {mac}\ntrust {mac}" | bluetoothctl', shell=True)
    return True
