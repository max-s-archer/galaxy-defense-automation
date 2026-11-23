"""Capture one PNG from a USB-connected Android device."""

import argparse
import subprocess
import sys
from pathlib import Path


def capture_png() -> bytes:
    result = subprocess.run(
        ["adb", "-d", "exec-out", "screencap", "-p"],
        capture_output=True,
        timeout=30,
    )
    if result.returncode:
        detail = result.stderr.decode(errors="replace").strip()
        raise ValueError(detail or f"adb exited with status {result.returncode}")

    image = result.stdout
    if not (image.startswith(b"\x89PNG\r\n\x1a\n") and
            image.endswith(b"\x00\x00\x00\x00IEND\xaeB`\x82")):
        raise ValueError("ADB returned an empty or incomplete PNG. Check the USB connection.")
    return image


def capture(output: Path) -> None:
    image = capture_png()
    with output.open("xb") as stream:
        try:
            stream.write(image)
            stream.flush()
        except OSError:
            output.unlink()
            raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="new PNG file in an existing directory")
    args = parser.parse_args()
    try:
        capture(args.output)
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        print(f"Capture failed: {error}", file=sys.stderr)
        return 1
    print(f"Saved {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
