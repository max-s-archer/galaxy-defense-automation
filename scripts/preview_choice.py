"""Preview a three-card choice from a screenshot or a single live USB frame."""

import argparse
import subprocess
from pathlib import Path

import cv2
import numpy as np

from capture_screen import capture_png
from detect_screen import detect


PRIORITY = ("purple", "combo", "chain", "ordinary")


def classify_cards(image):
    frame = cv2.resize(image, (466, 1000), interpolation=cv2.INTER_AREA)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    teal = cv2.inRange(hsv, (75, 50, 45), (105, 255, 255))
    purple = cv2.inRange(hsv, (118, 45, 45), (155, 255, 255))

    def coverage(region):
        return cv2.countNonZero(region) / region.size

    def classify(x):
        # Read the title band, not the weapon illustration.
        title = np.s_[426:449, x-50:x+50]
        if coverage(purple[title]) > 0.6:
            return "purple"
        if coverage(teal[title]) < 0.6:
            return "unknown"

        badge = coverage(teal[652:665, x-42:x+42])
        if badge < 0.15:
            return "ordinary"
        if badge < 0.65:
            return "unknown"

        # Combo and chain badges are similar. Only the combo has two weapon tiles.
        tiles = [coverage(teal[679:717, x+offset:x+offset+37]) for offset in (-50, 13)]
        if min(tiles) > 0.35:
            return "combo"
        if max(tiles) < 0.15:
            return "chain"
        return "unknown"

    return [classify(x) for x in (82, 233, 383)]


def choose(cards):
    if not all(card in PRIORITY for card in cards):
        return None
    return min(range(len(cards)), key=lambda i: PRIORITY.index(cards[i]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("image", nargs="?", type=Path)
    source.add_argument("--live", action="store_true", help="preview the phone without tapping")
    args = parser.parse_args()
    try:
        raw = capture_png() if args.live else args.image.read_bytes()
        image = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR) if raw else None
        if image is None:
            raise ValueError("Cannot decode screenshot.")
        state = detect(image)
        if state != "three_cards":
            print(f"{state}: no three-card choice")
            return
        cards = classify_cards(image)
        index = choose(cards)
        choice = "wait" if index is None else f"card {index+1} ({cards[index]})"
        print(f"three_cards: {', '.join(cards)} -> {choice}")
    except (ValueError, OSError, subprocess.SubprocessError, cv2.error) as error:
        parser.exit(1, f"Preview failed: {error}\n")


if __name__ == "__main__":
    main()
