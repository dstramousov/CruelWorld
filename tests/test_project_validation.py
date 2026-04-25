from __future__ import annotations

import copy

import pytest

from src.core.project_validation import ProjectValidationError, validate_project_config
from src.utils.paths import CONFIG_DIR
from src.utils.serialization import load_json


def _game_config() -> dict:
    return load_json(CONFIG_DIR / "game.json")


def test_project_validation_accepts_current_game_config() -> None:
    validate_project_config(_game_config())


def test_project_validation_rejects_missing_required_section() -> None:
    config = _game_config()
    config.pop("font")

    with pytest.raises(ProjectValidationError, match="Missing config sections"):
        validate_project_config(config)


def test_project_validation_rejects_missing_control_binding() -> None:
    config = _game_config()
    config = copy.deepcopy(config)
    config["controls"].pop("interact")

    with pytest.raises(ProjectValidationError, match="Missing control bindings"):
        validate_project_config(config)


def test_project_validation_rejects_invalid_control_type() -> None:
    config = _game_config()
    config = copy.deepcopy(config)
    config["controls"]["interact"] = "F"

    with pytest.raises(ProjectValidationError, match="controls.interact"):
        validate_project_config(config)


def test_project_validation_rejects_missing_start_map() -> None:
    config = _game_config()
    config = copy.deepcopy(config)
    config["world"]["start_map"] = "assets/maps/does_not_exist.tmx"

    with pytest.raises(ProjectValidationError, match="Missing required files"):
        validate_project_config(config)
