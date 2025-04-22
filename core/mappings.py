# core/mappings.py

def get_button_for_gesture(gesture_name):
    """Maps gesture identifiers to PS controller button strings."""
    gesture_to_button = {
        "elbow_raised": "cross",  # Maps elbow raise to the X button
    }
    return gesture_to_button.get(gesture_name)