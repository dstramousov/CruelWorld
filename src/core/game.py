from __future__ import annotations

from src.components.interaction import InteractionComponent
from src.components.statuses import StatusReceiverComponent
from src.core.service_container import ServiceContainer
from src.debug.overlay import DebugOverlay
from src.entities.factories import create_blue_mercy_gourd, create_grave_lace_vine
from src.entities.player import Player
from src.systems.camera_system import CameraSystem
from src.systems.input_system import InputSystem
from src.systems.interaction_system import InteractionSystem
from src.systems.localization_system import LocalizationSystem
from src.systems.status_system import StatusDefinition, StatusSystem
from src.systems.time_system import TimeSystem
from src.ui.hud import Hud
from src.ui.text_renderer import text_renderer
from src.utils import colors
from src.utils import rl as raylib
from src.utils.paths import ASSETS_DIR, CONFIG_DIR, CONTENT_DIR
from src.utils.serialization import load_json
from src.world.tiled_loader import TiledLoader
from src.world.world_state import WorldState
from src.systems.log_system import get_logger

logger = get_logger(__name__)


class Game:
    def __init__(self, config: dict) -> None:
        self.config = config
        self.world_state = WorldState()
        self.services = ServiceContainer()
        self.localization = LocalizationSystem()
        text_renderer.initialize(
            font_config=config.get("font", {}),
            localization_values=self.localization.get_all_values(),
        )
        self.input_system = InputSystem()
        self.camera_system = CameraSystem()
        self.time_system = TimeSystem(config=config)
        self.parallax_layers = []
        self._load_parallax_layers()
        render_cfg = config.get("render", {})
        self.time_system.generate_stars(
            width=int(render_cfg.get("internal_width", 640)),
            height=int(render_cfg.get("internal_height", 360)),
        )
        self.world_state.time_of_day = self.time_system.get_phase_name()
        self.world_state.time_hours = self.time_system.current_time_hours
        self.player = Player()
        self.hud = Hud()
        debug_cfg = load_json(CONFIG_DIR / "debug.json")
        self.debug_overlay = DebugOverlay(
            debug_cfg.get("overlay", {}),
            enabled=bool(debug_cfg.get("show_overlay_default", False)),
        )
        self.interaction_system = InteractionSystem()
        self.status_system = StatusSystem(self._load_status_definitions())
        self._hazard_contact_entities: set[str] = set()
        self.map_data = TiledLoader.load(ASSETS_DIR / "maps" / "vertical_slice_01.tmx")
        self.hazards: list = []
        self.interactables: list = []
        self.camera_regions: list[dict] = []
        self.exit_rect: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
        self.message_text = ""
        self.message_timer = 0.0
        self.interaction_target = None
        self.on_ground = False
        self._load_map_entities()
        self._spawn_player()
        logger.log_event("GAME_INITIALIZED", level=20, map_id=self.map_data.map_id)

    def shutdown(self) -> None:
        for layer in self.parallax_layers:
            texture = layer.get("texture")
            if texture is not None:
                raylib.unload_texture(texture)
        text_renderer.shutdown()

    def update(self, delta_time: float) -> None:
        self._handle_global_input()
        self._update_message(delta_time)
        self.time_system.update(delta_time)
        self.world_state.time_of_day = self.time_system.get_phase_name()
        self.world_state.time_hours = self.time_system.current_time_hours

        transform = self.player.get("transform")
        velocity = self.player.get("velocity")
        gravity = self.player.get("gravity")
        state = self.player.get("state")
        health = self.player.get("health")
        statuses = self.player.get("statuses")

        axis = self.input_system.horizontal_axis()
        speed = 96.0
        velocity.x = axis * speed

        if self.input_system.is_jump_pressed() and self.on_ground:
            velocity.y = -255.0
            self.on_ground = False
            logger.log_event("USER_JUMPED", x=transform.x, y=transform.y, velocity_y=velocity.y)

        velocity.y += gravity.value * delta_time
        new_x = transform.x + velocity.x * delta_time
        new_y = transform.y + velocity.y * delta_time

        transform.x = self._resolve_horizontal(new_x)
        transform.y = self._resolve_vertical(new_y, velocity)
        state.name = self._resolve_state(velocity)

        self._apply_hazards()
        self.status_system.update(statuses, health, delta_time)
        self.interaction_target = self.interaction_system.find_nearest(
            transform.x,
            transform.y,
            [entity for entity in self.interactables if not entity.get("consumable")["used"]],
        )
        if self.interaction_target and self.input_system.is_interact_pressed():
            result = self.interaction_system.execute(
                self.interaction_target,
                self.player,
                self.status_system,
            )
            self.interaction_target.get("consumable")["used"] = True
            if result == "cleansed":
                self._set_message(self.localization.tr("msg.poison_removed"))
            else:
                self._set_message(self.localization.tr("msg.interact_gourd"))

        move_dir = 0.0
        if velocity.x > 1.0:
            move_dir = 1.0
        elif velocity.x < -1.0:
            move_dir = -1.0

        self._update_camera_profile()
        self.camera_system.update(
            target_x=transform.x,
            target_y=transform.y,
            move_dir=move_dir,
        )
        self._check_exit()

    def draw(self, internal_width: int, internal_height: int) -> None:
        camera = self.camera_system.controller.get_render_state()
        raylib.clear_background(colors.CLEAR_COLOR)
        self._draw_parallax(internal_width, internal_height, camera)
        center_x = internal_width // 2
        center_y = internal_height // 2
        self._draw_tile_layer("ground", camera, center_x, center_y)
        self._draw_tile_layer("platforms", camera, center_x, center_y)
        self._draw_flora(camera, center_x, center_y)
        self._draw_player(camera, center_x, center_y)
        self._draw_exit(camera, center_x, center_y)
        self._draw_world_tint(internal_width, internal_height)

        health = self.player.get("health")
        statuses = self.player.get("statuses")
        status_text = self.localization.tr("status.none")
        if statuses.active:
            first_status = next(iter(statuses.active.keys()))
            status_text = self.localization.tr("hud.status", status=self.localization.tr(f"status.{first_status}.name"))
        health_text = self.localization.tr("hud.health", current=health.current, maximum=health.maximum)
        interaction_text = ""
        if self.interaction_system.context.available:
            target_name = self.localization.tr(self.interaction_target.name_id)
            interaction_text = self.localization.tr("hint.interact_with", target=target_name)
        else:
            interaction_text = ""
        hint = self.localization.tr("hint.controls")
        self.hud.draw(health_text, status_text, hint, interaction_text, self.message_text)

    def draw_debug_overlay(self, window_width: int, window_height: int) -> None:
        self.debug_overlay.draw(
            self._overlay_lines(),
            window_width=window_width,
            window_height=window_height,
        )

    def _load_parallax_layers(self) -> None:
        parallax_cfg = self.config.get("parallax", {})
        if not parallax_cfg.get("enabled", False):
            logger.log_event("PARALLAX_DISABLED", level=20)
            return
        for layer_cfg in parallax_cfg.get("layers", []):
            layer_path = ASSETS_DIR.parent / layer_cfg["path"]
            try:
                texture = raylib.load_texture(str(layer_path))
                self.parallax_layers.append({
                    "name": layer_cfg.get("name", layer_path.stem),
                    "texture": texture,
                    "path": layer_cfg["path"],
                    "speed": float(layer_cfg.get("speed", 0.1)),
                    "alpha": int(layer_cfg.get("alpha", 255)),
                    "vertical_offset": int(layer_cfg.get("vertical_offset", 0)),
                    "width": int(layer_cfg.get("width", 1280)),
                    "height": int(layer_cfg.get("height", 360)),
                })
                logger.log_event(
                    "PARALLAX_LAYER_LOADED",
                    level=20,
                    layer=layer_cfg.get("name", layer_path.stem),
                    path=layer_cfg["path"],
                    speed=layer_cfg.get("speed", 0.1),
                    alpha=layer_cfg.get("alpha", 255),
                )
            except Exception as exc:
                logger.log_exception_event(
                    "PARALLAX_LAYER_LOAD_FAILED",
                    exc,
                    level=40,
                    path=str(layer_path),
                )

    def _load_status_definitions(self) -> dict[str, StatusDefinition]:
        data = load_json(CONTENT_DIR / "items" / "statuses.json")
        definitions: dict[str, StatusDefinition] = {}
        for status_id, raw in data.items():
            definitions[status_id] = StatusDefinition(
                status_id=status_id,
                name_key=raw["name_key"],
                description_key=raw["description_key"],
                duration=float(raw["duration"]),
                tick_interval=float(raw["tick_interval"]),
                tick_damage=int(raw["tick_damage"]),
                color=tuple(raw["color"]),
            )
        return definitions

    def _load_map_entities(self) -> None:
        player_spawns = self.map_data.object_layers.get("spawns_player", [])
        if player_spawns:
            self.player_spawn = player_spawns[0]
        else:
            self.player_spawn = None

        for object_data in self.map_data.object_layers.get("hazards", []):
            self.hazards.append(
                create_grave_lace_vine(
                    entity_id=object_data.name or "grave_lace_vine",
                    x=object_data.x + object_data.width / 2,
                    y=object_data.y,
                    width=int(max(16.0, object_data.width)),
                    height=int(max(16.0, object_data.height)),
                )
            )

        for object_data in self.map_data.object_layers.get("interactables", []):
            self.interactables.append(
                create_blue_mercy_gourd(
                    entity_id=object_data.name or "blue_mercy_gourd",
                    x=object_data.x + object_data.width / 2,
                    y=object_data.y,
                    width=int(max(16.0, object_data.width)),
                    height=int(max(16.0, object_data.height)),
                )
            )

        self.camera_regions = []
        for object_data in self.map_data.object_layers.get("camera_zones", []):
            self.camera_regions.append(
                {
                    "x": object_data.x,
                    "y": object_data.y,
                    "width": object_data.width,
                    "height": object_data.height,
                    "profile": object_data.properties.get("camera_profile", "default_exploration"),
                    "name": object_data.name or object_data.properties.get("camera_profile", "camera_zone"),
                }
            )

        exits = self.map_data.object_layers.get("triggers", [])
        for object_data in exits:
            if object_data.name == "slice_exit":
                self.exit_rect = (object_data.x, object_data.y, object_data.width, object_data.height)
                break

    def _spawn_player(self) -> None:
        transform = self.player.get("transform")
        if self.player_spawn is not None:
            transform.x = self.player_spawn.x + self.player_spawn.width / 2
            transform.y = self.player_spawn.y
        logger.log_event("PLAYER_SPAWNED", level=20, x=transform.x, y=transform.y)

    def _resolve_horizontal(self, new_x: float) -> float:
        collider = self.player.get("collider")
        half_width = collider.width / 2
        world_left = half_width
        world_right = self.map_data.pixel_width - half_width
        return max(world_left, min(new_x, world_right))

    def _resolve_vertical(self, new_y: float, velocity) -> float:
        collider = self.player.get("collider")
        feet_x = self.player.get("transform").x
        half_width = max(1.0, collider.width / 2 - 1.0)
        sample_positions = [feet_x - half_width, feet_x, feet_x + half_width]
        feet_y = new_y
        tile_top = self._find_support_tile_top(sample_positions, feet_y)
        if tile_top is not None and velocity.y >= 0.0:
            self.on_ground = True
            velocity.y = 0.0
            return tile_top
        self.on_ground = False
        return min(new_y, float(self.map_data.pixel_height))

    def _find_support_tile_top(self, sample_positions: list[float], feet_y: float) -> float | None:
        layer = self.map_data.layers.get("collision")
        if layer is None:
            return None
        row = int(feet_y // self.map_data.tile_height)
        if row < 0 or row >= self.map_data.height:
            return None
        support_tops: list[float] = []
        for sample_x in sample_positions:
            col = int(sample_x // self.map_data.tile_width)
            if col < 0 or col >= self.map_data.width:
                continue
            index = row * self.map_data.width + col
            if index < len(layer.tiles) and layer.tiles[index] != 0:
                support_tops.append(float(row * self.map_data.tile_height))
        if support_tops:
            return min(support_tops)
        return None

    def _resolve_state(self, velocity) -> str:
        if not self.on_ground:
            return "jump" if velocity.y < 0.0 else "fall"
        if abs(velocity.x) > 0.1:
            return "run"
        return "idle"

    def _apply_hazards(self) -> None:
        transform = self.player.get("transform")
        statuses: StatusReceiverComponent = self.player.get("statuses")
        current_contacts: set[str] = set()
        for hazard in self.hazards:
            hazard_transform = hazard.get("transform")
            sprite = hazard.get("sprite")
            entity_in_contact = abs(transform.x - hazard_transform.x) <= sprite.width / 2 and abs(transform.y - hazard_transform.y) <= sprite.height
            biota = hazard.components.get("biota")
            if entity_in_contact:
                current_contacts.add(hazard.entity_id)
                if hazard.entity_id not in self._hazard_contact_entities and biota is not None:
                    logger.log_biota_event(
                        biota.get("species_id", "unknown"),
                        "PLAYER_NOTICED",
                        entity_kind=biota.get("entity_kind", "flora"),
                        entity_id=hazard.entity_id,
                        player_x=round(transform.x, 2),
                        player_y=round(transform.y, 2),
                    )
                status_id = hazard.get("hazard")["status_on_touch"]
                applied = self.status_system.apply(statuses, status_id)
                if applied:
                    if biota is not None:
                        logger.log_biota_event(
                            biota.get("species_id", "unknown"),
                            "PLAYER_CONTACT",
                            level=20,
                            entity_kind=biota.get("entity_kind", "flora"),
                            entity_id=hazard.entity_id,
                            applied_status=status_id,
                        )
                    self._set_message(self.localization.tr("msg.poisoned_applied"))
            elif hazard.entity_id in self._hazard_contact_entities and biota is not None:
                logger.log_biota_event(
                    biota.get("species_id", "unknown"),
                    "PLAYER_LOST",
                    entity_kind=biota.get("entity_kind", "flora"),
                    entity_id=hazard.entity_id,
                )
        self._hazard_contact_entities = current_contacts

    def _update_camera_profile(self) -> None:
        transform = self.player.get("transform")
        profile_name = "default_exploration"
        trigger_name = "none"
        for region in self.camera_regions:
            if (
                region["x"] <= transform.x <= region["x"] + region["width"]
                and region["y"] <= transform.y <= region["y"] + region["height"]
            ):
                profile_name = region["profile"]
                trigger_name = region["name"]
                break
        if profile_name != self.camera_system.profile_name:
            self.camera_system.set_profile(profile_name, trigger_name)

    def _check_exit(self) -> None:
        if self.world_state.slice_completed:
            return
        transform = self.player.get("transform")
        x, y, width, height = self.exit_rect
        if x <= transform.x <= x + width and y <= transform.y <= y + height:
            self.world_state.slice_completed = True
            logger.log_event("GAME_SLICE_COMPLETED", level=20, map_id=self.map_data.map_id)
            self._set_message(self.localization.tr("msg.slice_complete"), duration=4.0)

    def _handle_global_input(self) -> None:
        if raylib.is_key_pressed(raylib.KEY_F1):
            self.localization.toggle_language()
        if (
            raylib.is_key_down(raylib.KEY_LEFT_SHIFT)
            or raylib.is_key_down(raylib.KEY_RIGHT_SHIFT)
        ) and raylib.is_key_pressed(raylib.KEY_D):
            self.debug_overlay.toggle()
            logger.log_event("DEBUG_OVERLAY_TOGGLED", level=20, enabled=self.debug_overlay.enabled)
        if raylib.is_key_pressed(raylib.KEY_Q):
            self.camera_system.zoom_out()
        if raylib.is_key_pressed(raylib.KEY_E):
            self.camera_system.zoom_in()

    def _update_message(self, delta_time: float) -> None:
        if self.message_timer > 0.0:
            self.message_timer -= delta_time
            if self.message_timer <= 0.0:
                self.message_text = ""

    def _set_message(self, text: str, duration: float = 2.0) -> None:
        self.message_text = text
        self.message_timer = duration

    def _draw_parallax(self, internal_width: int, internal_height: int, camera) -> None:
        if not self.parallax_layers:
            raylib.draw_rectangle(0, 0, internal_width, internal_height, colors.CLEAR_COLOR)
            self._draw_stars(internal_width, camera)
            return

        stars_drawn = False
        for index, layer in enumerate(self.parallax_layers):
            texture = layer["texture"]
            layer_width = layer["width"]
            layer_height = layer["height"]
            speed = layer["speed"]
            alpha = layer["alpha"]
            offset_x = -round(camera.x * speed)
            dest_x = min(0, max(internal_width - layer_width, offset_x))
            source = raylib.Rectangle(0.0, 0.0, float(layer_width), float(layer_height))
            destination = raylib.Rectangle(float(dest_x), float(layer["vertical_offset"]), float(layer_width), float(layer_height))
            tint = self.time_system.get_sky_tint() if layer.get("name") == "sky" else (255, 255, 255, alpha)
            if layer.get("name") == "sky":
                layer_tint = (tint[0], tint[1], tint[2], min(255, alpha + tint[3]))
            else:
                layer_tint = (255, 255, 255, alpha)
            raylib.draw_texture_pro(
                texture,
                source,
                destination,
                raylib.Vector2(0.0, 0.0),
                0.0,
                layer_tint,
            )
            should_draw_stars = layer.get("name") == "sky" or index == 0
            if not stars_drawn and should_draw_stars:
                self._draw_stars(internal_width, camera)
                stars_drawn = True

    def _draw_stars(self, internal_width: int, camera) -> None:
        visibility = self.time_system.get_star_visibility()
        if visibility <= 0.0:
            return
        for star in self.time_system.stars:
            alpha = self.time_system.get_star_alpha(star)
            if alpha <= 0:
                continue
            screen_x = self.time_system.get_star_screen_x(star, camera.x, internal_width)
            raylib.draw_rectangle(screen_x, int(star.y), star.size, star.size, (255, 255, 255, alpha))


    def _draw_world_tint(self, internal_width: int, internal_height: int) -> None:
        tint = self.time_system.get_world_tint()
        if tint[3] <= 0:
            return
        raylib.draw_rectangle(0, 0, internal_width, internal_height, tint)

    def _draw_tile_layer(self, layer_name: str, camera, center_x: int, center_y: int) -> None:
        layer = self.map_data.layers.get(layer_name)
        if layer is None:
            return
        tile_width = self.map_data.tile_width
        tile_height = self.map_data.tile_height
        for row in range(layer.height):
            world_top = row * tile_height
            world_bottom = world_top + tile_height
            screen_top = round(center_y + (world_top - camera.y) * camera.zoom)
            screen_bottom = round(center_y + (world_bottom - camera.y) * camera.zoom)
            draw_height = max(1, screen_bottom - screen_top)
            for col in range(layer.width):
                tile = layer.tiles[row * layer.width + col]
                if tile == 0:
                    continue
                world_left = col * tile_width
                world_right = world_left + tile_width
                screen_left = round(center_x + (world_left - camera.x) * camera.zoom)
                screen_right = round(center_x + (world_right - camera.x) * camera.zoom)
                draw_width = max(1, screen_right - screen_left)
                raylib.draw_rectangle(screen_left, screen_top, draw_width, draw_height, colors.GROUND)
                raylib.draw_line(screen_left, screen_top, screen_right, screen_top, colors.GROUND_LIGHT)
                raylib.draw_line(screen_left, screen_bottom - 1, screen_right, screen_bottom - 1, colors.GROUND_DARK)

    def _draw_flora(self, camera, center_x: int, center_y: int) -> None:
        for hazard in self.hazards:
            transform = hazard.get("transform")
            sprite = hazard.get("sprite")
            screen_x = round(center_x + (transform.x - camera.x) * camera.zoom)
            screen_y = round(center_y + (transform.y - camera.y) * camera.zoom)
            width = max(1, round(sprite.width * camera.zoom))
            height = max(1, round(sprite.height * camera.zoom))
            raylib.draw_rectangle(screen_x - width // 2, screen_y - height, width, height, colors.VINE)
            raylib.draw_circle(screen_x, screen_y - height + 6, max(1.0, 4 * camera.zoom), colors.VINE_GLOW)
        for entity in self.interactables:
            if entity.get("consumable")["used"]:
                continue
            transform = entity.get("transform")
            sprite = entity.get("sprite")
            screen_x = round(center_x + (transform.x - camera.x) * camera.zoom)
            screen_y = round(center_y + (transform.y - camera.y) * camera.zoom)
            width = max(1, round(sprite.width * camera.zoom))
            height = max(1, round(sprite.height * camera.zoom))
            raylib.draw_rectangle(screen_x - width // 2, screen_y - height, width, height, colors.GOURD)
            raylib.draw_circle(screen_x, screen_y - height + 5, max(1.0, 5 * camera.zoom), colors.GOURD_CORE)

    def _draw_player(self, camera, center_x: int, center_y: int) -> None:
        transform = self.player.get("transform")
        sprite = self.player.get("sprite")
        screen_x = round(center_x + (transform.x - camera.x) * camera.zoom)
        screen_y = round(center_y + (transform.y - camera.y) * camera.zoom)
        width = max(1, round(sprite.width * camera.zoom))
        height = max(1, round(sprite.height * camera.zoom))
        raylib.draw_rectangle(screen_x - width // 2, screen_y - height, width, height, colors.PLAYER)
        raylib.draw_circle(screen_x + width // 2, screen_y - height + 3, max(1.0, 3 * camera.zoom), (255, 255, 180, 50))

    def _draw_exit(self, camera, center_x: int, center_y: int) -> None:
        x, y, width, height = self.exit_rect
        screen_x = round(center_x + (x - camera.x) * camera.zoom)
        screen_y = round(center_y + (y - camera.y) * camera.zoom)
        rect_w = max(1, round(width * camera.zoom))
        rect_h = max(1, round(height * camera.zoom))
        raylib.draw_rectangle(screen_x, screen_y, rect_w, rect_h, (35, 75, 42, 90))
        raylib.draw_line(screen_x + rect_w - 4, screen_y, screen_x + rect_w - 4, screen_y + rect_h, colors.EXIT)

    def _overlay_lines(self) -> list[str]:
        transform = self.player.get("transform")
        velocity = self.player.get("velocity")
        health = self.player.get("health")
        statuses = self.player.get("statuses")
        camera = self.camera_system.controller.get_render_state()
        language_key = f"language.{self.localization.current_language.value}"
        language_name = self.localization.tr(language_key)
        active_status = ", ".join(statuses.names()) if statuses.active else self.localization.tr("status.none")
        return [
            self.localization.tr("debug.overlay"),
            self.localization.tr("scene.current", scene=self.world_state.current_scene),
            self.localization.tr("zone.current", zone=self.world_state.current_zone),
            self.localization.tr("map.current", map_id=self.world_state.current_map_id),
            self.localization.tr("lang.current", language=language_name),
            self.localization.tr("weather.current", weather=self.world_state.weather),
            self.localization.tr(
                "time.current",
                time=f"{self.world_state.time_of_day} ({self.time_system.format_time_hours(self.world_state.time_hours)})",
            ),
            self.localization.tr("player.position", x=transform.x, y=transform.y),
            self.localization.tr("player.velocity", x=velocity.x, y=velocity.y),
            self.localization.tr("hud.health", current=health.current, maximum=health.maximum),
            self.localization.tr("status.debug", status=active_status),
            self.localization.tr("camera.profile", profile=self.camera_system.profile_name),
            self.localization.tr("camera.position", x=camera.x, y=camera.y),
            self.localization.tr("camera.zoom", zoom=camera.zoom),
            self.localization.tr("camera.follow_speed", value=camera.follow_speed),
            self.localization.tr("camera.trigger", trigger=self.camera_system.active_trigger),
            self.localization.tr("interaction.target", target=self.interaction_system.context.target_id),
            self.localization.tr("debug.last_event", event=self.status_system.last_event),
        ]
