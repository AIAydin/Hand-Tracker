from .hands import landmarks_px


def count_fingers_up(image, hand_landmarks, hand_label: str):
    """Return (count, states) where states is a dict of finger->bool (up?).

    Heuristics:
    - Index/Middle/Ring/Pinky: tip.y < pip.y (y axis grows downward)
    - Thumb: compare x of tip vs mcp; depends on handedness label ("Left"/"Right")
    """
    pts = landmarks_px(image, hand_landmarks)
    if not pts or len(pts) < 21:
        return 0, {"Thumb": False, "Index": False, "Middle": False, "Ring": False, "Pinky": False}

    hand_label_l = (hand_label or "").lower()

    def is_thumb_up():
        tip_x = pts[4][0]
        mcp_x = pts[2][0]
        if hand_label_l.startswith("right"):
            return tip_x > mcp_x
        if hand_label_l.startswith("left"):
            return tip_x < mcp_x
        # Fallback if label missing: assume right-hand-like orientation
        return tip_x > mcp_x

    def is_finger_up(tip_idx, pip_idx):
        return pts[tip_idx][1] < pts[pip_idx][1]

    states = {
        "Thumb": is_thumb_up(),
        "Index": is_finger_up(8, 6),
        "Middle": is_finger_up(12, 10),
        "Ring": is_finger_up(16, 14),
        "Pinky": is_finger_up(20, 18),
    }
    count = sum(1 for v in states.values() if v)
    return count, states

