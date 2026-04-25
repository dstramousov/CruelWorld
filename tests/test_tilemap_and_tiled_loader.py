from __future__ import annotations

from pathlib import Path

from src.utils.paths import resolve_project_path
from src.world.tiled_loader import TiledLoader
from src.world.tilemap import TileMap


def test_tilemap_pixel_dimensions_are_derived_from_tile_size() -> None:
    tile_map = TileMap(map_id="test", width=10, height=5, tile_width=16, tile_height=8)

    assert tile_map.pixel_width == 160
    assert tile_map.pixel_height == 40


def test_tiled_loader_loads_project_start_map_layers_and_objects() -> None:
    tile_map = TiledLoader.load(resolve_project_path("assets/maps/vertical_slice_01.tmx"))

    assert tile_map.map_id == "vertical_slice_01"
    assert tile_map.width == 360
    assert tile_map.height == 36
    assert tile_map.layers["ground"].width == tile_map.width
    assert tile_map.layers["ground"].height == tile_map.height
    assert len(tile_map.layers["ground"].tiles) == tile_map.width * tile_map.height
    assert "spawns_player" in tile_map.object_layers
    assert "interactables" in tile_map.object_layers


def test_tiled_loader_reads_object_properties(tmp_path: Path) -> None:
    tmx_path = tmp_path / "test_map.tmx"
    csv_values = ",".join(["0"] * 4)
    tmx_path.write_text(
        f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<map version=\"1.10\" tiledversion=\"1.10.2\" orientation=\"orthogonal\" renderorder=\"right-down\" width=\"2\" height=\"2\" tilewidth=\"16\" tileheight=\"16\" infinite=\"0\">
 <layer id=\"1\" name=\"ground\" width=\"2\" height=\"2\"><data encoding=\"csv\">{csv_values}</data></layer>
 <objectgroup id=\"2\" name=\"interactables\">
  <object id=\"1\" name=\"blue_mercy_gourd_01\" type=\"resource\" x=\"8\" y=\"12\" width=\"16\" height=\"16\">
   <properties><property name=\"journal\" value=\"disc.blue_mercy_gourd\"/></properties>
  </object>
 </objectgroup>
</map>
""",
        encoding="utf-8",
    )

    tile_map = TiledLoader.load(tmx_path)
    obj = tile_map.object_layers["interactables"][0]

    assert obj.name == "blue_mercy_gourd_01"
    assert obj.type_name == "resource"
    assert obj.x == 8.0
    assert obj.properties == {"journal": "disc.blue_mercy_gourd"}
