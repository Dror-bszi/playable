import time
from remote.controller_bridge import ui

# --- Button Codes Mapping ---
BUTTON_MAPPING = {
    "circle": 305,
    "cross": 304,
    "square": 308,
    "triangle": 307,
    "l1": 310,
    "r1": 311,
    "l2": 312,
    "r2": 313,
    "share": 314,
    "options": 315,
    "l3": 317,
    "r3": 318,
    "dpad_up": 544,
    "dpad_down": 545,
    "dpad_left": 546,
    "dpad_right": 547,
}

# --- Function to Press Button ---
def press_button(button_name, hold_time=0.01):
    button_code = BUTTON_MAPPING.get(button_name.lower())
    if button_code is None:
        print(f"❌ ERROR: Unknown button name: {button_name}")
        return

    print(f"[INFO] Emulating {button_name.upper()} press...")
    ui.write(1, button_code, 1)
    ui.syn()
    time.sleep(hold_time)
    ui.write(1, button_code, 0)
    ui.syn()
    print(f"[INFO] {button_name.upper()} Press Complete!")
