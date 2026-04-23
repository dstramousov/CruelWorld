from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ColliderComponent:
    width: float
    height: float
