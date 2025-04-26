# core/mappings.py

# ─── Global Gesture-to-Button Mapping ─────────────────────────────────────────

GESTURE_TO_BUTTON = {
    "left_elbow_raised_forward": None,
    "mouth_open": None,
    "head_tilt_right": None,
    "right_elbow_raised_forward": None,
}

# ─── Functions ────────────────────────────────────────────────────────────────

def get_button_for_gesture(gesture_name):
    """
    Return the button name assigned to a gesture (if any).
    """
    return GESTURE_TO_BUTTON.get(gesture_name)

def set_gesture_mapping(gesture_name, button_name):
    """
    Dynamically map a gesture to a button.
    """
    if gesture_name not in GESTURE_TO_BUTTON:
        return False  # Gesture not known

    GESTURE_TO_BUTTON[gesture_name] = button_name
    return True

def get_all_mappings():
    """
    Return the full mapping dictionary.
    """
    return GESTURE_TO_BUTTON.copy()
