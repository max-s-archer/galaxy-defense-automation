"""Capture the current USB device screen and perform one Galaxy Defense action."""

import argparse
import math
import secrets
import subprocess
import time

import cv2
import numpy as np

from capture_screen import capture_png
from detect_screen import FIVE_CENTERS, detect_with_slots
from preview_choice import choose, classify_cards


# Centers in the detector's 466 x 1000 portrait layout.
DRAW_STATES = ("five_cards", "five_cards_draw_again")


def observe():
    image = cv2.imdecode(np.frombuffer(capture_png(), np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Cannot decode the device screenshot.")
    state, slots = detect_with_slots(image)
    return state, image, slots


def act(state, image, dry_run, slots):
    target = None
    if state in DRAW_STATES and slots:
        index = secrets.choice(slots)
        target = FIVE_CENTERS[index]
        print(f"{state}: random card {index + 1}")
    elif state == "five_cards_claim":
        target = (233, 920)
    elif state == "battle_ready":
        target = (233, 840)
    if state == "three_cards":
        cards = classify_cards(image)
        index = choose(cards)
        if index is None:
            print(f"{state}: {', '.join(cards)} -> wait: no tap")
            return
        target = ((82, 233, 383)[index], 525)
        print(f"{state}: {', '.join(cards)} -> card {index + 1} ({cards[index]})")
    if target is None:
        print(f"{state}: no tap")
        return
    height, width = image.shape[:2]
    x = round(target[0] * width / 466)
    y = round(target[1] * height / 1000)
    if dry_run:
        print(f"{state}: would tap ({x}, {y})")
        return
    subprocess.run(["adb", "-d", "shell", "input", "tap", str(x), str(y)],
                   check=True, timeout=10)
    print(f"{state}: sent tap ({x}, {y})")


def poll(interval, dry_run, stop_on_result=False):
    last_action = None
    wait_frames = 0
    repeats = 0
    round_number = 0
    previous_state = None
    reported_result = None
    start_sent = False
    while True:
        state, image, slots = observe()
        round_number += 1
        print(f"[poll {round_number}] {state}", flush=True)
        if state in ("battle_won", "battle_lost"):
            start_sent = False
            if state == previous_state and state != reported_result:
                print(f"Result: {state}", flush=True)
                reported_result = state
                if stop_on_result:
                    return
            last_action = None
            repeats = wait_frames = 0
        elif state == "battle_ready":
            if not start_sent:
                act(state, image, dry_run, slots)
                start_sent = True
            last_action = reported_result = None
            repeats = wait_frames = 0
        elif state not in (*DRAW_STATES, "five_cards_claim", "three_cards"):
            if wait_frames == 0:
                print(f"{state}: no tap")
            wait_frames += 1
            # A single unrecognized animation frame can interrupt a selection.
            if wait_frames >= 2:
                last_action = None
                reported_result = None
            repeats = 0
        else:
            start_sent = False
            reported_result = None
            wait_frames = 0
            # Back-to-back level-ups can present another choice between polls.
            if state == "three_cards" or state != last_action:
                act(state, image, dry_run, slots)
                last_action = state
                repeats = 0
            else:
                repeats += 1
                if repeats == 3:
                    print(f"{state}: still visible after 3 checks. Check the phone.")
        previous_state = state
        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="print the planned action only")
    parser.add_argument("--loop", action="store_true", help="poll until Ctrl+C")
    parser.add_argument("--stop-on-result", action="store_true",
                        help="exit polling after two matching battle results")
    parser.add_argument("--interval", type=float, default=2, help="seconds between checks")
    args = parser.parse_args()
    if args.stop_on_result and not args.loop:
        parser.error("--stop-on-result requires --loop")
    if not math.isfinite(args.interval) or args.interval <= 0:
        parser.error("--interval must be a finite positive number")
    try:
        if args.loop:
            poll(args.interval, args.dry_run, args.stop_on_result)
        else:
            state, image, slots = observe()
            act(state, image, args.dry_run, slots)
    except KeyboardInterrupt:
        print("Stopped.")
    except (OSError, ValueError, subprocess.SubprocessError, cv2.error) as error:
        parser.exit(1, f"Step failed: {error}\n")


if __name__ == "__main__":
    main()
