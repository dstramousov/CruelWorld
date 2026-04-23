from __future__ import annotations

from src.ui.text_renderer import text_renderer
from src.utils import colors
from src.utils import rl as raylib


class Hud:
    def draw(
        self,
        health_text: str,
        status_text: str,
        hint_text: str,
        interaction_text: str,
        message_text: str,
    ) -> None:
        raylib.draw_rectangle(8, 8, 624, 42, colors.PANEL_BG)
        text_renderer.draw(health_text, 14, 14, 8, colors.TEXT)
        text_renderer.draw(status_text, 210, 14, 8, colors.WARNING)
        if interaction_text:
            text_renderer.draw(interaction_text, 14, 25, 8, colors.ACCENT)
        elif hint_text:
            text_renderer.draw(hint_text, 14, 25, 8, colors.TEXT)
        if message_text:
            raylib.draw_rectangle(144, 330, 352, 20, colors.PANEL_BG)
            text_renderer.draw(message_text, 154, 336, 8, colors.TEXT)
