"""Asset Manager module for application bootstrap, configuration, validation, and main game orchestration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.systems.log_system import get_logger
from src.utils import rl as raylib
from src.utils.paths import resolve_project_path

logger = get_logger(__name__)


class AssetLoadError(RuntimeError):
    """Raised when a required asset cannot be loaded."""


class AssetManager:
    """Small runtime asset manager for validated project-relative assets."""

    def __init__(self) -> None:
        """Execute init.
        """
        self._textures: list[Any] = []

    def resolve_existing_file(self, path_value: str | Path) -> Path:
        """
        Resolve and validate an existing file path.

        Args:
            path_value: Absolute path or a path relative to the project root.

        Returns:
            Resolved absolute path.

        Raises:
            AssetLoadError: If the file does not exist or is not a file.
        """
        path = resolve_project_path(path_value)
        if not path.is_file():
            raise AssetLoadError(f"Required asset file not found: {path}")
        return path

    def load_texture(self, path_value: str | Path) -> Any:
        """
        Load a texture and remember it for shutdown.

        Args:
            path_value: Absolute path or a path relative to the project root.

        Returns:
            Loaded Raylib texture object.

        Raises:
            AssetLoadError: If the texture file cannot be resolved or loaded.
        """
        path = self.resolve_existing_file(path_value)
        try:
            texture = raylib.load_texture(str(path))
        except Exception as exc:
            raise AssetLoadError(f"Failed to load texture: {path}") from exc
        self._textures.append(texture)
        logger.log_event("ASSET_TEXTURE_LOADED", level=20, path=str(path))
        return texture

    def unload_all(self) -> None:
        """Unload all tracked runtime assets."""
        # Shutdown is best-effort: log unload failures but keep releasing the
        # remaining assets so one bad texture cannot block cleanup.
        for texture in self._textures:
            try:
                raylib.unload_texture(texture)
            except Exception as exc:
                logger.log_exception_event("ASSET_TEXTURE_UNLOAD_FAILED", exc, level=40)
        self._textures.clear()
