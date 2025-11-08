import random
import time
from typing import Optional

import cv2

from .gestures import count_fingers_up
from .overlay import draw_label


# --- Rock-Paper-Scissors ----------------------------------------------------

class RPSGame:
    """Simple Rock-Paper-Scissors using hand shape.

    Player gesture mapping:
      - Rock: fist (<=1 finger up)
      - Paper: open hand (>=4 fingers up)
      - Scissors: index+middle up only
    """

    SIGNS = ("rock", "paper", "scissors")

    def __init__(self) -> None:
        self.state = "countdown"  # countdown -> show_result -> countdown
        self.round_end: float = 0.0
        self.countdown_end: float = time.time() + 3.0
        self.player: Optional[str] = None
        self.cpu: Optional[str] = None
        self.score_player = 0
        self.score_cpu = 0

    def _recognize(self, frame_bgr, results) -> Optional[str]:
        if not results or not getattr(results, "multi_hand_landmarks", None):
            return None
        hl = results.multi_hand_landmarks[0]
        handed = getattr(results, "multi_handedness", [])
        label = handed[0].classification[0].label if handed else "Hand"
        cnt, st = count_fingers_up(frame_bgr, hl, label)
        if cnt <= 1:
            return "rock"
        if cnt >= 4:
            return "paper"
        if st.get("Index") and st.get("Middle") and not st.get("Ring") and not st.get("Pinky"):
            return "scissors"
        return None

    @staticmethod
    def _winner(a: str, b: str) -> int:
        # returns 1 if a wins, -1 if b wins, 0 tie
        if a == b:
            return 0
        if (a, b) in (("rock", "scissors"), ("scissors", "paper"), ("paper", "rock")):
            return 1
        return -1

    def update(self, frame_bgr, results) -> None:
        h, w = frame_bgr.shape[:2]
        now = time.time()
        if self.state == "countdown":
            secs = max(0, int(self.countdown_end - now) + 1)
            draw_label(frame_bgr, f"RPS: Show rock/paper/scissors in {secs}s", (10, h - 10))
            if now >= self.countdown_end:
                # lock player's gesture
                self.player = self._recognize(frame_bgr, results) or random.choice(self.SIGNS)
                self.cpu = random.choice(self.SIGNS)
                win = self._winner(self.player, self.cpu)
                if win > 0:
                    self.score_player += 1
                elif win < 0:
                    self.score_cpu += 1
                self.round_end = now + 2.0
                self.state = "show_result"
        elif self.state == "show_result":
            msg = f"You: {self.player} | CPU: {self.cpu}  Score {self.score_player}-{self.score_cpu}"
            # big center text
            cv2.putText(
                frame_bgr,
                msg,
                (20, int(h * 0.5)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (50, 220, 50),
                2,
                cv2.LINE_AA,
            )
            if now >= self.round_end:
                self.countdown_end = now + 3.0
                self.state = "countdown"


# --- Reaction Test -----------------------------------------------------------

class ReactionGame:
    """Wait for GO, then close your hand as fast as you can.

    Sequence: get_ready (random 1-3s) -> go (measure time) -> result (2s) -> repeat
    """

    def __init__(self) -> None:
        self.state = "get_ready"
        self.next_at = time.time() + random.uniform(1.0, 3.0)
        self.go_at: Optional[float] = None
        self.reaction: Optional[float] = None
        self.best: Optional[float] = None

    def _is_closed(self, frame_bgr, results) -> bool:
        if not results or not getattr(results, "multi_hand_landmarks", None):
            return False
        hl = results.multi_hand_landmarks[0]
        handed = getattr(results, "multi_handedness", [])
        label = handed[0].classification[0].label if handed else "Hand"
        cnt, _ = count_fingers_up(frame_bgr, hl, label)
        return cnt <= 1

    def update(self, frame_bgr, results) -> None:
        h, w = frame_bgr.shape[:2]
        now = time.time()
        if self.state == "get_ready":
            draw_label(frame_bgr, "Reaction: Wait...", (10, h - 10))
            if now >= self.next_at:
                self.state = "go"
                self.go_at = now
        elif self.state == "go":
            cv2.putText(frame_bgr, "GO!", (int(w * 0.45), int(h * 0.2)), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3, cv2.LINE_AA)
            if self._is_closed(frame_bgr, results):
                rt = now - (self.go_at or now)
                self.reaction = rt
                self.best = min(self.best, rt) if (self.best is not None) else rt
                self.state = "result"
                self.next_at = now + 2.0
        elif self.state == "result":
            txt = f"Reaction: {self.reaction*1000:.0f} ms (best: {self.best*1000:.0f} ms)"
            draw_label(frame_bgr, txt, (10, h - 10))
            if now >= self.next_at:
                self.state = "get_ready"
                self.next_at = now + random.uniform(1.0, 3.0)

