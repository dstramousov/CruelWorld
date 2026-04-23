from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class LightEmitterComponent:
    enabled: bool = True
    radius: float = 72.0
