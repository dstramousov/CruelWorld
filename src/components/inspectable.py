"""Inspectable module for component data containers used by entities and systems."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class InspectableComponent:
    """Represent the InspectableComponent runtime concept."""
    description_key: str = ""
