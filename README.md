# Kingdom Fall - Working v6

## Included in this build
- Side-view playable vertical slice
- Tiled-driven test map
- Grave Lace Vine hazard applies `poisoned`
- Blue Mercy Gourd clears `poisoned`
- Cinematic camera profiles switched by Tiled camera zones
- English/Ukrainian localization
- Configurable UI font
- Colored logging and Shift+D debug overlay

## Controls
- `A/D` or arrow keys: move
- `W` or `Space`: jump
- `F`: interact
- `F1`: switch language
- `Shift+D`: debug overlay
- `Q/E`: camera zoom debug

## Slice flow
1. Start in the safe area.
2. Move through the hazard zone and get poisoned.
3. Reach the recovery pocket and use Blue Mercy Gourd.
4. Continue right to the exit trigger.


## Logging

- Console output is colorized by log level and semantic message rules from `config/logging.json`.
- `logs/game.log` and `logs/debug.log` also contain ANSI colors, so `tail -f logs/game.log` stays colorized in a terminal.
- Add new semantic color rules in `message_color_rules`, for example `USER_MOVED_*` -> `BLUE`.
- Helper methods are available through project loggers: `log_event`, `log_state`, `log_object`, `log_exception_event`.

<img width="1536" height="1024" alt="1" src="https://github.com/user-attachments/assets/2ef8ca47-91c2-4950-8b10-37b860b5e606" />
<img width="1536" height="1024" alt="2" src="https://github.com/user-attachments/assets/2624273e-0a77-42dc-9869-f62cfb9a2312" />
<img width="1672" height="940" alt="3" src="https://github.com/user-attachments/assets/b81c8800-d10e-4196-9d45-f120f96e455f" />




- <img width="2132" height="1120" alt="Screenshot from 2026-04-23 21-41-44" src="https://github.com/user-attachments/assets/f85afb5b-a657-47b8-ad39-e810cefee4ba" />

