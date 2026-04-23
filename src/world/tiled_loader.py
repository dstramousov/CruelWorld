from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from src.systems.log_system import get_logger
from src.world.tilemap import MapObject, TileLayer, TileMap

logger = get_logger(__name__)


class TiledLoader:
    """Loads a minimal subset of TMX maps exported from Tiled."""

    @staticmethod
    def load(path: Path) -> TileMap:
        root = ET.parse(path).getroot()
        width = int(root.attrib["width"])
        height = int(root.attrib["height"])
        tile_width = int(root.attrib["tilewidth"])
        tile_height = int(root.attrib["tileheight"])
        map_id = path.stem
        tile_map = TileMap(
            map_id=map_id,
            width=width,
            height=height,
            tile_width=tile_width,
            tile_height=tile_height,
        )

        for layer_node in root.findall("layer"):
            data_node = layer_node.find("data")
            csv_data = data_node.text or ""
            tiles = [int(value.strip()) for value in csv_data.replace("\n", "").split(",") if value.strip()]
            layer = TileLayer(
                name=layer_node.attrib["name"],
                width=int(layer_node.attrib["width"]),
                height=int(layer_node.attrib["height"]),
                tiles=tiles,
            )
            tile_map.layers[layer.name] = layer

        for group_node in root.findall("objectgroup"):
            objects: list[MapObject] = []
            for object_node in group_node.findall("object"):
                properties: dict[str, str] = {}
                properties_node = object_node.find("properties")
                if properties_node is not None:
                    for prop in properties_node.findall("property"):
                        properties[prop.attrib["name"]] = prop.attrib.get("value", "")
                objects.append(
                    MapObject(
                        name=object_node.attrib.get("name", ""),
                        type_name=object_node.attrib.get("type", ""),
                        x=float(object_node.attrib.get("x", 0.0)),
                        y=float(object_node.attrib.get("y", 0.0)),
                        width=float(object_node.attrib.get("width", 0.0)),
                        height=float(object_node.attrib.get("height", 0.0)),
                        properties=properties,
                    )
                )
            tile_map.object_layers[group_node.attrib["name"]] = objects

        logger.log_event(
            "MAP_LOADED",
            level=20,
            map_id=map_id,
            width=width,
            height=height,
            tile_width=tile_width,
            tile_height=tile_height,
            tile_layers=len(tile_map.layers),
            object_layers=len(tile_map.object_layers),
        )
        return tile_map
