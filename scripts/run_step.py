"""Capture the current USB device screen and perform one Galaxy Defense action."""

import argparse
import math
import subprocess
import time

import cv2
import numpy as np

from capture_screen import capture_png
from detect_screen import detect


# Centers in the detector's 466 x 1000 portrait layout.
TARGETS = {
    "three_cards": (82, 525),
    "five_cards": (98, 473),
    "five_cards_draw_again": (233, 473),
    "five_cards_claim": (233, 920),
}


def observe():
    image = cv2.imdecode(np.frombuffer(capture_png(), np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Cannot decode the device screenshot.")
    return detect(image), image.shape


def act(state, shape, dry_run):
    target = TARGETS.get(state)
    if target is None:
        print(f"{state}: no tap")
        return
    height, width = shape[:2]
    x = round(target[0] * width / 466)
    y = round(target[1] * height / 1000)
    if dry_run:
        print(f"{state}: would tap ({x}, {y})")
        return
    subprocess.run(["adb", "-d", "shell", "input", "tap", str(x), str(y)],
                   check=True, timeout=10)
    print(f"{state}: sent tap ({x}, {y})")


def poll(interval, dry_run):
    last_action = None
    wait_frames = 0
    repeats = 0
    round_number = 0
    while True:
        state, shape = observe()
        round_number += 1
        print(f"[poll {round_number}] {state}", flush=True)
        if state not in TARGETS:
            if wait_frames == 0:
                print(f"{state}: no tap")
            wait_frames += 1
            # A single unrecognized animation frame can interrupt a selection.
            if wait_frames >= 2:
                last_action = None
            repeats = 0
        else:
            wait_frames = 0
            # Back-to-back level-ups can present another choice between polls.
            if state == "three_cards" or state != last_action:
                act(state, shape, dry_run)
                last_action = state
                repeats = 0
            else:
                repeats += 1
                if repeats == 3:
                    print(f"{state}: still visible after 3 checks. Check the phone.")
        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="print the planned action only")
    parser.add_argument("--loop", action="store_true", help="poll until Ctrl+C")
    parser.add_argument("--interval", type=float, default=2, help="seconds between checks")
    args = parser.parse_args()
    if not math.isfinite(args.interval) or args.interval <= 0:
        parser.error("--interval must be a finite positive number")
    try:
        if args.loop:
            poll(args.interval, args.dry_run)
        else:
            state, shape = observe()
            act(state, shape, args.dry_run)
    except KeyboardInterrupt:
        print("Stopped.")
    except (OSError, ValueError, subprocess.SubprocessError, cv2.error) as error:
        parser.exit(1, f"Step failed: {error}\n")


if __name__ == "__main__":
    main()
