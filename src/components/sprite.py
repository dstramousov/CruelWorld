"""Sprite module for component data containers used by entities and systems."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SpriteComponent:
    """Represent the SpriteComponent runtime concept."""
    width: int
    height: int
