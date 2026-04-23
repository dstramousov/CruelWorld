from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class StateComponent:
    name: str = "idle"
    flags: set[str] = field(default_factory=set)
