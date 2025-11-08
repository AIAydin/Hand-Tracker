import time
from collections import deque
from typing import Deque, Optional, Tuple

from .gestures import count_fingers_up
from .hands import landmarks_px
from .overlay import draw_label

# Optional keyboard backends
try:
    import pyautogui as _pygui  # type: ignore
except Exception:  # pragma: no cover - optional
    _pygui = None

try:
    from pynput.keyboard import Controller as _KeyCtl, Key as _Key  # type: ignore
except Exception:  # pragma: no cover - optional
    _KeyCtl = None
    _Key = None


class SlideController:
    """Detect two-finger horizontal swipe and send Left/Right arrow keys.

    Gesture: Index + Middle up, Ring + Pinky down. Trigger when horizontal velocity
    and displacement exceed thresholds within a short time window. Cooldown to avoid repeats.
    """

    def __init__(
        self,
        vx_thresh: float = 900.0,  # px/sec
        dx_thresh: float = 120.0,  # px
        window_sec: float = 0.25,
        cooldown_sec: float = 0.8,
    ) -> None:
        self.vx_thresh = float(vx_thresh)
        self.dx_thresh = float(dx_thresh)
        self.window_sec = float(window_sec)
        self.cooldown_sec = float(cooldown_sec)
        self.samples: Deque[Tuple[float, float]] = deque(maxlen=30)  # (t, x)
        self.last_trigger: float = 0.0

        # keyboard backend
        self.backend = None
        self._key = None
        if _pygui is not None:
            self.backend = "pyautogui"
            self._key = _pygui
        elif _KeyCtl is not None:
            self.backend = "pynput"
            self._key = _KeyCtl()

    def _press(self, which: str) -> None:
        if self.backend == "pyautogui":
            try:
                self._key.press(which)
            except Exception:
                pass
        elif self.backend == "pynput":
            try:
                key = getattr(_Key, which)
                self._key.press(key)
                self._key.release(key)
            except Exception:
                pass

    def update(self, frame_bgr, results) -> None:
        h, w = frame_bgr.shape[:2]
        t = time.time()
        # Need hand and gesture state
        if not results or not getattr(results, "multi_hand_landmarks", None):
            self.samples.clear()
            return
        hand_landmarks = results.multi_hand_landmarks[0]
        handed = getattr(results, "multi_handedness", [])
        label = handed[0].classification[0].label if handed else "Hand"
        cnt, states = count_fingers_up(frame_bgr, hand_landmarks, label)

        two_fingers = states.get("Index") and states.get("Middle") and not states.get("Ring") and not states.get("Pinky")
        pts = landmarks_px(frame_bgr, hand_landmarks)
        if not pts:
            self.samples.clear()
            return

        x = float(pts[0][0])  # wrist x
        self.samples.append((t, x))

        # Only consider when gesture held
        if not two_fingers:
            draw_label(frame_bgr, "Slides: show ✌️ and swipe", (10, h - 10))
            return

        # Compute dx and vx in the recent window
        t0 = t - self.window_sec
        xs = [sx for (st, sx) in self.samples if st >= t0]
        ts = [st for (st, sx) in self.samples if st >= t0]
        if len(xs) < 2:
            return
        dx = xs[-1] - xs[0]
        dt = max(1e-3, ts[-1] - ts[0])
        vx = dx / dt

        ready = (t - self.last_trigger) > self.cooldown_sec
        if ready and abs(vx) > self.vx_thresh and abs(dx) > self.dx_thresh:
            direction = "right" if vx > 0 else "left"
            key = "right" if vx > 0 else "left"
            self._press(key)
            self.last_trigger = t
            draw_label(frame_bgr, f"Slides: {direction} ▶", (10, h - 10))
        else:
            draw_label(frame_bgr, f"Slides: hold ✌️, swipe fast (vx={vx:.0f})", (10, h - 10))

