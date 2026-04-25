"""Math2D module for shared utility functions and wrappers."""

from __future__ import annotations


def lerp(current: float, target: float, factor: float) -> float:
    """Execute lerp.
    
    Args:
        current: Input value used by this operation.
        target: Input value used by this operation.
        factor: Input value used by this operation.
    
    Returns:
        Result produced by this operation.
    """
    return current + (target - current) * factor
