from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, is_dataclass
from fnmatch import fnmatchcase
from pathlib import Path
from pprint import pformat
from typing import Any

from src.utils.paths import CONFIG_DIR, LOGS_DIR


_BIOTA_LOGGING_ENABLED = True


class ProjectLogger(logging.Logger):
    """Application logger with convenience helpers for structured text events."""

    def log_event(self, event_name: str, level: int = logging.DEBUG, **kwargs: Any) -> None:
        self.log(level, _compose_message(event_name, kwargs))

    def log_state(self, state_name: str, level: int = logging.DEBUG, **kwargs: Any) -> None:
        self.log(level, _compose_message(state_name, kwargs))

    def log_object(self, object_name: str, obj: Any, level: int = logging.DEBUG) -> None:
        payload = serialize_object(obj)
        self.log(level, "%s | %s", object_name, payload)

    def log_exception_event(self, event_name: str, exc: BaseException, **kwargs: Any) -> None:
        payload = dict(kwargs)
        payload["exception"] = f"{type(exc).__name__}: {exc}"
        self.exception(_compose_message(event_name, payload))

    def log_biota_event(
        self,
        species_key: str,
        event_name: str,
        *,
        level: int = logging.DEBUG,
        entity_kind: str = "flora",
        entity_id: str | None = None,
        enabled: bool | None = None,
        **kwargs: Any,
    ) -> None:
        """Log a biota-specific event with semantic tags for color rules and filtering."""
        should_log = _BIOTA_LOGGING_ENABLED if enabled is None else enabled
        if not should_log:
            return

        normalized_kind = _normalize_token(entity_kind)
        normalized_species = _normalize_token(species_key)
        normalized_event = _normalize_token(event_name)
        payload = dict(kwargs)
        if entity_id is not None:
            payload.setdefault("entity", entity_id)
        message = _compose_message(
            f"BIOTA_{normalized_kind}_{normalized_species}_{normalized_event}",
            payload,
        )
        self.log(level, message, extra={"is_biota": True})


logging.setLoggerClass(ProjectLogger)


class ColorRule:
    """Semantic color rule matched against the rendered log message."""

    def __init__(self, pattern: str, match_type: str, color: str) -> None:
        self.pattern = pattern
        self.match_type = match_type.lower()
        self.color = color.upper()
        self._regex = re.compile(pattern) if self.match_type == "regex" else None

    def matches(self, message: str) -> bool:
        if self.match_type == "glob":
            return fnmatchcase(message, self.pattern)
        if self.match_type == "contains":
            return self.pattern in message
        if self.match_type == "regex":
            return bool(self._regex and self._regex.search(message))
        return False


class SemanticColorFormatter(logging.Formatter):
    """Formatter that colors entire log lines using severity and semantic rules."""

    ANSI = {
        "RESET": "\033[0m",
        "BLACK": "\033[30m",
        "RED": "\033[31m",
        "GREEN": "\033[32m",
        "YELLOW": "\033[33m",
        "BLUE": "\033[34m",
        "MAGENTA": "\033[35m",
        "CYAN": "\033[36m",
        "WHITE": "\033[37m",
        "BRIGHT_BLACK": "\033[90m",
        "BRIGHT_RED": "\033[91m",
        "BRIGHT_GREEN": "\033[92m",
        "BRIGHT_YELLOW": "\033[93m",
        "BRIGHT_BLUE": "\033[94m",
        "BRIGHT_MAGENTA": "\033[95m",
        "BRIGHT_CYAN": "\033[96m",
        "BRIGHT_WHITE": "\033[97m",
    }

    def __init__(
        self,
        fmt: str,
        *,
        level_colors: dict[str, str],
        message_rules: list[ColorRule],
        enable_colors: bool,
    ) -> None:
        super().__init__(fmt)
        self._level_colors = {key.upper(): value.upper() for key, value in level_colors.items()}
        self._message_rules = message_rules
        self._enable_colors = enable_colors

    def format(self, record: logging.LogRecord) -> str:
        rendered = super().format(record)
        if not self._enable_colors:
            return rendered

        message = record.getMessage()
        color_name = self._resolve_color(record.levelname, message)
        if not color_name:
            return rendered

        prefix = self.ANSI.get(color_name)
        reset = self.ANSI["RESET"]
        if not prefix:
            return rendered
        return f"{prefix}{rendered}{reset}"

    def _resolve_color(self, level_name: str, message: str) -> str | None:
        for rule in self._message_rules:
            if rule.matches(message):
                return rule.color
        return self._level_colors.get(level_name.upper())


class BiotaOnlyFilter(logging.Filter):
    """Allow only biota-tagged records through the handler."""

    def filter(self, record: logging.LogRecord) -> bool:
        return bool(getattr(record, "is_biota", False))


class ExcludeBiotaFilter(logging.Filter):
    """Optional filter to keep general logs cleaner if desired later."""

    def filter(self, record: logging.LogRecord) -> bool:
        return True


def get_logger(name: str) -> ProjectLogger:
    """Return a project logger with helper methods."""
    return logging.getLogger(name)  # type: ignore[return-value]


def serialize_object(obj: Any) -> str:
    """Serialize an object into a readable, single-line string."""
    if is_dataclass(obj):
        return pformat(asdict(obj), compact=True, sort_dicts=True)
    if hasattr(obj, "__dict__"):
        safe_dict = {
            key: value
            for key, value in vars(obj).items()
            if not key.startswith("_")
        }
        return pformat(safe_dict, compact=True, sort_dicts=True)
    if isinstance(obj, dict):
        return pformat(obj, compact=True, sort_dicts=True)
    if isinstance(obj, (list, tuple, set)):
        return pformat(obj, compact=True, sort_dicts=True)
    return repr(obj)


def configure_logging(config_path: Path | None = None) -> None:
    """Configure root logging from project config."""
    global _BIOTA_LOGGING_ENABLED

    config_file = config_path or CONFIG_DIR / "logging.json"
    config = json.loads(config_file.read_text(encoding="utf-8"))

    logging_cfg = config.get("logging", {})
    level_name = logging_cfg.get("level", "DEBUG").upper()
    console_colors = bool(logging_cfg.get("console_colors", True))
    file_logging = bool(logging_cfg.get("file_logging", True))
    ansi_in_file = bool(logging_cfg.get("ansi_in_file", True))
    show_timestamp = bool(logging_cfg.get("show_timestamp", True))
    show_level = bool(logging_cfg.get("show_level", True))
    show_logger_name = bool(logging_cfg.get("show_logger_name", True))

    biota_cfg = config.get("biota_logging", {})
    _BIOTA_LOGGING_ENABLED = bool(biota_cfg.get("enabled", True))
    biota_console_echo = bool(biota_cfg.get("console_echo", True))
    biota_file_logging = bool(biota_cfg.get("separate_file", True))
    biota_ansi_in_file = bool(biota_cfg.get("ansi_in_file", ansi_in_file))

    level_colors = config.get(
        "level_colors",
        {
            "DEBUG": "BRIGHT_BLACK",
            "INFO": "GREEN",
            "WARNING": "YELLOW",
            "ERROR": "RED",
            "CRITICAL": "BRIGHT_RED",
        },
    )
    message_rules = [
        ColorRule(
            pattern=item.get("pattern", ""),
            match_type=item.get("match", "glob"),
            color=item.get("color", "WHITE"),
        )
        for item in config.get("message_color_rules", [])
        if item.get("pattern")
    ]

    fmt_parts: list[str] = []
    if show_timestamp:
        fmt_parts.append("[%(asctime)s]")
    if show_level:
        fmt_parts.append("[%(levelname)s]")
    if show_logger_name:
        fmt_parts.append("[%(name)s]")
    fmt_parts.append("%(message)s")
    base_format = " ".join(fmt_parts)

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(level_name)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level_name)
    console_handler.setFormatter(
        SemanticColorFormatter(
            base_format,
            level_colors=level_colors,
            message_rules=message_rules,
            enable_colors=console_colors,
        )
    )
    if not biota_console_echo:
        console_handler.addFilter(ExcludeBiotaFilter())
    root_logger.addHandler(console_handler)

    if file_logging:
        file_formatter = SemanticColorFormatter(
            base_format,
            level_colors=level_colors,
            message_rules=message_rules,
            enable_colors=ansi_in_file,
        )
        game_handler = logging.FileHandler(LOGS_DIR / "game.log", encoding="utf-8")
        game_handler.setLevel(level_name)
        game_handler.setFormatter(file_formatter)
        root_logger.addHandler(game_handler)

        debug_handler = logging.FileHandler(LOGS_DIR / "debug.log", encoding="utf-8")
        debug_handler.setLevel("DEBUG")
        debug_handler.setFormatter(file_formatter)
        root_logger.addHandler(debug_handler)

        if biota_file_logging:
            biota_formatter = SemanticColorFormatter(
                base_format,
                level_colors=level_colors,
                message_rules=message_rules,
                enable_colors=biota_ansi_in_file,
            )
            biota_handler = logging.FileHandler(LOGS_DIR / "biota.log", encoding="utf-8")
            biota_handler.setLevel("DEBUG")
            biota_handler.setFormatter(biota_formatter)
            biota_handler.addFilter(BiotaOnlyFilter())
            root_logger.addHandler(biota_handler)

        crash_handler = logging.FileHandler(LOGS_DIR / "crash.log", encoding="utf-8")
        crash_handler.setLevel("ERROR")
        crash_handler.setFormatter(logging.Formatter(base_format))
        root_logger.addHandler(crash_handler)

    get_logger(__name__).log_event(
        "LOGGING_CONFIGURED",
        level=logging.INFO,
        level_name=level_name,
        console_colors=console_colors,
        file_logging=file_logging,
        ansi_in_file=ansi_in_file,
        biota_logging=_BIOTA_LOGGING_ENABLED,
        biota_file_logging=biota_file_logging,
    )

def is_biota_logging_enabled() -> bool:
    """Expose current biota logging toggle for runtime systems."""
    return _BIOTA_LOGGING_ENABLED


def _compose_message(name: str, payload: dict[str, Any]) -> str:
    if not payload:
        return name
    fragments = [f"{key}={serialize_object(value)}" for key, value in payload.items()]
    return f"{name} | " + " | ".join(fragments)


def _normalize_token(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_")
    return normalized.upper() or "UNKNOWN"
