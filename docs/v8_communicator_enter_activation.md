# v8 communicator Enter activation

## Changes

- Added communicator activation key binding: `communicator_activate = ENTER`.
- Added communicator cancel key binding: `communicator_cancel = BACKSPACE`.
- `Enter` activates the currently selected communicator top-menu item.
- When `Exit Game` is selected, `Enter` opens the confirmation dialog.
- When the exit confirmation dialog is visible, `Enter` confirms exit.
- `Backspace` cancels the confirmation dialog and returns to the `Communicator` tab.
- Updated communicator control hints for English, Ukrainian and Russian localization.

## Notes

The implementation does not simulate a mouse click. It uses explicit UI actions on `CommunicatorUi`, which keeps the behavior testable and independent from mouse hitboxes.
