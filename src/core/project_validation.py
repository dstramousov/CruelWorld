"""Project Validation module for application bootstrap, configuration, validation, and main game orchestration."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from src.systems.log_system import get_logger
from src.utils.paths import CONTENT_DIR, I18N_DIR, resolve_project_path
from src.world.tiled_loader import TiledLoader

logger = get_logger(__name__)


class ProjectValidationError(RuntimeError):
    """Raised when required project data is invalid or missing."""


# Project validation runs before the window opens. It catches missing files,
# broken control bindings, and malformed Tiled layers early with clear errors.
def validate_project_config(config: Mapping[str, Any]) -> None:
    """
    Validate required files and map layers referenced by the game config.

    Args:
        config: Loaded game configuration.

    Raises:
        ProjectValidationError: If a required file or map layer is missing.
    """
    _validate_required_sections(config)
    _validate_required_files(config)
    _validate_controls(config)
    _validate_start_map(config)
    logger.log_event("PROJECT_VALIDATION_PASSED", level=20)


def _validate_required_sections(config: Mapping[str, Any]) -> None:
    """Validate validate required sections.
    
    Args:
        config: Input value used by this operation.
    """
    required_sections = ("window", "render", "font", "world", "localization")
    missing = [section for section in required_sections if section not in config]
    if missing:
        raise ProjectValidationError(f"Missing config sections: {', '.join(missing)}")


def _validate_required_files(config: Mapping[str, Any]) -> None:
    """Validate validate required files.
    
    Args:
        config: Input value used by this operation.
    """
    font_cfg = _as_mapping(config.get("font"), "font")
    world_cfg = _as_mapping(config.get("world"), "world")
    localization_cfg = _as_mapping(config.get("localization"), "localization")

    required_paths = [
        _require_string(font_cfg, "path", "font.path"),
        _require_string(world_cfg, "start_map", "world.start_map"),
        CONTENT_DIR / "items" / "statuses.json",
        CONTENT_DIR / "journal_entries.json",
    ]

    for language in localization_cfg.get("supported_languages", []):
        if not isinstance(language, str):
            raise ProjectValidationError("localization.supported_languages must contain strings")
        required_paths.append(I18N_DIR / f"{language}.lng")

    missing = [str(resolve_project_path(path)) for path in required_paths if not resolve_project_path(path).is_file()]
    if missing:
        raise ProjectValidationError("Missing required files: " + "; ".join(missing))



def _validate_controls(config: Mapping[str, Any]) -> None:
    """Validate validate controls.
    
    Args:
        config: Input value used by this operation.
    """
    controls = _as_mapping(config.get("controls"), "controls")
    required_actions = (
        "move_left",
        "move_right",
        "jump",
        "interact",
        "communicator_toggle",
        "communicator_close",
        "communicator_next",
        "communicator_previous",
        "communicator_menu_next",
        "communicator_menu_previous",
        "communicator_activate",
        "communicator_cancel",
        "flashlight_cycle",
        "toggle_language",
        "toggle_debug",
        "zoom_out",
        "zoom_in",
    )
    missing = [action for action in required_actions if action not in controls]
    if missing:
        raise ProjectValidationError("Missing control bindings: " + ", ".join(missing))
    for action in required_actions:
        _as_string_list(controls.get(action), f"controls.{action}")

def _validate_start_map(config: Mapping[str, Any]) -> None:
    """Validate validate start map.
    
    Args:
        config: Input value used by this operation.
    """
    world_cfg = _as_mapping(config.get("world"), "world")
    map_path = resolve_project_path(_require_string(world_cfg, "start_map", "world.start_map"))
    tile_map = TiledLoader.load(map_path)

    required_tile_layers = _as_string_list(
        world_cfg.get("required_tile_layers", []),
        "world.required_tile_layers",
    )
    required_object_layers = _as_string_list(
        world_cfg.get("required_object_layers", []),
        "world.required_object_layers",
    )

    missing_tile_layers = [name for name in required_tile_layers if name not in tile_map.layers]
    missing_object_layers = [name for name in required_object_layers if name not in tile_map.object_layers]

    errors: list[str] = []
    if missing_tile_layers:
        errors.append("missing tile layers: " + ", ".join(missing_tile_layers))
    if missing_object_layers:
        errors.append("missing object layers: " + ", ".join(missing_object_layers))
    if errors:
        raise ProjectValidationError(f"Invalid start map {map_path}: " + "; ".join(errors))


def _as_mapping(value: object, name: str) -> Mapping[str, Any]:
    """Execute as mapping.
    
    Args:
        value: Input value used by this operation.
        name: Input value used by this operation.
    
    Returns:
        Result produced by this operation.
    """
    if not isinstance(value, Mapping):
        raise ProjectValidationError(f"Config section must be an object: {name}")
    return value


def _require_string(mapping: Mapping[str, Any], key: str, label: str) -> str:
    """Execute require string.
    
    Args:
        mapping: Input value used by this operation.
        key: Input value used by this operation.
        label: Input value used by this operation.
    
    Returns:
        Result produced by this operation.
    """
    value = mapping.get(key)
    if not isinstance(value, str) or not value:
        raise ProjectValidationError(f"Config value must be a non-empty string: {label}")
    return value


def _as_string_list(value: object, label: str) -> list[str]:
    """Execute as string list.
    
    Args:
        value: Input value used by this operation.
        label: Input value used by this operation.
    
    Returns:
        Result produced by this operation.
    """
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ProjectValidationError(f"Config value must be a list of strings: {label}")
    return value
