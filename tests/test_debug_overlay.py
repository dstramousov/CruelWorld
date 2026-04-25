from __future__ import annotations

from src.debug.overlay import DebugOverlay


def test_debug_overlay_reads_value_color_from_config() -> None:
    overlay = DebugOverlay({"value_color": [255, 128, 32, 255]})

    assert overlay.layout.value_color == (255, 128, 32, 255)


def test_debug_overlay_clamps_invalid_color_channels() -> None:
    overlay = DebugOverlay({"value_color": [-10, 512, 32.8, "64"]})

    assert overlay.layout.value_color == (0, 255, 32, 64)


def test_debug_overlay_falls_back_for_invalid_color_config() -> None:
    overlay = DebugOverlay({"value_color": "orange"})

    assert overlay.layout.value_color == (255, 170, 64, 255)


def test_debug_overlay_resolves_full_window_rect() -> None:
    overlay = DebugOverlay({"margin": 8, "min_width": 100, "min_height": 50})

    assert overlay._resolve_rect(320, 180) == (8, 8, 304, 164)
