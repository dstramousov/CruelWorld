"""Zone module for tile map, zone, spawning, and world-state helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Zone:
    """Minimal zone descriptor."""

    zone_id: str
    name_key: str
    map_path: str
    camera_profile_default: str
