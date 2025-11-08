import math
import time
from typing import Optional, Tuple

import cv2

from .hands import landmarks_px
from .overlay import draw_label

# Try optional backends for controlling mouse
try:  # Prefer pyautogui for cross-platform simplicity
    import pyautogui as _pygui  # type: ignore
except Exception:  # pragma: no cover - optional
    _pygui = None

try:
    from pynput.mouse import Controller as _PynputMouse, Button as _MouseButton  # type: ignore
except Exception:  # pragma: no cover - optional
    _PynputMouse = None
    _MouseButton = None


def _distance(a: Tuple[int, int], b: Tuple[int, int]) -> float:
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return math.hypot(dx, dy)


class _LowPass:
    def __init__(self, alpha: float = 0.2):
        self.alpha = max(0.0, min(1.0, float(alpha)))
        self._v: Optional[Tuple[float, float]] = None

    def __call__(self, x: Tuple[float, float]) -> Tuple[float, float]:
        if self._v is None:
            self._v = x
        else:
            ax = self.alpha
            self._v = (self._v[0] + ax * (x[0] - self._v[0]), self._v[1] + ax * (x[1] - self._v[1]))
        return self._v


class VirtualMouse:
    """Virtual mouse controller using hand landmarks.

    - Pointer: index fingertip (id=8)
    - Click: pinch (thumb tip id=4 close to index tip id=8)
    - Optional scroll: change in pinch distance -> mouse wheel

    Works best when the app frame is mirrored (use --flip).
    External libs (optional): pyautogui or pynput. If missing, actions are no-ops with on-screen hints.
    """

    def __init__(
        self,
        screen_size: Optional[Tuple[int, int]] = None,
        pinch_threshold: float = 0.8,
        smoothing: float = 0.25,
        enable_scroll: bool = False,
        scroll_gain: float = 60.0,
    ) -> None:
        # Determine screen size
        self.screen_w, self.screen_h = self._detect_screen_size(screen_size)
        self.alpha = smoothing
        self.filter = _LowPass(alpha=self.alpha)
        self.enable_scroll = enable_scroll
        self.scroll_gain = float(scroll_gain)

        # Pinch handling
        self.pinch_threshold = float(pinch_threshold)  # threshold on normalized (0..1) pinch distance
        self._prev_pinch_norm: Optional[float] = None
        self._pinch_down = False

        # Mouse backend
        self.backend = None
        self._mouse = None
        if _pygui is not None:
            try:
                _pygui.FAILSAFE = False
                self.backend = "pyautogui"
                self._mouse = _pygui
            except Exception:
                pass
        if self.backend is None and _PynputMouse is not None:
            try:
                self._mouse = _PynputMouse()
                self.backend = "pynput"
            except Exception:
                pass

        # Accumulators
        self._scroll_accum = 0.0
        self._last_pos: Optional[Tuple[float, float]] = None

    def _detect_screen_size(self, hint: Optional[Tuple[int, int]]) -> Tuple[int, int]:
        if hint:
            return int(hint[0]), int(hint[1])
        # Try pyautogui
        if _pygui is not None:
            try:
                sz = _pygui.size()
                return int(sz[0]), int(sz[1])
            except Exception:
                pass
        # Fallback common 1080p
        return 1920, 1080

    def _move_cursor(self, x: float, y: float) -> None:
        if self.backend == "pyautogui":
            try:
                self._mouse.moveTo(x, y)
            except Exception:
                pass
        elif self.backend == "pynput":
            try:
                self._mouse.position = (int(x), int(y))
            except Exception:
                pass

    def _mouse_down(self) -> None:
        if self.backend == "pyautogui":
            try:
                self._mouse.mouseDown()
            except Exception:
                pass
        elif self.backend == "pynput":
            try:
                self._mouse.press(_MouseButton.left)
            except Exception:
                pass

    def _mouse_up(self) -> None:
        if self.backend == "pyautogui":
            try:
                self._mouse.mouseUp()
            except Exception:
                pass
        elif self.backend == "pynput":
            try:
                self._mouse.release(_MouseButton.left)
            except Exception:
                pass

    def _scroll(self, dy: int) -> None:
        if dy == 0:
            return
        if self.backend == "pyautogui":
            try:
                self._mouse.scroll(dy)
            except Exception:
                pass
        elif self.backend == "pynput":
            try:
                self._mouse.scroll(0, int(dy))
            except Exception:
                pass

    def _hand_scale(self, pts):
        # Approximate palm width between index MCP (5) and pinky MCP (17)
        try:
            return max(1.0, _distance(pts[5], pts[17]))
        except Exception:
            return 100.0

    def update(self, frame_bgr, results) -> None:
        if not results or not getattr(results, "multi_hand_landmarks", None):
            self._maybe_release()
            return
        # Use first detected hand
        hand_landmarks = results.multi_hand_landmarks[0]
        pts = landmarks_px(frame_bgr, hand_landmarks)
        if not pts or len(pts) < 21:
            self._maybe_release()
            return
        h, w = frame_bgr.shape[:2]

        # Pointer position from index tip
        ix, iy = pts[8]
        sx = int(self.screen_w * (ix / max(1, w)))
        sy = int(self.screen_h * (iy / max(1, h)))
        sx, sy = self.filter((sx, sy))
        self._move_cursor(sx, sy)
        self._last_pos = (sx, sy)

        # Pinch distance normalized by hand scale
        pinch_d = _distance(pts[4], pts[8])
        norm = pinch_d / self._hand_scale(pts)
        if norm < self.pinch_threshold:
            if not self._pinch_down:
                self._mouse_down()
                self._pinch_down = True
        else:
            if self._pinch_down:
                self._mouse_up()
                self._pinch_down = False

        # Optional scroll based on change in normed pinch distance
        if self.enable_scroll and self._prev_pinch_norm is not None:
            delta = norm - self._prev_pinch_norm
            self._scroll_accum += -delta * self.scroll_gain  # widen -> scroll up
            steps = int(self._scroll_accum)
            if steps != 0:
                self._scroll(steps)
                self._scroll_accum -= steps
        self._prev_pinch_norm = norm

        # On-screen hint
        lib = self.backend or "no-op"
        hint = f"VMOUSE[{lib}] pinch<{self.pinch_threshold:.2f} scroll={'on' if self.enable_scroll else 'off'}"
        draw_label(frame_bgr, hint, (10, frame_bgr.shape[0] - 10))

    def _maybe_release(self) -> None:
        if self._pinch_down:
            self._mouse_up()
            self._pinch_down = False
        self._prev_pinch_norm = None

