"""Collider module for component data containers used by entities and systems."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ColliderComponent:
    """Represent the ColliderComponent runtime concept."""
    width: float
    height: float
