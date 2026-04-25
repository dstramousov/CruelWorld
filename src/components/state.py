"""State module for component data containers used by entities and systems."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class StateComponent:
    """Represent the StateComponent runtime concept."""
    name: str = "idle"
    flags: set[str] = field(default_factory=set)
