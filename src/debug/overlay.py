from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.ui.text_renderer import text_renderer
from src.utils import colors
from src.utils import rl as raylib


@dataclass(slots=True)
class DebugOverlayLayout:
    mode: str = "full_window"
    padding: int = 12
    margin: int = 8
    font_size: int = 8
    line_height: int = 10
    min_width: int = 320
    min_height: int = 120


class DebugOverlay:
    def __init__(self, layout: dict | None = None, enabled: bool = False) -> None:
        self.enabled = enabled
        layout = layout or {}
        self.layout = DebugOverlayLayout(
            mode=str(layout.get("mode", "full_window")),
            padding=int(layout.get("padding", 12)),
            margin=int(layout.get("margin", 8)),
            font_size=int(layout.get("font_size", 8)),
            line_height=int(layout.get("line_height", 10)),
            min_width=int(layout.get("min_width", 320)),
            min_height=int(layout.get("min_height", 120)),
        )

    def toggle(self) -> None:
        self.enabled = not self.enabled

    def draw(self, lines: Iterable[str], window_width: int, window_height: int) -> None:
        if not self.enabled:
            return

        normalized_lines = list(lines)
        rect_x, rect_y, rect_width, rect_height = self._resolve_rect(window_width, window_height)
        line_limit = max(1, (rect_height - self.layout.padding * 2) // self.layout.line_height)
        visible_lines = normalized_lines[:line_limit]

        raylib.draw_rectangle(rect_x, rect_y, rect_width, rect_height, colors.PANEL_BG)
        for index, line in enumerate(visible_lines):
            text_renderer.draw(
                line,
                rect_x + self.layout.padding,
                rect_y + self.layout.padding + index * self.layout.line_height,
                self.layout.font_size,
                colors.TEXT,
            )

    def _resolve_rect(self, window_width: int, window_height: int) -> tuple[int, int, int, int]:
        mode = self.layout.mode
        margin = self.layout.margin
        min_width = self.layout.min_width
        min_height = self.layout.min_height

        if mode == "half_window_bottom":
            rect_width = max(min_width, window_width)
            rect_height = max(min_height, window_height // 2)
            rect_x = 0
            rect_y = window_height - rect_height
            return rect_x, rect_y, rect_width, rect_height

        if mode == "half_window_left":
            rect_width = max(min_width, window_width // 2)
            rect_height = max(min_height, window_height)
            rect_x = 0
            rect_y = 0
            return rect_x, rect_y, rect_width, rect_height

        rect_width = max(min_width, window_width - margin * 2)
        rect_height = max(min_height, window_height - margin * 2)
        rect_x = margin
        rect_y = margin
        return rect_x, rect_y, rect_width, rect_height
