# ui/controller_bluetooth.py
import subprocess

def scan_devices():
    """Scans for Bluetooth devices using bluetoothctl."""
    output = subprocess.run(['bluetoothctl', 'devices'], capture_output=True, text=True).stdout
    devices = []
    for line in output.splitlines():
        parts = line.split(' ', 2)
        if len(parts) >= 3:
            mac, name = parts[1], parts[2]
            if "Wireless Controller" in name or "Sony" in name:
                devices.append((mac, name))
    return devices

def connect_device(mac):
    """Connects and trusts the given Bluetooth MAC address."""
    subprocess.run(f'echo -e "connect {mac}\ntrust {mac}" | bluetoothctl', shell=True)
    return True