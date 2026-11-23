# Galaxy Defense Automation

A planned Python tool for automating repeated card selections in Galaxy Defense.
The initial target device is a Samsung Galaxy S23 Ultra running Android 16.

## Phase 1

The tool will recognize two card selection screens and choose by position. Card names,
descriptions, and effects do not affect the choice.

- **Three cards:** Tap the first card once. The game returns to battle automatically.
- **Five cards:** Tap the first card once. Another card may appear after the selection.
  Keep the single selection and tap Continue to resume battle. Only this flow uses Continue.

During battle or on an unrecognized screen, the tool waits without tapping.

## Project status

The author has approved the Phase 1 scope. Implementation is pending. The author may release the
tool after Phase 1 is complete. The scope of Phase 2 is open.

## Repository

- [Agent instructions](AGENTS.md)
- [Apache License 2.0](LICENSE)
