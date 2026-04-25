from __future__ import annotations

import sys
import types


def _install_raylib_stub() -> None:
    raylib_stub = types.SimpleNamespace(
        KEY_F1=290,
        KEY_LEFT_SHIFT=340,
        KEY_RIGHT_SHIFT=344,
        KEY_D=68,
        KEY_Q=81,
        KEY_E=69,
        KEY_A=65,
        KEY_F=70,
        KEY_LEFT=263,
        KEY_RIGHT=262,
        KEY_SPACE=32,
        KEY_W=87,
        KEY_UP=265,
        KEY_DOWN=264,
        KEY_S=83,
        KEY_J=74,
        KEY_L=76,
        KEY_TAB=258,
        KEY_ESCAPE=256,
        KEY_ENTER=257,
        KEY_BACKSPACE=259,
        FLAG_VSYNC_HINT=64,
        FILTER_POINT=0,
        FILTER_BILINEAR=1,
    )
    sys.modules.setdefault("raylib", raylib_stub)


_install_raylib_stub()

from src.ui.hud import Hud  # noqa: E402


def test_top_panel_width_is_centered_for_larger_render_target() -> None:
    hud = Hud()
    panel_width = hud._resolve_panel_width(1280)

    assert panel_width == 624
    assert hud._center_x(panel_width, 1280) == 328


def test_top_panel_width_is_clamped_for_small_render_target() -> None:
    hud = Hud()
    panel_width = hud._resolve_panel_width(320)

    assert panel_width == 304
    assert hud._center_x(panel_width, 320) == 8
