# ui/controller_bluetooth.py
import subprocess
import re


def scan_devices():
    try:
        output = subprocess.check_output(["sudo", "hcitool", "scan"], timeout=10, text=True, stderr=subprocess.STDOUT)
        devices = []
        for line in output.splitlines()[1:]:
            match = re.match(r"([0-9A-F:]{17})\s+(.+)", line)
            if match:
                mac, name = match.groups()
                if "DualSense" in name or "Wireless" in name or "Controller" in name:
                    devices.append((mac, name))
        return devices
    except subprocess.CalledProcessError as e:
        print("Scan failed:", e.output)
        return [("N/A", "⚠️ Scan error")]
    except subprocess.TimeoutExpired:
        return [("N/A", "⚠️ Scan timed out")]

def connect_device(mac):
    """Connects and trusts the given Bluetooth MAC address using bluetoothctl."""
    subprocess.run(f'echo -e "connect {mac}\ntrust {mac}\nexit" | bluetoothctl', shell=True)
    return True
