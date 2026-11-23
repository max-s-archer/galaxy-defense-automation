# Galaxy Defense Automation

A planned Python tool for automating repeated card selections in Galaxy Defense.
The initial target device is a Samsung Galaxy S23 Ultra running Android 16.

## Phase 1

The tool will recognize two card selection screens and choose by position. Card names,
descriptions, and effects do not affect the choice.

- **Three cards:** Tap the first card once. The game returns to battle automatically.
- **Five cards:** Draw the first card. If prompted to draw again, choose a remaining face-down
  card. The "獲得" button appears when all required draws are complete. Tap it to resume battle.

During battle or on an unrecognized screen, the tool waits without tapping.

## Project status

The author has approved the Phase 1 scope. The first utility captures a single screenshot.
The author may release the tool after Phase 1 is complete. The scope of Phase 2 is open.

## Capture one screenshot

On macOS, install Python 3.7 or later and Android SDK Platform-Tools. Enable USB debugging on
the phone, connect it by USB, unlock it, and accept the debugging prompt. If using the default
Android Studio SDK location, add ADB to the current zsh session:

```sh
export PATH="$HOME/Library/Android/sdk/platform-tools:$PATH"
```

From the repository root, open the game on the phone and run:

```sh
adb devices -l
python3 scripts/capture_screen.py battle.png
```

Check that the phone is listed as `device`. Open `battle.png` in Preview and verify the full
game screen is visible, correctly oriented, and legible. Change the screen and capture again
using a fresh filename. Each invocation saves the original PNG and preserves existing files.
To verify failure handling, disconnect USB and run the script with another fresh filename.
Expect a nonzero exit status and no output file.

## Detect the screen offline

From the repository root, create a Python environment and classify a saved portrait screenshot.
On macOS (zsh):

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/detect_screen.py battle_three_cards.png
```

On Windows (PowerShell):

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\detect_screen.py battle_three_cards.png
```

Supply your own screenshot path. The detector uses the portrait layout observed on the S23 Ultra.

| Output | Screen |
| --- | --- |
| `three_cards` | Three face-up upgrade choices |
| `five_cards` | Five face-down cards ready to draw |
| `five_cards_draw_again` | First card revealed and the game prompts for another draw |
| `five_cards_claim` | All required draws complete and the gold claim button visible |
| `wait` | Battle or an unrecognized layout |

## Repository

- [Agent instructions](AGENTS.md)
- [Apache License 2.0](LICENSE)
