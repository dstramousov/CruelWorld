from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class InteractionComponent:
    """Describes a simple interaction behavior."""

    interaction_id: str = "none"
    prompt_key: str = "hint.interact"
    clears_statuses: list[str] = field(default_factory=list)
