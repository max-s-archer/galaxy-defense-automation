"""Classify one portrait Galaxy Defense screenshot offline."""

import argparse
from pathlib import Path

import cv2
import numpy as np


def detect(image):
    height, width = image.shape[:2]
    if abs(width / height - 1440 / 3088) > 0.02:
        return "wait"

    # Coordinates below use a normalized portrait layout.
    frame = cv2.resize(image, (466, 1000), interpolation=cv2.INTER_AREA)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    teal = cv2.inRange(hsv, (75, 50, 40), (102, 255, 255))
    yellow = cv2.inRange(hsv, (17, 80, 110), (35, 255, 255))

    def coverage(mask, x, y, w, h):
        return cv2.countNonZero(mask[y:y+h, x:x+w]) / (w * h)

    # Card colors vary. Check the horizontal edges of all three title bands and card bottoms.
    def card_edge(x, y):
        above = frame[y-3, x:x+100]
        below = frame[y+3, x:x+100]
        return cv2.absdiff(above, below).mean() > 22

    if (coverage(teal, 180, 110, 105, 23) > 0.6
            and all(card_edge(x, y) for x in (32, 182, 332) for y in (423, 451, 641))
            and all(coverage(teal, x, 470, 8, 130) < 0.25 for x in (152, 302))):
        return "three_cards"

    if coverage(teal, 180, 82, 105, 23) < 0.6:
        return "wait"

    # The gold claim button appears once all required draws are complete.
    if coverage(yellow, 134, 902, 197, 35) > 0.65:
        return "five_cards_claim"

    # Compare against the second card, which is still face down after the first draw.
    centers = [(98, 473), (233, 473), (367, 473), (166, 680), (300, 680)]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    x, y = centers[1]
    emblem = gray[y-22:y+22, x-32:x+32]
    if emblem.std() > 2:
        backs = []
        for x, y in centers:
            region = gray[y-27:y+27, x-37:x+37]
            score = cv2.matchTemplate(region, emblem, cv2.TM_CCOEFF_NORMED).max()
            backs.append(score > 0.85 and coverage(teal, x-32, y-22, 64, 44) > 0.8)
        if all(backs):
            return "five_cards"
        if (all(backs[1:]) and coverage(teal, 45, 378, 108, 20) > 0.6
                and coverage(teal, 95, 826, 55, 17) > 0.08):
            return "five_cards_draw_again"
    return "wait"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    try:
        data = np.frombuffer(args.image.read_bytes(), dtype=np.uint8)
        image = cv2.imdecode(data, cv2.IMREAD_COLOR) if data.size else None
    except (OSError, cv2.error) as error:
        parser.exit(1, f"Cannot read image: {error}\n")
    if image is None:
        parser.exit(1, "Cannot decode image.\n")
    print(detect(image))


if __name__ == "__main__":
    main()
