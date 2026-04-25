"""Hud module for user interface widgets and overlays."""

from __future__ import annotations

from src.ui.text_renderer import text_renderer
from src.utils import colors
from src.utils import rl as raylib


class Hud:
    """Draw the in-game HUD and contextual screen messages."""

    _FONT_SIZE = 8
    _MARGIN = 8
    _PADDING_X = 8
    _TOP_PANEL_HEIGHT = 42
    _BOTTOM_PANEL_HEIGHT = 20
    _BOTTOM_GAP = 4
    _MAX_PANEL_WIDTH = 624

    def draw(
        self,
        health_text: str,
        status_text: str,
        hint_text: str,
        interaction_text: str,
        message_text: str,
        internal_width: int = 640,
        internal_height: int = 360,
    ) -> None:
        """Draw the gameplay HUD.

        Args:
            health_text: Localized player health text.
            status_text: Localized active status text.
            hint_text: Localized controls hint text.
            interaction_text: Localized contextual interaction text.
            message_text: Localized temporary message text.
            internal_width: Internal render target width in pixels.
            internal_height: Internal render target height in pixels.
        """
        self._draw_top_panel(health_text, status_text, hint_text, internal_width)
        self._draw_bottom_messages(interaction_text, message_text, internal_width, internal_height)

    def _draw_top_panel(
        self,
        health_text: str,
        status_text: str,
        hint_text: str,
        internal_width: int,
    ) -> None:
        """Draw the centered top HUD panel."""
        panel_width = self._resolve_panel_width(internal_width)
        panel_x = self._center_x(panel_width, internal_width)
        panel_y = self._MARGIN

        raylib.draw_rectangle(panel_x, panel_y, panel_width, self._TOP_PANEL_HEIGHT, colors.PANEL_BG)

        text_y = panel_y + 6
        text_renderer.draw(health_text, panel_x + self._PADDING_X, text_y, self._FONT_SIZE, colors.TEXT)

        status_width = int(text_renderer.measure_width(status_text, self._FONT_SIZE))
        status_x = panel_x + panel_width - status_width - self._PADDING_X
        text_renderer.draw(status_text, status_x, text_y, self._FONT_SIZE, colors.WARNING)

        if hint_text:
            hint_x = self._center_text_x(hint_text, internal_width)
            text_renderer.draw(hint_text, hint_x, panel_y + 23, self._FONT_SIZE, colors.TEXT)

    def _draw_bottom_messages(
        self,
        interaction_text: str,
        message_text: str,
        internal_width: int,
        internal_height: int,
    ) -> None:
        """Draw centered bottom messages from bottom to top."""
        next_y = internal_height - self._MARGIN - self._BOTTOM_PANEL_HEIGHT

        if interaction_text:
            self._draw_centered_bottom_panel(interaction_text, internal_width, next_y, colors.ACCENT)
            next_y -= self._BOTTOM_PANEL_HEIGHT + self._BOTTOM_GAP

        if message_text:
            self._draw_centered_bottom_panel(message_text, internal_width, next_y, colors.TEXT)

    def _draw_centered_bottom_panel(
        self,
        text: str,
        internal_width: int,
        y: int,
        color: tuple[int, int, int, int],
    ) -> None:
        """Draw one centered bottom text panel."""
        text_width = int(text_renderer.measure_width(text, self._FONT_SIZE))
        panel_width = min(
            max(text_width + self._PADDING_X * 2, 96),
            max(96, internal_width - self._MARGIN * 2),
        )
        panel_x = self._center_x(panel_width, internal_width)
        text_x = panel_x + max(self._PADDING_X, (panel_width - text_width) // 2)

        raylib.draw_rectangle(panel_x, y, panel_width, self._BOTTOM_PANEL_HEIGHT, colors.PANEL_BG)
        text_renderer.draw(text, text_x, y + 6, self._FONT_SIZE, color)

    def _resolve_panel_width(self, internal_width: int) -> int:
        """Return the top panel width constrained by the render size."""
        available_width = max(1, internal_width - self._MARGIN * 2)
        return min(self._MAX_PANEL_WIDTH, available_width)

    @staticmethod
    def _center_x(width: int, internal_width: int) -> int:
        """Return a centered x coordinate for a fixed-width rectangle."""
        return max(0, (internal_width - width) // 2)

    def _center_text_x(self, text: str, internal_width: int) -> int:
        """Return a centered x coordinate for rendered text."""
        text_width = int(text_renderer.measure_width(text, self._FONT_SIZE))
        return self._center_x(text_width, internal_width)
