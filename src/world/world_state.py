"""World State module for tile map, zone, spawning, and world-state helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class WorldState:
    """Represent the WorldState runtime concept."""
    player_name: str = "Survivor"
    current_scene: str = "vertical_slice_01"
    current_zone: str = "landing_margin"
    weather: str = "clear"
    time_of_day: str = "day"
    time_hours: float = 12.0
    current_map_id: str = "vertical_slice_01"
    slice_completed: bool = False
