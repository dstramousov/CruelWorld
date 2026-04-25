"""Paths module for shared utility functions and wrappers."""

from __future__ import annotations

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT_DIR / "config"
I18N_DIR = ROOT_DIR / "i18n"
LOGS_DIR = ROOT_DIR / "logs"
ASSETS_DIR = ROOT_DIR / "assets"
CONTENT_DIR = ROOT_DIR / "content"
SAVES_DIR = ROOT_DIR / "saves"


def resolve_project_path(path_value: str | Path) -> Path:
    """
    Resolve a project-relative or absolute path.

    Args:
        path_value: Absolute path or a path relative to the project root.

    Returns:
        Normalized absolute path.
    """
    path = Path(path_value)
    if path.is_absolute():
        return path
    return ROOT_DIR / path
