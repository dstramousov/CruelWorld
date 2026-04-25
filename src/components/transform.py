"""Transform module for component data containers used by entities and systems."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TransformComponent:
    """Represent the TransformComponent runtime concept."""
    x: float
    y: float
