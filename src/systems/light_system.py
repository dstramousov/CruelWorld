"""Flashlight mode logic and drawing helpers."""

from __future__ import annotations

from src.components.light_emitter import LightEmitterComponent
from src.utils import colors
from src.utils import rl as raylib


class LightSystem:
    """Control player flashlight modes and draw their current visual state."""

    MODES: tuple[str, ...] = ("off", "radial", "beam")

    def cycle_mode(self, light: LightEmitterComponent) -> str:
        """Switch the flashlight to the next configured mode.

        Args:
            light: Light component to modify.

        Returns:
            Newly selected flashlight mode.
        """
        try:
            current_index = self.MODES.index(light.mode)
        except ValueError:
            current_index = 0
        light.mode = self.MODES[(current_index + 1) % len(self.MODES)]
        return light.mode

    def draw_player_flashlight(
        self,
        *,
        light: LightEmitterComponent,
        screen_x: int,
        screen_y: int,
        player_height: int,
        facing: float,
        zoom: float,
    ) -> None:
        """Draw the player's flashlight in internal render coordinates.

        Args:
            light: Player light component.
            screen_x: Player anchor X on screen.
            screen_y: Player feet Y on screen.
            player_height: Player rendered height in pixels.
            facing: Horizontal facing direction; negative means left, positive means right.
            zoom: Active camera zoom.
        """
        if not light.enabled or light.mode == "off":
            return

        origin_x = int(screen_x)
        origin_y = int(screen_y - player_height * 0.58)
        if light.mode == "radial":
            raylib.draw_circle(origin_x, origin_y, light.radius * zoom, colors.FLASHLIGHT_RADIAL)
            return

        if light.mode == "beam":
            self._draw_beam(light, origin_x, origin_y, facing, zoom)

    def _draw_beam(
        self,
        light: LightEmitterComponent,
        origin_x: int,
        origin_y: int,
        facing: float,
        zoom: float,
    ) -> None:
        """Draw a triangular flashlight beam.

        Args:
            light: Player light component.
            origin_x: Beam origin X in screen pixels.
            origin_y: Beam origin Y in screen pixels.
            facing: Horizontal facing direction.
            zoom: Active camera zoom.
        """
        points = self.build_beam_points(light, origin_x, origin_y, facing, zoom)
        raylib.draw_triangle(
            points[0][0],
            points[0][1],
            points[1][0],
            points[1][1],
            points[2][0],
            points[2][1],
            colors.FLASHLIGHT_BEAM,
        )

    @staticmethod
    def build_beam_points(
        light: LightEmitterComponent,
        origin_x: int,
        origin_y: int,
        facing: float,
        zoom: float,
    ) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int]]:
        """Build flashlight beam triangle points with stable winding.

        Raylib's triangle drawing can be sensitive to point winding. The beam
        uses a clockwise vertex order for both horizontal directions so the
        shape remains visible when the player faces left or right.

        Args:
            light: Player light component.
            origin_x: Beam origin X in screen pixels.
            origin_y: Beam origin Y in screen pixels.
            facing: Horizontal facing direction.
            zoom: Active camera zoom.

        Returns:
            Three triangle points in draw order.
        """
        direction = -1.0 if facing < 0.0 else 1.0
        distance = light.beam_distance * zoom
        half_width = light.beam_half_width * zoom
        end_x = origin_x + int(round(distance * direction))
        top_y = origin_y - int(round(half_width))
        bottom_y = origin_y + int(round(half_width))

        if direction > 0.0:
            return ((origin_x, origin_y), (end_x, bottom_y), (end_x, top_y))
        return ((origin_x, origin_y), (end_x, top_y), (end_x, bottom_y))
