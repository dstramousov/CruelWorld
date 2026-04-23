from __future__ import annotations


def lerp(current: float, target: float, factor: float) -> float:
    return current + (target - current) * factor
