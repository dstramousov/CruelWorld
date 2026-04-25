"""Tilemap module for tile map, zone, spawning, and world-state helpers."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class TileLayer:
    """A simple tile layer."""

    name: str
    width: int
    height: int
    tiles: list[int]


@dataclass(slots=True)
class MapObject:
    """A generic object loaded from Tiled."""

    name: str
    type_name: str
    x: float
    y: float
    width: float
    height: float
    properties: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class TileMap:
    """Container for map data loaded from Tiled."""

    map_id: str
    width: int
    height: int
    tile_width: int
    tile_height: int
    layers: dict[str, TileLayer] = field(default_factory=dict)
    object_layers: dict[str, list[MapObject]] = field(default_factory=dict)

    @property
    def pixel_width(self) -> int:
        """Execute pixel width.
        
        Returns:
            Result produced by this operation.
        """
        return self.width * self.tile_width

    @property
    def pixel_height(self) -> int:
        """Execute pixel height.
        
        Returns:
            Result produced by this operation.
        """
        return self.height * self.tile_height
