# Hand Tracker (MediaPipe + OpenCV)

[![CI](https://github.com/AIAydin/Hand-Tracker-Finger-Counter/actions/workflows/ci.yml/badge.svg)](https://github.com/AIAydin/Hand-Tracker-Finger-Counter/actions/workflows/ci.yml)


A simple, modular hand tracker that uses your computer's camera in real time. It detects hand landmarks using Google's MediaPipe and overlays them on the live video feed with OpenCV.

## Features
- Real-time hand landmark tracking (up to 2 hands)
- Overlay of hand skeleton and FPS
- Configurable camera index, resolution, model complexity, and confidences
- Optional horizontal flip for a mirrored view
- Lightweight, modular code organized by feature:
  - `hand_tracker/camera.py` (camera capture)
  - `hand_tracker/hands.py` (hand detection)
  - `hand_tracker/overlay.py` (drawing overlays)
  - `hand_tracker/app.py` (CLI entrypoint)

## Requirements
- Python 3.9+
- See pinned runtime dependencies in `requirements.txt`

## Install
- From source (packaged):
  ```bash
  pip install .           # base runtime
  pip install .[os-control]  # optional: OS mouse/keyboard backends (pyautogui + pynput)
  # for contributors (tests, lint):
  pip install -e .[dev]
  ```
- Or using requirements.txt (development):
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
  pip install --upgrade pip
  pip install -r requirements.txt
  ```

## Run
GUI launcher:
```bash
hand-tracker         # installed entry point
# or
python -m hand_tracker  # choose a mode
```

Direct CLI:
```bash
hand-tracker-app --mode default --flip --width 640 --height 480
# or python -m hand_tracker.app --mode default --flip --width 640 --height 480
```

### Common options
- `--camera 0`       Camera device index (0 is default). Use `--camera 1` if you have multiple cameras.
- `--width 1280`     Capture width (try 640x480 for lower latency)
- `--height 720`     Capture height
- `--max-hands 2`    Max hands to detect
- `--complexity 0`   Model complexity (0/1/2). Use 0 for speed.
- `--det 0.5`        Min detection confidence
- `--track 0.5`      Min tracking confidence
- `--flip`           Mirror the frame (preferred for selfies)
- `--no-overlay`     Disable drawing landmarks


### Modes (new)
- Virtual mouse: move cursor with your index fingertip, pinch to click, optional scroll by changing pinch distance.
  - Run: `hand-tracker-app --mode vmouse --flip --vm-scroll`
  - Optional deps: install extras: `pip install .[os-control]` (pyautogui + pynput). On macOS, grant Accessibility permission to your Terminal/IDE and Python.
- Slides control: two-finger (✌️) swipe left/right to send arrow keys for slides/media.
  - Run: `hand-tracker-app --mode slides --flip`
  - Optional deps: install extras: `pip install .[os-control]`.
- Mini‑games:
  - Rock‑Paper‑Scissors: `hand-tracker-app --mode rps`
  - Reaction test (close fist on GO): `hand-tracker-app --mode reaction`

Keyboard shortcuts while running:
- `q` or `Esc` to quit
- `h` to toggle overlay on/off

## Safety & privacy
- This app processes your camera frames locally only; it does not send images or data to external services.
- Grant Camera permission to your Terminal/IDE and Python runtime on macOS.
- Not intended for safety-critical or medical use.

## Contributing & conduct
- See CONTRIBUTING.md for development/PR guidelines
- See CODE_OF_CONDUCT.md for community standards
- See SECURITY.md for responsible disclosure

## License
MIT (see LICENSE)

## Troubleshooting
- macOS: Allow Terminal (or your IDE) camera access in System Settings > Privacy & Security > Camera.
- If the window is blank or slow, try `--width 640 --height 480` and set `--complexity 0`.
- If you have multiple webcams, try `--camera 1` (or 2, etc.).

