from __future__ import annotations

from src.ui.text_renderer import TextRenderer


def test_build_codepoints_contains_ascii_ukrainian_and_localized_characters() -> None:
    renderer = TextRenderer()

    codepoints = renderer._build_codepoints(["Ґанок Єнот їжак", "Scavenger #1"])

    assert ord("A") in codepoints
    assert ord("Ґ") in codepoints
    assert ord("ї") in codepoints
    assert ord("#") in codepoints
    assert ord("\n") not in codepoints
    assert codepoints == sorted(codepoints)


def test_measure_width_returns_zero_for_empty_text() -> None:
    renderer = TextRenderer()

    assert renderer.measure_width("", 8) == 0.0
