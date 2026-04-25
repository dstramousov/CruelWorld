"""Gravity module for component data containers used by entities and systems."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class GravityComponent:
    """Represent the GravityComponent runtime concept."""
    value: float = 900.0
