"""Classify one portrait Galaxy Defense screenshot offline."""

import argparse
from pathlib import Path

import cv2
import numpy as np


FIVE_CENTERS = ((98, 473), (233, 473), (367, 473), (166, 680), (300, 680))


def detect(image):
    state, _ = detect_with_slots(image)
    return state


def detect_with_slots(image):
    height, width = image.shape[:2]
    if abs(width / height - 1440 / 3088) > 0.02:
        return "wait", ()

    # Coordinates below use a normalized portrait layout.
    frame = cv2.resize(image, (466, 1000), interpolation=cv2.INTER_AREA)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    teal = cv2.inRange(hsv, (75, 50, 40), (102, 255, 255))
    yellow = cv2.inRange(hsv, (17, 80, 110), (35, 255, 255))

    def coverage(mask, x, y, w, h):
        return cv2.countNonZero(mask[y:y+h, x:x+w]) / (w * h)

    # Require the active start button, stage banner and selected battle tab together.
    bright_teal = cv2.inRange(hsv, (75, 65, 130), (102, 255, 255))
    if (coverage(bright_teal, 130, 820, 206, 41) > 0.75
            # The title lettering stays bright teal on both normal and elite backgrounds.
            and coverage(bright_teal, 180, 135, 106, 18) > 0.2
            and coverage(teal, 205, 926, 50, 53) > 0.7):
        return "battle_ready", ()

    # Result screens share a return button and a weapon statistics header.
    if (coverage(teal, 36, 805, 155, 33) > 0.8
            and coverage(teal, 90, 401, 285, 19) > 0.65):
        banner = hsv[112:133, 112:352]
        for state, lower, upper in (
            ("battle_won", (6, 110, 65), (22, 255, 255)),
            ("battle_lost", (98, 30, 50), (121, 145, 210)),
        ):
            mask = cv2.inRange(banner, lower, upper)
            if cv2.countNonZero(mask) > 0.7 * mask.size:
                return state, ()

    # Card colors vary. Check the horizontal edges of all three title bands and card bottoms.
    def card_edge(x, y):
        above = frame[y-3, x:x+100]
        below = frame[y+3, x:x+100]
        return cv2.absdiff(above, below).mean() > 22

    if (coverage(teal, 180, 110, 105, 23) > 0.6
            and all(card_edge(x, y) for x in (32, 182, 332) for y in (423, 451, 641))):
        return "three_cards", ()

    if coverage(teal, 180, 82, 105, 23) < 0.6:
        return "wait", ()

    # The gold claim button appears once all required draws are complete.
    if coverage(yellow, 134, 902, 197, 35) > 0.65:
        return "five_cards_claim", ()

    # Any slot can be revealed. Accept only an unambiguous group of 4 or 5 matching backs.
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    groups = set()
    for cx, cy in FIVE_CENTERS:
        emblem = gray[cy-22:cy+22, cx-32:cx+32]
        if emblem.std() <= 2:
            continue
        backs = []
        for index, (x, y) in enumerate(FIVE_CENTERS):
            region = gray[y-27:y+27, x-37:x+37]
            score = cv2.matchTemplate(region, emblem, cv2.TM_CCOEFF_NORMED).max()
            if score > 0.85 and coverage(teal, x-32, y-22, 64, 44) > 0.8:
                backs.append(index)
        if len(backs) >= 4:
            groups.add(tuple(backs))
    if len(groups) == 1:
        slots = groups.pop()
        if len(slots) == 5:
            return "five_cards", slots
        face = next(i for i in range(5) if i not in slots)
        x, y = FIVE_CENTERS[face]
        if (coverage(teal, x-53, y-95, 108, 20) > 0.6
                and coverage(teal, 95, 826, 55, 17) > 0.08):
            return "five_cards_draw_again", slots
    return "wait", ()


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
