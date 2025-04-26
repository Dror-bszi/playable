import socket
import time

# Mapping from button names to Chiaki button codes
BUTTON_CODES = {
    "cross": 0x02,
    "circle": 0x03,
    "square": 0x00,
    "triangle": 0x01,
    "l1": 0x04,
    "r1": 0x05,
    "l2": 0x06,
    "r2": 0x07,
    "options": 0x0C,
    "share": 0x0D,
    "dpad_up": 0x10,
    "dpad_down": 0x11,
    "dpad_left": 0x12,
    "dpad_right": 0x13,
    # Add more if needed
}

HOST = "127.0.0.1"  # Chiaki server is running locally
PORT = 9867         # Default Chiaki input server port

def send_button_press(button_name):
    """
    Sends a button press + release to Chiaki/PS5.
    """
    button_code = BUTTON_CODES.get(button_name.lower())
    if button_code is None:
        print(f"[ERROR] Unknown button: {button_name}")
        return

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            # Press
            s.sendall(bytes([0x01, button_code, 0x01]))
            time.sleep(0.1)  # Press time
            # Release
            s.sendall(bytes([0x01, button_code, 0x00]))
        print(f"[INFO] Sent button: {button_name.upper()}")
    except Exception as e:
        print(f"[ERROR] Failed to send button {button_name}: {e}")
