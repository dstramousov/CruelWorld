from src.systems.time_system import TimeSystem


def make_system(**overrides: object) -> TimeSystem:
    cycle_cfg = {
        "enabled": True,
        "day_duration_minutes": 24.0,
        "randomize_start_time": False,
        "start_time_hours": 12.0,
        "phase_ranges": {
            "dawn_start": 5.0,
            "day_start": 7.0,
            "dusk_start": 18.0,
            "night_start": 20.0,
        },
        "stars": {
            "enabled": True,
            "count": 8,
            "min_alpha": 90,
            "max_alpha": 255,
            "twinkle_enabled": False,
            "parallax_speed": 0.03,
        },
        "tint": {
            "day_world": [255, 255, 255, 0],
            "dusk_world": [255, 226, 186, 22],
            "night_world": [180, 196, 255, 42],
            "dawn_world": [198, 222, 255, 20],
            "day_sky": [225, 235, 255, 36],
            "dusk_sky": [255, 196, 140, 78],
            "night_sky": [96, 126, 168, 118],
            "dawn_sky": [176, 206, 240, 72],
        },
    }
    cycle_cfg.update(overrides)
    return TimeSystem({"day_night_cycle": cycle_cfg}, seed=123)


def test_time_phase_boundaries() -> None:
    system = make_system(start_time_hours=6.0)
    system.current_time_hours = 6.5
    assert system.get_phase_name() == "dawn"
    system.current_time_hours = 12.0
    assert system.get_phase_name() == "day"
    system.current_time_hours = 19.0
    assert system.get_phase_name() == "dusk"
    system.current_time_hours = 23.0
    assert system.get_phase_name() == "night"


def test_star_visibility_changes_with_time() -> None:
    system = make_system(start_time_hours=12.0)
    system.current_time_hours = 12.0
    assert system.get_star_visibility() == 0.0
    system.current_time_hours = 19.0
    assert 0.0 < system.get_star_visibility() < 1.0
    system.current_time_hours = 22.0
    assert system.get_star_visibility() == 1.0
    system.current_time_hours = 6.0
    assert 0.0 < system.get_star_visibility() < 1.0


def test_time_advances_one_game_hour_per_real_minute_by_default() -> None:
    system = make_system(start_time_hours=0.0)
    system.update(60.0)
    assert round(system.current_time_hours, 3) == 1.0


def test_world_tint_matches_phase_intent() -> None:
    system = make_system(start_time_hours=12.0)
    system.current_time_hours = 12.0
    assert system.get_world_tint() == (255, 255, 255, 0)

    system.current_time_hours = 19.0
    dusk_tint = system.get_world_tint()
    assert 0 < dusk_tint[3] < 42
    assert dusk_tint[0] >= dusk_tint[2]

    system.current_time_hours = 22.0
    assert system.get_world_tint() == (180, 196, 255, 42)


def test_sky_tint_is_stronger_than_world_tint_at_night() -> None:
    system = make_system(start_time_hours=22.0)
    system.current_time_hours = 22.0
    sky_tint = system.get_sky_tint()
    world_tint = system.get_world_tint()
    assert sky_tint[3] > world_tint[3]
    assert sky_tint[2] >= sky_tint[0]
