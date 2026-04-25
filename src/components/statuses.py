"""Statuses module for component data containers used by entities and systems."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class StatusInstance:
    """Runtime status effect data."""

    status_id: str
    remaining: float
    tick_interval: float
    next_tick_in: float
    tick_damage: int = 0


@dataclass(slots=True)
class StatusReceiverComponent:
    """Container for active status effects."""

    active: dict[str, StatusInstance] = field(default_factory=dict)

    def names(self) -> list[str]:
        """Return active status identifiers."""
        return list(self.active.keys())
