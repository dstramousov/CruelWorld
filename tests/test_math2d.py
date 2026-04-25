from __future__ import annotations

from src.utils.math2d import lerp


def test_lerp_returns_current_when_factor_is_zero() -> None:
    assert lerp(10.0, 20.0, 0.0) == 10.0


def test_lerp_returns_target_when_factor_is_one() -> None:
    assert lerp(10.0, 20.0, 1.0) == 20.0


def test_lerp_supports_extrapolation_when_factor_is_outside_unit_range() -> None:
    assert lerp(10.0, 20.0, 1.5) == 25.0
