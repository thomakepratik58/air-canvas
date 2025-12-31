import math


def fingers_up(lm):
    """
    Detect which fingers are extended
    Returns: [thumb, index, middle, ring, pinky]
    """
    if not lm or len(lm) < 21:
        return [False] * 5

    fingers = []

    # Thumb detection (horizontal check for better accuracy)
    # Check if thumb tip is to the right/left of thumb IP joint
    thumb_is_up = lm[4][1] > lm[3][1]  # For right hand
    # For left hand detection, you might need: thumb_is_up = lm[4][1] < lm[3][1]
    fingers.append(thumb_is_up)

    # Index, Middle, Ring, Pinky (vertical check)
    # Finger is up if tip is higher (lower y-value) than PIP joint
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]
    
    for tip, pip in zip(tips, pips):
        # Add some threshold to avoid jitter
        is_up = lm[tip][2] < lm[pip][2] - 10
        fingers.append(is_up)

    return fingers


def distance(p1, p2):
    """Calculate Euclidean distance between two points"""
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])


def is_pinch(lm, threshold=40):
    """
    Detect pinch gesture (thumb and index finger close together)
    """
    if not lm or len(lm) < 9:
        return False

    thumb_tip = lm[4][1:]  # (x, y)
    index_tip = lm[8][1:]  # (x, y)
    
    dist = distance(thumb_tip, index_tip)
    return dist < threshold


def get_finger_distance(lm, finger1_idx=4, finger2_idx=8):
    """
    Get distance between any two finger landmarks
    Useful for dynamic brush sizing
    """
    if not lm or len(lm) <= max(finger1_idx, finger2_idx):
        return 0
    
    p1 = lm[finger1_idx][1:]
    p2 = lm[finger2_idx][1:]
    return distance(p1, p2)


def is_fist(lm):
    """Detect closed fist (all fingers down)"""
    if not lm or len(lm) < 21:
        return False
    
    fingers = fingers_up(lm)
    return not any(fingers)


def is_peace_sign(lm):
    """Detect peace sign (index and middle fingers up, others down)"""
    if not lm or len(lm) < 21:
        return False
    
    fingers = fingers_up(lm)
    return fingers[1] and fingers[2] and not fingers[3] and not fingers[4]


def is_pointing(lm):
    """Detect pointing gesture (only index finger up)"""
    if not lm or len(lm) < 21:
        return False
    
    fingers = fingers_up(lm)
    return fingers[1] and not any([fingers[0], fingers[2], fingers[3], fingers[4]])


def get_palm_center(lm):
    """Get center of palm for positioning"""
    if not lm or len(lm) < 21:
        return None
    
    # Average of key palm points
    palm_points = [0, 5, 9, 13, 17]  # Base of each finger
    avg_x = sum(lm[i][1] for i in palm_points) / len(palm_points)
    avg_y = sum(lm[i][2] for i in palm_points) / len(palm_points)
    
    return (int(avg_x), int(avg_y))


def get_hand_rotation(lm):
    """
    Get approximate hand rotation angle
    Returns angle in degrees
    """
    if not lm or len(lm) < 21:
        return 0
    
    # Use wrist and middle finger base
    wrist = lm[0][1:]
    middle_base = lm[9][1:]
    
    dx = middle_base[0] - wrist[0]
    dy = middle_base[1] - wrist[1]
    
    angle = math.degrees(math.atan2(dy, dx))
    return angle


def is_thumbs_up(lm):
    """Detect thumbs up gesture"""
    if not lm or len(lm) < 21:
        return False
    
    fingers = fingers_up(lm)
    
    # Thumb up, all others down
    # Also check thumb is above wrist
    thumb_above_wrist = lm[4][2] < lm[0][2]
    
    return fingers[0] and not any(fingers[1:]) and thumb_above_wrist


def get_gesture_confidence(lm, gesture_type="point"):
    """
    Return confidence score for a gesture (0-1)
    Useful for filtering out uncertain gestures
    """
    if not lm or len(lm) < 21:
        return 0.0
    
    fingers = fingers_up(lm)
    
    if gesture_type == "point":
        # Only index should be up
        if fingers[1] and not any([fingers[0], fingers[2], fingers[3], fingers[4]]):
            # Check if index is really extended
            index_tip = lm[8][2]
            index_base = lm[5][2]
            extension = abs(index_base - index_tip)
            return min(1.0, extension / 100)
    
    elif gesture_type == "palm":
        # All fingers should be up
        if all(fingers):
            return 1.0
        elif sum(fingers) >= 4:
            return 0.7
    
    return 0.0


def detect_swipe(lm_history, direction="horizontal", threshold=100):
    """
    Detect swipe gestures based on hand movement history
    lm_history: list of recent landmark positions
    direction: "horizontal" or "vertical"
    """
    if not lm_history or len(lm_history) < 2:
        return False
    
    # Use index finger tip for tracking
    first_pos = lm_history[0][8][1:] if lm_history[0] else None
    last_pos = lm_history[-1][8][1:] if lm_history[-1] else None
    
    if not first_pos or not last_pos:
        return False
    
    if direction == "horizontal":
        movement = abs(last_pos[0] - first_pos[0])
    else:  # vertical
        movement = abs(last_pos[1] - first_pos[1])
    
    return movement > threshold