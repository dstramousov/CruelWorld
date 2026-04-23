from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SpriteComponent:
    width: int
    height: int
