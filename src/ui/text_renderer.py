"""Font loading, text measuring, and text drawing helpers."""

from __future__ import annotations

import string
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from src.systems.log_system import get_logger
from src.utils import rl as raylib
from src.utils.paths import resolve_project_path

logger = get_logger(__name__)


@dataclass(slots=True)
class FontConfig:
    """Configuration for UI font loading."""

    path: str
    base_size: int = 8
    spacing: float = 1.0


class TextRenderer:
    """Loads a configurable font and renders localized UI text."""

    def __init__(self) -> None:
        """Execute init.
        """
        self._font = None
        self._config: FontConfig | None = None
        self._ready = False

    @property
    def is_ready(self) -> bool:
        """Return whether ready is true.
        
        Returns:
            Result produced by this operation.
        """
        return self._ready and self._font is not None

    def initialize(self, font_config: dict, localization_values: Iterable[str]) -> None:
        # Load one font that contains every glyph used by the current localization
        # bundles, so Ukrainian text renders without missing characters.
        """Execute initialize.
        
        Args:
            font_config: Input value used by this operation.
            localization_values: Input value used by this operation.
        """
        self.shutdown()

        self._config = FontConfig(
            path=str(font_config.get("path", "assets/fonts/PressStart2P-Regular.ttf")),
            base_size=int(font_config.get("base_size", 8)),
            spacing=float(font_config.get("spacing", 1.0)),
        )

        font_path = resolve_project_path(self._config.path).resolve()
        if not font_path.exists():
            logger.log_event("FONT_FILE_NOT_FOUND", level=30, path=str(font_path))
            return

        codepoints = self._build_codepoints(localization_values)
        try:
            self._font = raylib.load_font_ex(
                str(font_path),
                self._config.base_size,
                codepoints,
            )
            self._ready = True
            logger.log_event(
                "FONT_LOADED",
                level=20,
                file=font_path.name,
                glyphs=len(codepoints),
                base_size=self._config.base_size,
                spacing=self._config.spacing,
            )
        except Exception as exc:  # pragma: no cover
            logger.log_exception_event("FONT_LOAD_FAILED", exc, path=str(font_path))
            self._font = None
            self._ready = False

    def shutdown(self) -> None:
        """Execute shutdown.
        """
        if self._font is not None:
            try:
                raylib.unload_font(self._font)
                logger.log_event("FONT_UNLOADED", file=getattr(self._config, 'path', 'unknown'))
            except Exception as exc:  # pragma: no cover
                logger.log_exception_event("FONT_UNLOAD_FAILED", exc)
        self._font = None
        self._ready = False

    def draw(self, text: str, x: int, y: int, size: int, color: tuple[int, int, int, int]) -> None:
        # Fallback to Raylib default text if the configured font is unavailable,
        # which keeps diagnostics visible instead of crashing the UI.
        """Draw draw.
        
        Args:
            text: Input value used by this operation.
            x: Input value used by this operation.
            y: Input value used by this operation.
            size: Input value used by this operation.
            color: Input value used by this operation.
        """
        if not self.is_ready or self._config is None:
            raylib.draw_text(text, x, y, size, color)
            return

        raylib.draw_text_ex(
            self._font,
            text,
            raylib.Vector2(float(x), float(y)),
            float(size),
            self._config.spacing,
            color,
        )

    def measure_width(self, text: str, size: int) -> float:
        """Return rendered text width in pixels for the active font."""
        if not text:
            return 0.0

        if not self.is_ready or self._config is None:
            return float(raylib.measure_text(text, size))

        measured = raylib.measure_text_ex(
            self._font,
            text,
            float(size),
            self._config.spacing,
        )
        return float(getattr(measured, "x", 0.0))

    
    def _build_codepoints(self, localization_values: Iterable[str]) -> list[int]:
        # Build a compact glyph set from ASCII, Ukrainian Cyrillic, punctuation,
        # and all localized strings loaded at startup.
        """Build build codepoints.
        
        Args:
            localization_values: Input value used by this operation.
        
        Returns:
            Result produced by this operation.
        """
        characters: set[str] = set(string.ascii_letters + string.digits)
        characters.update(" !?.,:;+-_=()[]{}<>/%'\"|&#@*\\")
        characters.update("АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ")
        characters.update("абвгґдеєжзиіїйклмнопрстуфхцчшщьюя")
        for value in localization_values:
            characters.update(value)
        characters.discard("\n")
        return sorted(ord(character) for character in characters)


text_renderer = TextRenderer()
