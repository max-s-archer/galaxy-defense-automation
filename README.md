# Galaxy Defense Automation

[简体中文](README.zh-CN.md)

A planned Python tool for automating repeated card selections in Galaxy Defense.
The initial target device is a Samsung Galaxy S23 Ultra running Android 16.

## Phase 1

The tool will recognize two card selection screens and choose by position. Card names,
descriptions, and effects do not affect the choice.

- **Three cards:** Tap the first card once. The game returns to battle automatically.
- **Five cards:** Draw a random face-down card. If prompted to draw again, choose a remaining
  face-down card at random. Each eligible slot is equally likely. Tap the gold "獲得" button
  when all required draws are complete to resume battle.

During battle or on an unrecognized screen, the tool waits without tapping.

## Phase 2: three-card priority

On the three-card upgrade screen, choose the highest-priority card available.
The priority order is highest first.

1. Purple card
2. Combination skill card (組合卡)
3. Chain skill card (連鎖卡)
4. New weapon card (新)
5. Ordinary card

If multiple cards share the highest priority, choose the leftmost of those cards.

Preview the choice with `scripts/preview_choice.py IMAGE` or `scripts/preview_choice.py --live`
using the project Python environment. Both modes report the categories from left to right
without tapping. Both single-step and polling commands apply the same choice to the current
frame. A card marked `新` is classified as a new weapon and ranks above an ordinary card.
If any category is uncertain, neither command taps.

When the phone is on the battle start page, the script recognizes the `開始戰鬥` button as
`battle_ready` and taps it once. It then waits for the battle screen before handling cards.

## Project status

Phase 1 has passed device validation. Phase 2 is in progress. The author completed a full
battle on the target device using priority selection. Combination cards have been checked
in screenshot replay; live selection of that category is not yet confirmed. New weapon
recognition and automatic battle start are ready for device testing.

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
| `battle_ready` | Stage selection with the active Start Battle button |
| `five_cards` | Five face-down cards ready to draw |
| `five_cards_draw_again` | First card revealed and the game prompts for another draw |
| `five_cards_claim` | All required draws complete and the gold claim button visible |
| `battle_won` | Challenge completed, showing rewards and damage statistics |
| `battle_lost` | Challenge failed, showing rewards and damage statistics |
| `wait` | Battle or an unrecognized layout |

## Run one step on the phone

Connect the USB device and open Galaxy Defense. From the same Python environment, preview
the action for the current screen, then run one live step (macOS, zsh):

```sh
.venv/bin/python scripts/run_step.py --dry-run
.venv/bin/python scripts/run_step.py
```

On Windows (PowerShell), use `.\.venv\Scripts\python.exe scripts\run_step.py` with the same
options. Each invocation captures a fresh frame. On the three-card screen, verify that a live
step selects the reported card and battle resumes. Run again during battle and expect `wait: no tap`.
For five cards, run once per action: draw a random card, draw another face-down card if
prompted, and tap the claim button when it appears.

## Poll during battle

On macOS, start the game and run `.venv/bin/python scripts/run_step.py --loop`.
On Windows PowerShell, run `.\.venv\Scripts\python.exe scripts\run_step.py --loop`.
Press Ctrl+C to stop polling.

### Polling options

| Option | Default | When to use it |
| --- | --- | --- |
| `--interval SECONDS` | `2` | Set the delay after each check. Use `--loop --interval 1` for a one-second delay. |
| `--dry-run` | Off | Use `--loop --dry-run` to see which actions the script would take. |
| `--stop-on-result` | Off | Use `--loop --stop-on-result` to exit after one confirmed win or loss. |

Two consecutive checks showing the same outcome confirm the result. The terminal prints
`Result: battle_won` or `Result: battle_lost` once for that result screen. By default, polling
continues so you can manually start another battle. With `--stop-on-result`, the Python process
exits successfully and the phone stays on the result screen. This also applies in dry-run mode.

Each poll showing three recognized upgrade cards taps the preferred card once, even on consecutive level-ups.
For five-card screens, each new selection state triggers its corresponding action once. If that
state persists for three further checks, the loop prints a reminder and keeps observing. Two
consecutive `wait` results allow the same five-card state to trigger a fresh action.
A capture or tap error stops the loop.

## Repository

- [Agent instructions](AGENTS.md)
- [Apache License 2.0](LICENSE)
