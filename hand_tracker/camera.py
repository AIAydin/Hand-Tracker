import sys
from typing import Optional
import cv2


class Camera:
    """Simple wrapper around cv2.VideoCapture.

    Uses AVFoundation by default on macOS for better compatibility.
    """

    def __init__(self, index: int = 0, width: Optional[int] = None, height: Optional[int] = None, prefer_avfoundation: bool = True):
        self.index = index

        # Prefer AVFoundation on macOS, fall back to default backend if it fails
        if sys.platform == "darwin" and prefer_avfoundation:
            cap = cv2.VideoCapture(index, cv2.CAP_AVFOUNDATION)
            if not cap.isOpened():
                try:
                    cap.release()
                except Exception:
                    pass
                cap = cv2.VideoCapture(index)
        else:
            cap = cv2.VideoCapture(index)

        self.cap = cap

        if width is not None:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        if height is not None:
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        if not self.cap.isOpened():
            raise RuntimeError(
                (
                    f"Could not open camera {index}. "
                    "If on macOS, ensure 'Python' has Camera access in System Settings "
                    "→ Privacy & Security → Camera, close other apps using the camera, "
                    "or try a different index with --camera 1."
                )
            )

    def read(self):
        """Return (ok, frame)."""
        return self.cap.read()

    def release(self):
        try:
            self.cap.release()
        except Exception:
            pass

