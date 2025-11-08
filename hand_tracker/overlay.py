import cv2
import mediapipe as mp
from typing import Tuple


mp_drawing = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands


def draw_hands(image, results, draw: bool = True):
    if not draw or results is None or not getattr(results, "multi_hand_landmarks", None):
        return image
    for hand_landmarks in results.multi_hand_landmarks:
        mp_drawing.draw_landmarks(
            image,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_styles.get_default_hand_landmarks_style(),
            mp_styles.get_default_hand_connections_style(),
        )
    return image


def draw_fps(image, fps: float):
    cv2.putText(
        image,
        f"FPS: {fps:.1f}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2,
        cv2.LINE_AA,
    )




def draw_label(image, text: str, origin: Tuple[int, int], bg=(0, 0, 0), fg=(255, 255, 255)):
    """Draw a small label box with text at the given (x, y) origin (baseline origin)."""
    x, y = origin
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.6
    thickness = 2
    (w, h), baseline = cv2.getTextSize(text, font, scale, thickness)
    pad = 6
    top_left = (max(0, x), max(0, y - h - pad * 2))
    bottom_right = (max(0, x) + w + pad * 2, max(0, y + baseline + pad // 2))
    cv2.rectangle(image, top_left, bottom_right, bg, -1)
    cv2.putText(image, text, (x + pad, y - pad), font, scale, fg, thickness, cv2.LINE_AA)
    return image
