from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class GravityComponent:
    value: float = 900.0
