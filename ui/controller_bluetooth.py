# ui/controller_bluetooth.py
import subprocess

def scan_devices():
    """Scans for Bluetooth devices using bluetoothctl."""
    output = subprocess.run(['bluetoothctl', 'devices'], capture_output=True, text=True).stdout
    return [line.split(' ', 2)[2] for line in output.splitlines() if 'Controller' in line or 'Wireless' in line]

def connect_device(name):
    """Connects and trusts the selected Bluetooth device."""
    subprocess.run(f'echo -e "connect {name}\ntrust {name}" | bluetoothctl', shell=True)
    return True