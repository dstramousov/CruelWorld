# v8_game_state_and_flashlight_foundation

## Done in this pass

- Added the first player flashlight foundation before larger GameState/save work.
- Added flashlight modes: `off`, `radial`, `beam`.
- Added configurable input action: `flashlight_cycle` with default `L`.
- Added player light component fields for radial radius and beam geometry.
- Added `LightSystem` for mode cycling and drawing.
- Added basic radial light and directed beam visuals.
- Added debug overlay line for current flashlight mode.
- Added localization strings for flashlight messages.
- Added tests for flashlight mode cycling and draw routing.

## Notes

- Flashlight has no energy drain by design.
- The current implementation is a visual/gameplay foundation, not a final lighting renderer.
- The selected mode is ready to be stored by future save/load work.
