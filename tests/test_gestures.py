import numpy as np

from hand_tracker.gestures import count_fingers_up


class LM:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class HandLandmarks:
    def __init__(self, pts):
        # pts: list[(x, y)] in normalized coords (0..1)
        self.landmark = [LM(x, y) for (x, y) in pts]


def make_blank(h=480, w=640):
    return np.zeros((h, w, 3), dtype=np.uint8)


def pose_all_down():
    # All fingers down: tips have y > PIP (lower on screen)
    # 21 landmarks; we only care about fingertips and PIP/MCP
    pts = [(0.5, 0.5) for _ in range(21)]
    # Index tip 8 below PIP 6
    pts[6] = (0.5, 0.45)
    pts[8] = (0.5, 0.55)
    # Middle
    pts[10] = (0.55, 0.45)
    pts[12] = (0.55, 0.55)
    # Ring
    pts[14] = (0.6, 0.46)
    pts[16] = (0.6, 0.56)
    # Pinky
    pts[18] = (0.65, 0.47)
    pts[20] = (0.65, 0.57)
    # Thumb tip vs MCP: set tip left of MCP for Right hand => not up
    pts[2] = (0.4, 0.5)   # thumb MCP
    pts[4] = (0.35, 0.5)  # thumb tip (left of MCP)
    return HandLandmarks(pts)


def pose_index_up():
    pts = [(0.5, 0.5) for _ in range(21)]
    # Index up: tip above PIP
    pts[6] = (0.5, 0.55)
    pts[8] = (0.5, 0.35)
    # Others down similar to all_down
    pts[10] = (0.55, 0.45)
    pts[12] = (0.55, 0.55)
    pts[14] = (0.6, 0.46)
    pts[16] = (0.6, 0.56)
    pts[18] = (0.65, 0.47)
    pts[20] = (0.65, 0.57)
    # Thumb down for right hand
    pts[2] = (0.4, 0.5)
    pts[4] = (0.35, 0.5)
    return HandLandmarks(pts)


def pose_right_thumb_up():
    pts = [(0.5, 0.5) for _ in range(21)]
    # Right-hand thumb up => tip.x > mcp.x
    pts[2] = (0.4, 0.5)
    pts[4] = (0.6, 0.5)
    # Others down
    pts[6] = (0.5, 0.45)
    pts[8] = (0.5, 0.55)
    pts[10] = (0.55, 0.45)
    pts[12] = (0.55, 0.55)
    pts[14] = (0.6, 0.46)
    pts[16] = (0.6, 0.56)
    pts[18] = (0.65, 0.47)
    pts[20] = (0.65, 0.57)
    return HandLandmarks(pts)


def test_all_down_counts_zero():
    img = make_blank()
    hl = pose_all_down()
    cnt, states = count_fingers_up(img, hl, "Right")
    assert cnt == 0
    assert all(not v for v in states.values())


def test_index_up_counts_one():
    img = make_blank()
    hl = pose_index_up()
    cnt, states = count_fingers_up(img, hl, "Right")
    assert cnt == 1
    assert states["Index"] is True


def test_right_thumb_up():
    img = make_blank()
    hl = pose_right_thumb_up()
    cnt, states = count_fingers_up(img, hl, "Right")
    assert states["Thumb"] is True
    assert cnt == 1
