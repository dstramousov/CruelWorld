"""Interaction module for component data containers used by entities and systems."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class InteractionComponent:
    """Describes a simple interaction behavior."""

    interaction_id: str = "none"
    prompt_key: str = "hint.interact"
    message_key: str = "msg.interaction_used"
    discovery_key: str = ""
    clears_statuses: list[str] = field(default_factory=list)
    applies_statuses: list[str] = field(default_factory=list)
    health_delta: int = 0
    single_use: bool = True
