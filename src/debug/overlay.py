"""Debug overlay rendering helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.ui.text_renderer import text_renderer
from src.utils import colors
from src.utils import rl as raylib

Color = tuple[int, int, int, int]


@dataclass(slots=True)
class DebugOverlayLayout:
    """Store debug overlay layout and text color configuration.

    Attributes:
        mode: Overlay placement mode.
        padding: Inner padding in pixels.
        margin: Outer margin in pixels.
        font_size: Overlay text size.
        line_height: Vertical distance between lines.
        min_width: Minimum overlay width.
        min_height: Minimum overlay height.
        label_color: Color for field names and static text.
        value_color: Color for values after the first colon.
    """

    mode: str = "full_window"
    padding: int = 12
    margin: int = 8
    font_size: int = 8
    line_height: int = 10
    min_width: int = 320
    min_height: int = 120
    label_color: Color = colors.TEXT
    value_color: Color = (255, 170, 64, 255)


class DebugOverlay:
    """Draw the developer debug overlay."""

    def __init__(self, layout: dict | None = None, enabled: bool = False) -> None:
        """Initialize the overlay from configuration.

        Args:
            layout: Debug overlay layout and color configuration.
            enabled: Whether the overlay is visible by default.
        """
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
            label_color=self._parse_color(layout.get("label_color"), colors.TEXT),
            value_color=self._parse_color(layout.get("value_color"), (255, 170, 64, 255)),
        )

    def toggle(self) -> None:
        """Toggle overlay visibility."""
        self.enabled = not self.enabled

    def draw(self, lines: Iterable[str], window_width: int, window_height: int) -> None:
        """Draw visible overlay lines.

        Args:
            lines: Overlay text lines.
            window_width: Current window width.
            window_height: Current window height.
        """
        if not self.enabled:
            return

        normalized_lines = list(lines)
        rect_x, rect_y, rect_width, rect_height = self._resolve_rect(window_width, window_height)
        line_limit = max(1, (rect_height - self.layout.padding * 2) // self.layout.line_height)
        visible_lines = normalized_lines[:line_limit]

        raylib.draw_rectangle(rect_x, rect_y, rect_width, rect_height, colors.PANEL_BG)
        for index, line in enumerate(visible_lines):
            self._draw_line(
                line,
                rect_x + self.layout.padding,
                rect_y + self.layout.padding + index * self.layout.line_height,
            )

    def _draw_line(self, line: str, x: int, y: int) -> None:
        """Draw one line with a highlighted value segment.

        Args:
            line: Text line to draw.
            x: Start X coordinate.
            y: Start Y coordinate.
        """
        label, separator, value = line.partition(":")
        if not separator:
            text_renderer.draw(line, x, y, self.layout.font_size, self.layout.label_color)
            return

        label_text = f"{label}{separator}"
        text_renderer.draw(label_text, x, y, self.layout.font_size, self.layout.label_color)
        value_x = x + round(text_renderer.measure_width(label_text, self.layout.font_size))
        text_renderer.draw(value, value_x, y, self.layout.font_size, self.layout.value_color)

    def _resolve_rect(self, window_width: int, window_height: int) -> tuple[int, int, int, int]:
        """Resolve overlay rectangle in window coordinates.

        Args:
            window_width: Current window width.
            window_height: Current window height.

        Returns:
            Rectangle as ``x, y, width, height``.
        """
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

    @staticmethod
    def _parse_color(value: object, fallback: Color) -> Color:
        """Parse RGBA color values from config.

        Args:
            value: Config value expected to be a 4-item sequence.
            fallback: Color returned when config value is invalid.

        Returns:
            Parsed RGBA tuple.
        """
        if not isinstance(value, (list, tuple)) or len(value) != 4:
            return fallback
        try:
            channels = tuple(max(0, min(255, int(channel))) for channel in value)
        except (TypeError, ValueError):
            return fallback
        return channels  # type: ignore[return-value]
