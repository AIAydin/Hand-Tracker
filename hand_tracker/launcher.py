"""
Simple GUI/console launcher to choose a Hand Tracker mode.
- Uses Tkinter if available (no extra deps)
- Falls back to a console prompt otherwise
- Spawns the main app as a subprocess with selected options
"""
from __future__ import annotations
import sys
import subprocess
from typing import List


def _launch(args: List[str]) -> None:
    # Launch the app as a subprocess using the current Python interpreter
    cmd = [sys.executable, "-m", "hand_tracker.app"] + args
    subprocess.Popen(cmd, close_fds=True)


def _console_main() -> None:
    print("Hand Tracker Launcher (console)")
    modes = ["default", "vmouse", "slides", "rps", "reaction"]
    for i, m in enumerate(modes, 1):
        print(f"{i}. {m}")
    try:
        choice = int(input("Choose mode [1-5] (default 1): ") or "1") - 1
    except Exception:
        choice = 0
    choice = max(0, min(choice, len(modes) - 1))
    mode = modes[choice]

    flip = input("Flip mirror? [y/N]: ").strip().lower().startswith("y")
    vm_scroll = False
    if mode == "vmouse":
        vm_scroll = input("Enable scroll with pinch? [y/N]: ").strip().lower().startswith("y")

    args: List[str] = ["--mode", mode]
    if flip:
        args.append("--flip")
    if mode == "vmouse" and vm_scroll:
        args.append("--vm-scroll")

    print("Launching:", "python -m hand_tracker.app", " ".join(args))
    _launch(args)


def main() -> None:
    try:
        import tkinter as tk
        from tkinter import messagebox
    except Exception:
        # Fallback to console prompt if Tk is unavailable
        _console_main()
        return

    root = tk.Tk()
    root.title("Hand Tracker Launcher")
    # Give the window a reasonable size so content is visible immediately
    root.geometry("380x380")
    root.minsize(320, 320)

    mode = tk.StringVar(value="default")
    flip = tk.BooleanVar(value=True)
    vm_scroll = tk.BooleanVar(value=False)

    wrap = tk.Frame(root, padx=12, pady=12)
    wrap.pack(fill="both", expand=True)

    tk.Label(wrap, text="Choose mode:", font=("Helvetica", 13, "bold")).pack(anchor="w")
    modes = ["default", "vmouse", "slides", "rps", "reaction"]
    for m in modes:
        tk.Radiobutton(wrap, text=m, variable=mode, value=m, anchor="w", justify="left").pack(anchor="w")

    tk.Frame(wrap, height=8).pack()
    tk.Checkbutton(wrap, text="Flip mirror (--flip)", variable=flip).pack(anchor="w")

    vmf = tk.LabelFrame(wrap, text="Virtual mouse options")
    vmf.pack(fill="x", pady=(8, 0))
    tk.Checkbutton(vmf, text="Enable scroll (--vm-scroll)", variable=vm_scroll).pack(anchor="w")

    def do_launch() -> None:
        args: List[str] = ["--mode", mode.get()]
        if flip.get():
            args.append("--flip")
        if mode.get() == "vmouse" and vm_scroll.get():
            args.append("--vm-scroll")
        try:
            _launch(args)
            messagebox.showinfo(
                "Launched",
                f"Started: python -m hand_tracker.app {' '.join(args)}\nYou can close this window or launch another.",
            )
        except Exception as e:
            messagebox.showerror("Error launching app", str(e))

    btns = tk.Frame(wrap)
    btns.pack(fill="x", pady=(12, 0))
    tk.Button(btns, text="Launch", command=do_launch).pack(side="left", expand=True, fill="x", padx=(0, 6))
    tk.Button(btns, text="Quit", command=root.destroy).pack(side="left", expand=True, fill="x", padx=(6, 0))

    # Ensure window is realized before showing
    root.update_idletasks()
    root.deiconify()
    root.mainloop()


if __name__ == "__main__":
    main()

