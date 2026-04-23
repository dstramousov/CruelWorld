from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class HealthComponent:
    current: int = 100
    maximum: int = 100
