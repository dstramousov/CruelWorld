from __future__ import annotations

from src.components.light_emitter import LightEmitterComponent
from src.systems.light_system import LightSystem


def test_light_system_cycles_modes_in_order() -> None:
    light = LightEmitterComponent(mode="off")
    system = LightSystem()

    assert system.cycle_mode(light) == "radial"
    assert system.cycle_mode(light) == "beam"
    assert system.cycle_mode(light) == "off"


def test_light_system_recovers_from_unknown_mode() -> None:
    light = LightEmitterComponent(mode="broken")
    system = LightSystem()

    assert system.cycle_mode(light) == "radial"


def test_draw_player_flashlight_skips_disabled_or_off_light(monkeypatch) -> None:
    calls: list[tuple] = []
    monkeypatch.setattr("src.systems.light_system.raylib.draw_circle", lambda *args: calls.append(args))
    monkeypatch.setattr("src.systems.light_system.raylib.draw_triangle", lambda *args: calls.append(args))
    system = LightSystem()

    system.draw_player_flashlight(
        light=LightEmitterComponent(enabled=False, mode="radial"),
        screen_x=10,
        screen_y=20,
        player_height=12,
        facing=1.0,
        zoom=1.0,
    )
    system.draw_player_flashlight(
        light=LightEmitterComponent(enabled=True, mode="off"),
        screen_x=10,
        screen_y=20,
        player_height=12,
        facing=1.0,
        zoom=1.0,
    )

    assert calls == []


def test_draw_player_flashlight_draws_radial_mode(monkeypatch) -> None:
    calls: list[tuple] = []
    monkeypatch.setattr("src.systems.light_system.raylib.draw_circle", lambda *args: calls.append(args))
    system = LightSystem()

    system.draw_player_flashlight(
        light=LightEmitterComponent(mode="radial", radius=10.0),
        screen_x=50,
        screen_y=100,
        player_height=20,
        facing=1.0,
        zoom=2.0,
    )

    assert calls[0][0:3] == (50, 88, 20.0)


def test_draw_player_flashlight_draws_left_beam_mode(monkeypatch) -> None:
    calls: list[tuple] = []
    monkeypatch.setattr("src.systems.light_system.raylib.draw_triangle", lambda *args: calls.append(args))
    system = LightSystem()

    system.draw_player_flashlight(
        light=LightEmitterComponent(mode="beam", beam_distance=30.0, beam_half_width=5.0),
        screen_x=50,
        screen_y=100,
        player_height=20,
        facing=-1.0,
        zoom=2.0,
    )

    assert calls[0][0:6] == (50, 88, -10, 78, -10, 98)


def test_draw_player_flashlight_draws_right_beam_with_stable_winding(monkeypatch) -> None:
    calls: list[tuple] = []
    monkeypatch.setattr("src.systems.light_system.raylib.draw_triangle", lambda *args: calls.append(args))
    system = LightSystem()

    system.draw_player_flashlight(
        light=LightEmitterComponent(mode="beam", beam_distance=30.0, beam_half_width=5.0),
        screen_x=50,
        screen_y=100,
        player_height=20,
        facing=1.0,
        zoom=2.0,
    )

    assert calls[0][0:6] == (50, 88, 110, 98, 110, 78)


def test_build_beam_points_returns_visible_winding_for_both_directions() -> None:
    light = LightEmitterComponent(mode="beam", beam_distance=30.0, beam_half_width=5.0)

    left_points = LightSystem.build_beam_points(light, 50, 88, -1.0, 2.0)
    right_points = LightSystem.build_beam_points(light, 50, 88, 1.0, 2.0)

    assert left_points == ((50, 88), (-10, 78), (-10, 98))
    assert right_points == ((50, 88), (110, 98), (110, 78))
