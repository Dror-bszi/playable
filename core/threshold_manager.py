# core/threshold_manager.py

delta_threshold = 0.05
min_normalized_raise = 0.05

def set_delta_threshold(value):
    global delta_threshold
    delta_threshold = value

def get_delta_threshold():
    return delta_threshold

def set_min_normalized_raise(value):
    global min_normalized_raise
    min_normalized_raise = value

def get_min_normalized_raise():
    return min_normalized_raise
