# v7_communicator_menu_exit_pass

## Changes

- Disabled direct ESC-to-quit behavior through `raylib.set_exit_key(0)`.
- Exit is now requested only from the communicator menu.
- Added top communicator menu:
  - New Game
  - Save
  - Load
  - Settings
  - Exit Game
- Top menu items highlight when selected.
- Added placeholder content panels for New Game, Save, Load and Settings.
- Added Exit Game confirmation dialog with YES / NO click targets.
- Added mouse click handling in internal render coordinates.
- Preserved user utilities: `a`, `c`, `g`.

## Notes

Save/load/new game/settings are UI placeholders for now. They do not change game state yet.

## Hotfix: rectangle coordinate normalization

Fixed communicator menu crash on mouse click. UI tab widths can be calculated from measured text and may become floating-point values. The raylib wrapper now normalizes rectangle coordinates and sizes to integer pixels before calling `DrawRectangle`.


## Communicator tab fix

- Added `Communicator` as the first top-menu item.
- Opening the communicator now always selects the communicator/journal tab.
- Clicking `Communicator` returns from other menu sections back to the default journal view.
