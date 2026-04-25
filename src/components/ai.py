"""Ai module for component data containers used by entities and systems."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AIComponent:
    """Represent the AIComponent runtime concept."""
    behavior: str = "idle"
