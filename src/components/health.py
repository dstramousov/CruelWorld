"""Health module for component data containers used by entities and systems."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class HealthComponent:
    """Represent the HealthComponent runtime concept."""
    current: int = 100
    maximum: int = 100
