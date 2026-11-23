"""Capture the current USB device screen and perform one Galaxy Defense action."""

import argparse
import subprocess

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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="print the planned action only")
    args = parser.parse_args()
    try:
        image = cv2.imdecode(np.frombuffer(capture_png(), np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("Cannot decode the device screenshot.")
        state = detect(image)
        target = TARGETS.get(state)
        if target is None:
            print(f"{state}: no tap")
            return

        height, width = image.shape[:2]
        x = round(target[0] * width / 466)
        y = round(target[1] * height / 1000)
        if args.dry_run:
            print(f"{state}: would tap ({x}, {y})")
            return
        subprocess.run(["adb", "-d", "shell", "input", "tap", str(x), str(y)],
                       check=True, timeout=10)
        print(f"{state}: sent tap ({x}, {y})")
    except (OSError, ValueError, subprocess.SubprocessError, cv2.error) as error:
        parser.exit(1, f"Step failed: {error}\n")


if __name__ == "__main__":
    main()
