# v7_debug_overlay_metrics_pass

## Goal

Extend the existing Shift+D debug overlay with runtime system metrics. No separate overlay was added.

## Added metrics

- FPS.
- Raw frame time in milliseconds.
- Simulation update delta in milliseconds.
- Process RSS memory in MB when available.
- Total, active and visible runtime object counts.
- Object breakdown for hazards, interactables and observation markers.
- Debug chunk status in full-map mode.
- Map size in tiles and pixels.

## Chunk note

The game still loads the current TMX map as one full map. The overlay now exposes a chunk debug line so future streaming can replace `full_map` mode with real loaded/active chunk counts without changing the overlay UI.

Current debug chunk width is configured in `config/game.json` under `debug.chunk_width_tiles`.

## Controls

The overlay is still toggled through the existing configured action:

- `toggle_debug`: `LEFT_SHIFT+D`, `RIGHT_SHIFT+D`

## Files changed

- `src/core/app.py`
- `src/core/game.py`
- `src/systems/debug_metrics.py`
- `src/utils/rl.py`
- `config/game.json`
- `i18n/eng.lng`
- `i18n/ukr.lng`
