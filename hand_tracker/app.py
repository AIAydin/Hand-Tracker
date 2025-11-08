import argparse
import time
import cv2

from .camera import Camera
from .hands import HandDetector, landmarks_px
from .overlay import draw_hands, draw_fps, draw_label
from .gestures import count_fingers_up


def build_argparser():
    p = argparse.ArgumentParser(description="Real-time Hand Tracker (MediaPipe + OpenCV)")
    p.add_argument("--camera", type=int, default=0, help="Camera index (default: 0)")
    p.add_argument("--width", type=int, help="Capture width")
    p.add_argument("--height", type=int, help="Capture height")
    p.add_argument("--max-hands", type=int, default=2)
    p.add_argument("--complexity", type=int, default=1, choices=[0, 1, 2])
    p.add_argument("--det", type=float, default=0.5, help="Min detection confidence")
    p.add_argument("--track", type=float, default=0.5, help="Min tracking confidence")
    p.add_argument("--flip", action="store_true", help="Mirror the camera frame")
    p.add_argument("--no-overlay", action="store_true", help="Disable drawing overlays")
    # Modes
    p.add_argument(
        "--mode",
        type=str,
        default="default",
        choices=["default", "vmouse", "slides", "rps", "reaction"],
        help="Run mode: default draw, virtual mouse, slides control, rock-paper-scissors, or reaction test",
    )
    # Virtual mouse options
    p.add_argument("--vm-pinch", type=float, default=0.45, help="Pinch threshold (normed 0..1) to hold click")
    p.add_argument("--vm-smooth", type=float, default=0.25, help="Pointer smoothing alpha (0..1)")
    p.add_argument("--vm-scroll", action="store_true", help="Enable scroll from pinch distance change")
    p.add_argument("--vm-scroll-gain", type=float, default=60.0, help="Scroll sensitivity")
    # Slides options
    p.add_argument("--slides-vx", type=float, default=900.0, help="Swipe velocity threshold (px/s)")
    p.add_argument("--slides-dx", type=float, default=120.0, help="Swipe distance threshold (px)")
    p.add_argument("--slides-window", type=float, default=0.25, help="Swipe time window (s)")
    p.add_argument("--slides-cooldown", type=float, default=0.8, help="Cooldown between triggers (s)")
    return p


def main(argv=None):
    args = build_argparser().parse_args(argv)

    cam = Camera(args.camera, args.width, args.height)
    detector = HandDetector(
        max_num_hands=args.max_hands,
        model_complexity=args.complexity,
        detection_confidence=args.det,
        tracking_confidence=args.track,
    )

    # Initialize mode controllers
    vm = None
    slides = None
    game = None
    if args.mode == "vmouse":
        from .virtual_mouse import VirtualMouse
        vm = VirtualMouse(pinch_threshold=args.vm_pinch, smoothing=args.vm_smooth,
                          enable_scroll=args.vm_scroll, scroll_gain=args.vm_scroll_gain)
    elif args.mode == "slides":
        from .slides import SlideController
        slides = SlideController(vx_thresh=args.slides_vx, dx_thresh=args.slides_dx,
                                 window_sec=args.slides_window, cooldown_sec=args.slides_cooldown)
    elif args.mode == "rps":
        from .games import RPSGame
        game = RPSGame()
    elif args.mode == "reaction":
        from .games import ReactionGame
        game = ReactionGame()

    prev_t = time.time()

    try:
        while True:
            ok, frame = cam.read()
            if not ok:
                # Warm-up retry: some backends return False on the first read
                for _ in range(10):
                    ok, frame = cam.read()
                    if ok:
                        break
                    cv2.waitKey(1)
                    time.sleep(0.05)
                if not ok:
                    print("Failed to read from camera; retrying...")
                    continue
            if args.flip:
                frame = cv2.flip(frame, 1)
            results = detector.process(frame)

            if not args.no_overlay:
                draw_hands(frame, results, draw=True)
                if getattr(results, "multi_hand_landmarks", None):
                    handedness_list = getattr(results, "multi_handedness", [])
                    for hand_landmarks, handedness in zip(results.multi_hand_landmarks, handedness_list):
                        label = (
                            handedness.classification[0].label
                            if handedness and getattr(handedness, "classification", None)
                            else "Hand"
                        )
                        count, _ = count_fingers_up(frame, hand_landmarks, label)
                        pts = landmarks_px(frame, hand_landmarks)
                        if pts:
                            x, y = pts[0]
                            draw_label(frame, f"{label}: {count}", (x, max(20, y - 10)))


            # Mode-specific updates
            if args.mode == "vmouse" and vm is not None:
                vm.update(frame, results)
            elif args.mode == "slides" and slides is not None:
                slides.update(frame, results)
            elif args.mode in ("rps", "reaction") and game is not None:
                game.update(frame, results)

            now = time.time()
            fps = 1.0 / max(1e-6, now - prev_t)
            prev_t = now
            draw_fps(frame, fps)

            cv2.imshow("Hand Tracker", frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (27, ord("q")):
                break
            elif key == ord("h"):
                args.no_overlay = not args.no_overlay

    finally:
        detector.close()
        cam.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

