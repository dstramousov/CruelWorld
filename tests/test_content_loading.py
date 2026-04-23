from src.utils.paths import CONFIG_DIR
from src.utils.serialization import load_json


def test_game_config_loads() -> None:
    data = load_json(CONFIG_DIR / "game.json")
    assert data["render"]["internal_width"] == 640
