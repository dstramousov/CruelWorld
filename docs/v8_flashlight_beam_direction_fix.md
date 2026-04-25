# v8_flashlight_beam_direction_fix

## Fixed

- Fixed flashlight beam rendering when the player faces right.
- The issue was caused by triangle vertex winding in `raylib.DrawTriangle`.
- `LightSystem` now builds beam triangle points with stable winding for both left and right directions.

## Updated files

- `src/systems/light_system.py`
- `tests/test_light_system.py`

## Notes

- No files from the base archive were removed.
- User utilities `a`, `c`, `d`, `g`, and `t` are preserved.
