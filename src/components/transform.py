from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TransformComponent:
    x: float
    y: float
