from __future__ import annotations

import pytest

from src.systems.input_system import InputSystem
from src.utils import rl as raylib


def test_parse_chord_supports_single_keys_and_modifier_chords() -> None:
    assert InputSystem._parse_chord("F") == (raylib.KEY_F,)
    assert InputSystem._parse_chord("LEFT_SHIFT+D") == (raylib.KEY_LEFT_SHIFT, raylib.KEY_D)


def test_parse_chord_rejects_empty_and_unknown_chords() -> None:
    with pytest.raises(ValueError, match="Empty key chord"):
        InputSystem._parse_chord("+")

    with pytest.raises(ValueError, match="Unknown key name"):
        InputSystem._parse_chord("NO_SUCH_KEY")


def test_horizontal_axis_uses_configured_bindings(monkeypatch: pytest.MonkeyPatch) -> None:
    down_keys: set[int] = set()
    monkeypatch.setattr(raylib, "is_key_down", lambda key: key in down_keys)
    monkeypatch.setattr(raylib, "is_key_pressed", lambda key: False)
    input_system = InputSystem({"move_left": ["A"], "move_right": ["D"]})

    down_keys.add(raylib.KEY_A)
    assert input_system.horizontal_axis() == -1.0

    down_keys.clear()
    down_keys.add(raylib.KEY_D)
    assert input_system.horizontal_axis() == 1.0

    down_keys.add(raylib.KEY_A)
    assert input_system.horizontal_axis() == 0.0


def test_action_pressed_supports_modifier_chords(monkeypatch: pytest.MonkeyPatch) -> None:
    down_keys = {raylib.KEY_LEFT_SHIFT}
    pressed_keys = {raylib.KEY_D}
    monkeypatch.setattr(raylib, "is_key_down", lambda key: key in down_keys)
    monkeypatch.setattr(raylib, "is_key_pressed", lambda key: key in pressed_keys)
    input_system = InputSystem({"toggle_debug": ["LEFT_SHIFT+D"]})

    assert input_system.is_action_pressed("toggle_debug") is True

    down_keys.clear()
    assert input_system.is_action_pressed("toggle_debug") is False


def test_invalid_configured_binding_is_ignored() -> None:
    input_system = InputSystem({"interact": ["NO_SUCH_KEY"]})

    assert input_system.is_interact_pressed() is False


def test_flashlight_cycle_action_uses_configurable_binding(monkeypatch: pytest.MonkeyPatch) -> None:
    pressed_keys = {raylib.KEY_L}
    monkeypatch.setattr(raylib, "is_key_down", lambda key: False)
    monkeypatch.setattr(raylib, "is_key_pressed", lambda key: key in pressed_keys)
    input_system = InputSystem({"flashlight_cycle": ["L"]})

    assert input_system.is_flashlight_cycle_pressed() is True


def test_parse_chord_supports_enter_and_backspace() -> None:
    assert InputSystem._parse_chord("ENTER") == (raylib.KEY_ENTER,)
    assert InputSystem._parse_chord("BACKSPACE") == (raylib.KEY_BACKSPACE,)
