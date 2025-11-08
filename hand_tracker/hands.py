import cv2
import mediapipe as mp


class HandDetector:
    """MediaPipe Hands wrapper."""

    def __init__(
        self,
        static_image_mode: bool = False,
        max_num_hands: int = 2,
        model_complexity: int = 1,
        detection_confidence: float = 0.5,
        tracking_confidence: float = 0.5,
    ):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            model_complexity=model_complexity,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )

    def process(self, frame_bgr):
        # MediaPipe expects RGB input
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        return self.hands.process(frame_rgb)

    def close(self):
        try:
            self.hands.close()
        except Exception:
            pass


def landmarks_px(image, hand_landmarks):
    """Convert normalized landmarks to integer pixel coordinates.
    Returns list[(x, y)].
    """
    if hand_landmarks is None:
        return []
    h, w = image.shape[:2]
    pts = []
    for lm in hand_landmarks.landmark:
        pts.append((int(lm.x * w), int(lm.y * h)))
    return pts

