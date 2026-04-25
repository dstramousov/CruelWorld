"""Velocity module for component data containers used by entities and systems."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class VelocityComponent:
    """Represent the VelocityComponent runtime concept."""
    x: float = 0.0
    y: float = 0.0
