from src.core.project_validation import validate_project_config
from src.utils.paths import CONFIG_DIR, resolve_project_path
from src.utils.serialization import load_json


def test_game_config_loads() -> None:
    data = load_json(CONFIG_DIR / "game.json")
    assert data["render"]["internal_width"] == 640
    assert data["render"]["internal_height"] == 360
    assert data["window"]["width"] == 1280
    assert data["window"]["height"] == 720
    assert "parallax" not in data


def test_start_map_is_config_driven_and_exists() -> None:
    data = load_json(CONFIG_DIR / "game.json")
    start_map = resolve_project_path(data["world"]["start_map"])
    assert start_map.is_file()


def test_project_config_validation_passes() -> None:
    data = load_json(CONFIG_DIR / "game.json")
    validate_project_config(data)


def test_controls_are_config_driven() -> None:
    data = load_json(CONFIG_DIR / "game.json")
    controls = data["controls"]
    assert controls["interact"] == ["F"]
    assert "TAB" in controls["communicator_toggle"]
    assert "communicator_close" in controls


def test_journal_entries_load() -> None:
    entries = load_json(resolve_project_path("content/journal_entries.json"))
    assert "disc.blue_mercy_gourd" in entries
    assert "disc.rain_choir_frog" in entries
