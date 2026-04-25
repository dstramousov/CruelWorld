"""Localization System module for runtime gameplay systems."""

from __future__ import annotations

from pathlib import Path

from src.systems.log_system import get_logger
from src.utils.enums import Language
from src.utils.paths import I18N_DIR

logger = get_logger(__name__)


class LocalizationSystem:
    """Loads and resolves localized strings from .lng files."""

    def __init__(self, default_language: Language = Language.ENG) -> None:
        """Execute init.
        
        Args:
            default_language: Input value used by this operation.
        """
        self._default_language = default_language
        self._current_language = default_language
        self._bundles: dict[Language, dict[str, str]] = {}
        self._load_all()

    @property
    def current_language(self) -> Language:
        """Execute current language.
        
        Returns:
            Result produced by this operation.
        """
        return self._current_language

    def toggle_language(self) -> None:
        """Cycle to the next available localization language."""
        languages = tuple(Language)
        try:
            current_index = languages.index(self._current_language)
        except ValueError:
            current_index = 0
        self.set_language(languages[(current_index + 1) % len(languages)])

    def set_language(self, language: Language) -> None:
        """Set the active localization language.

        Args:
            language: Language to make active.
        """
        self._current_language = language
        logger.log_event(
            "I18N_LANGUAGE_SWITCHED",
            level=20,
            language=self._current_language.value,
        )

    def tr(self, key: str, **kwargs: object) -> str:
        """Execute tr.
        
        Args:
            key: Input value used by this operation.
            kwargs: Input value used by this operation.
        
        Returns:
            Result produced by this operation.
        """
        value = self._bundles.get(self._current_language, {}).get(key)
        if value is None:
            value = self._bundles.get(self._default_language, {}).get(key)
            logger.log_event(
                "I18N_KEY_MISSING_ACTIVE_BUNDLE",
                level=30,
                language=self._current_language.value,
                key=key,
            )
        if value is None:
            logger.log_event(
                "I18N_KEY_MISSING_FALLBACK_BUNDLE",
                level=40,
                key=key,
            )
            return key
        try:
            return value.format(**kwargs)
        except Exception as exc:  # pragma: no cover
            logger.log_exception_event("I18N_FORMAT_FAILED", exc, key=key)
            return value

    def get_all_values(self) -> list[str]:
        """Return all values.
        
        Returns:
            Result produced by this operation.
        """
        values: list[str] = []
        for bundle in self._bundles.values():
            values.extend(bundle.values())
        return values

    def _load_all(self) -> None:
        """Load all localization bundles declared by the Language enum."""
        for language in Language:
            path = Path(I18N_DIR, f"{language.value}.lng")
            self._bundles[language] = self._load_lng(path)
            logger.log_event(
                "I18N_BUNDLE_LOADED",
                level=20,
                language=language.value,
                file=path.name,
                entries=len(self._bundles[language]),
            )

    @staticmethod
    def _load_lng(path: Path) -> dict[str, str]:
        """Execute load lng.
        
        Args:
            path: Input value used by this operation.
        
        Returns:
            Result produced by this operation.
        """
        data: dict[str, str] = {}
        with path.open("r", encoding="utf-8") as file:
            for raw_line in file:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                data[key.strip()] = value.strip()
        return data
