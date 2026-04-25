# v8_new_game_foundation

Added a working New Game screen to the communicator.

## Features

- New Game screen now contains:
  - hero name input;
  - starting scenario display;
  - Start action;
  - Back action.
- Player can type the hero name while the name row is selected.
- `Backspace` removes one character from the hero name.
- `Up/Down` or `W/S` changes the selected row.
- `Enter` activates the selected row.
- Starting a new game resets runtime state:
  - player object and position;
  - health and statuses;
  - flashlight mode;
  - journal discoveries;
  - slice completion flag;
  - interaction prompt state;
  - time-of-day cycle.
- Hero name is stored in `WorldState.player_name` for future save/load support.

## Config

```json
"new_game": {
  "default_hero_name": "Survivor",
  "max_hero_name_length": 18,
  "scenario_id": "crash_wake"
}
```

## Notes

- This is still a foundation screen, not a full character creator.
- Difficulty selection and multiple starting scenarios should be added later, after save/load foundation.
