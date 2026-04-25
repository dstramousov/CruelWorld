"""Enums module for shared utility functions and wrappers."""

from __future__ import annotations

from enum import StrEnum


class Language(StrEnum):
    """Represent supported localization languages."""

    ENG = "eng"
    UKR = "ukr"
    RUS = "rus"
