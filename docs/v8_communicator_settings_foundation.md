# v8 communicator settings foundation

Added the first player-facing Settings screen to the communicator.

## What is included

- Language row: cycles English / Українська / Русский.
- Communicator text-size row: cycles through values from `config/game.json`.
- Controls row: read-only pointer to `config/game.json` for now.

## Controls

- `Up/Down` or `W/S`: select a settings row.
- `Enter`: change the selected editable setting.
- `Left/Right`: move between top communicator tabs.

## Notes

Developer-only overlays are intentionally not shown in this Settings screen.
