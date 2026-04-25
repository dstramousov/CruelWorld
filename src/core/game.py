"""Main gameplay coordinator that updates simulation systems and draws the current scene."""

from __future__ import annotations

from src.components.statuses import StatusReceiverComponent
from src.core.asset_manager import AssetManager
from src.core.service_container import ServiceContainer
from src.debug.overlay import DebugOverlay
from src.entities.factories import (
    create_hazard_entity,
    create_interactable_entity,
    create_observation_entity,
)
from src.entities.player import Player
from src.systems.camera_system import CameraSystem
from src.systems.debug_metrics import DebugMetrics, ObjectDebugStats
from src.systems.input_system import InputSystem
from src.systems.interaction_system import InteractionSystem
from src.systems.journal_system import JournalSystem
from src.systems.light_system import LightSystem
from src.systems.localization_system import LocalizationSystem
from src.systems.status_system import StatusDefinition, StatusSystem
from src.systems.time_system import TimeSystem
from src.ui.communicator import CommunicatorUi
from src.ui.hud import Hud
from src.ui.text_renderer import text_renderer
from src.utils import colors
from src.utils import rl as raylib
from src.utils.paths import CONFIG_DIR, CONTENT_DIR, resolve_project_path
from src.utils.serialization import load_json
from src.world.tiled_loader import TiledLoader
from src.world.world_state import WorldState
from src.systems.log_system import get_logger

logger = get_logger(__name__)


class Game:
    """Represent the Game runtime concept."""
    def __init__(self, config: dict) -> None:
        # Core game object composition. This is the runtime root that wires
        # configuration, services, systems, UI, map data, and player state.
        """Execute init.
        
        Args:
            config: Input value used by this operation.
        """
        self.config = config
        self.world_state = WorldState()
        self.services = ServiceContainer()
        self.asset_manager = AssetManager()
        self.localization = LocalizationSystem()
        text_renderer.initialize(
            font_config=config.get("font", {}),
            localization_values=self.localization.get_all_values(),
        )
        self.input_system = InputSystem(config.get("controls", {}))
        self.camera_system = CameraSystem()
        self.time_system = TimeSystem(config=config)
        self.light_system = LightSystem()
        render_cfg = config.get("render", {})
        window_cfg = config.get("window", {})
        self.window_width = int(window_cfg.get("width", 1280))
        self.window_height = int(window_cfg.get("height", 720))
        self.internal_width = int(render_cfg.get("internal_width", 640))
        self.internal_height = int(render_cfg.get("internal_height", 360))
        self.quit_requested = False
        self.raw_frame_time = 0.0
        self.update_delta_time = 0.0
        self.debug_metrics = DebugMetrics(
            chunk_width_tiles=int(config.get("debug", {}).get("chunk_width_tiles", 64)),
        )
        self.time_system.generate_stars(
            width=self.internal_width,
            height=self.internal_height,
        )
        self._initialize_world_state()
        self.world_state.player_name = str(config.get("new_game", {}).get("default_hero_name", "Survivor"))
        self.world_state.time_of_day = self.time_system.get_phase_name()
        self.world_state.time_hours = self.time_system.current_time_hours
        self.player = Player()
        self.player_facing = 1.0
        self._configure_player_flashlight()
        self.hud = Hud()
        debug_cfg = load_json(CONFIG_DIR / "debug.json")
        self.debug_overlay = DebugOverlay(
            debug_cfg.get("overlay", {}),
            enabled=bool(debug_cfg.get("show_overlay_default", False)),
        )
        self.interaction_system = InteractionSystem()
        self.journal_system = JournalSystem()
        communicator_config = dict(config.get("ui", {}).get("communicator", {}))
        communicator_config.update(config.get("new_game", {}))
        self.communicator = CommunicatorUi(communicator_config)
        self.status_system = StatusSystem(self._load_status_definitions())
        self._hazard_contact_entities: set[str] = set()
        self.map_data = self._load_start_map()
        self.hazards: list = []
        self.interactables: list = []
        self.observation_markers: list = []
        self.discovered_entries: set[str] = set()
        self.camera_regions: list[dict] = []
        self.route_guides: list[dict] = []
        self.exit_rect: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
        self.message_text = ""
        self.message_timer = 0.0
        self.interaction_target = None
        self.on_ground = False
        # Map-derived runtime objects are created after systems are ready, so
        # hazards, interactables, route guides, and camera regions share one map.
        self._load_map_entities()
        self._spawn_player()
        logger.log_event("GAME_INITIALIZED", level=20, map_id=self.map_data.map_id)

    def record_frame_metrics(self, raw_frame_time: float, update_delta_time: float) -> None:
        """Store last frame timings for the debug overlay."""
        self.raw_frame_time = max(0.0, raw_frame_time)
        self.update_delta_time = max(0.0, update_delta_time)

    def shutdown(self) -> None:
        """Execute shutdown.
        """
        self.asset_manager.unload_all()
        text_renderer.shutdown()

    def update(self, delta_time: float) -> None:
        # Simulation update. Communicator pauses the world but still consumes
        # input, so it is handled before time, player movement, and hazards.
        """Update update.
        
        Args:
            delta_time: Input value used by this operation.
        """
        self._update_message(delta_time)
        if self.communicator.is_open:
            self._handle_communicator_input()
            return
        self._handle_global_input()
        if self.communicator.is_open:
            return
        self.time_system.update(delta_time)
        self.world_state.time_of_day = self.time_system.get_phase_name()
        self.world_state.time_hours = self.time_system.current_time_hours

        # Player movement block: read input, apply status modifiers, integrate
        # gravity, then resolve against the current tile map.
        transform = self.player.get("transform")
        velocity = self.player.get("velocity")
        gravity = self.player.get("gravity")
        state = self.player.get("state")
        health = self.player.get("health")
        statuses = self.player.get("statuses")

        axis = self.input_system.horizontal_axis()
        speed = 96.0
        if "slowed" in statuses.active:
            speed *= 0.65
        if "drowsy" in statuses.active:
            speed *= 0.82
        velocity.x = axis * speed
        if axis < -0.01:
            self.player_facing = -1.0
        elif axis > 0.01:
            self.player_facing = 1.0

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

        # World interaction block: hazards apply passive contact effects, while
        # explicit interactables require the configured interact button.
        self._apply_hazards()
        self.status_system.update(statuses, health, delta_time)
        available_interactions = [
            entity
            for entity in self.interactables + self.observation_markers
            if not entity.get("consumable")["used"]
        ]
        self.interaction_target = self.interaction_system.find_nearest(
            transform.x,
            transform.y,
            available_interactions,
        )
        if self.interaction_target and self.input_system.is_interact_pressed():
            result = self.interaction_system.execute(
                self.interaction_target,
                self.player,
                self.status_system,
            )
            consumable = self.interaction_target.get("consumable")
            if consumable["single_use"]:
                consumable["used"] = True
            if result.discovery_key:
                self.discovered_entries.add(result.discovery_key)
                if self.journal_system.unlock(result.discovery_key):
                    self._set_message(self.localization.tr("msg.journal_entry_added"), duration=2.4)
                else:
                    self._set_message(self.localization.tr(result.message_key))
            else:
                self._set_message(self.localization.tr(result.message_key))

        # Camera block: update profile from map regions, then follow the player
        # with a small look-ahead based on movement direction.
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
        # Render order: background, tile layers, route guides, gameplay objects,
        # player, world tint, HUD, then communicator overlay.
        """Draw draw.
        
        Args:
            internal_width: Input value used by this operation.
            internal_height: Input value used by this operation.
        """
        camera = self.camera_system.controller.get_render_state()
        raylib.clear_background(colors.CLEAR_COLOR)
        self._draw_background(internal_width, internal_height, camera)
        center_x = internal_width // 2
        center_y = internal_height // 2
        self._draw_tile_layer("ground", camera, center_x, center_y)
        self._draw_tile_layer("platforms", camera, center_x, center_y)
        self._draw_route_guides(camera, center_x, center_y)
        self._draw_flora(camera, center_x, center_y)
        self._draw_player(camera, center_x, center_y)
        self._draw_exit(camera, center_x, center_y)
        self._draw_world_tint(internal_width, internal_height)
        self._draw_player_flashlight(camera, center_x, center_y)

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
        self.hud.draw(
            health_text,
            status_text,
            hint,
            interaction_text,
            self.message_text,
            internal_width,
            internal_height,
        )
        self.communicator.draw(self.journal_system, self.localization, internal_width, internal_height)

    def draw_debug_overlay(self, window_width: int, window_height: int) -> None:
        """Draw draw debug overlay.
        
        Args:
            window_width: Input value used by this operation.
            window_height: Input value used by this operation.
        """
        self.debug_overlay.draw(
            self._overlay_lines(),
            window_width=window_width,
            window_height=window_height,
        )

    def _configure_player_flashlight(self) -> None:
        """Apply flashlight configuration to the player light component."""
        light = self.player.get("light")
        cfg = self.config.get("flashlight", {})
        light.mode = str(cfg.get("start_mode", "off"))
        light.radius = float(cfg.get("radial_radius", light.radius))
        light.beam_distance = float(cfg.get("beam_distance", light.beam_distance))
        light.beam_half_width = float(cfg.get("beam_half_width", light.beam_half_width))

    def _initialize_world_state(self) -> None:
        """Execute initialize world state.
        """
        world_cfg = self.config.get("world", {})
        self.world_state.current_scene = str(world_cfg.get("start_scene", "vertical_slice_01"))
        self.world_state.current_zone = str(world_cfg.get("start_zone", "landing_margin"))

    def _load_start_map(self):
        """Execute load start map.
        """
        world_cfg = self.config.get("world", {})
        start_map = world_cfg.get("start_map", "assets/maps/vertical_slice_01.tmx")
        map_path = resolve_project_path(start_map)
        tile_map = TiledLoader.load(map_path)
        self.world_state.current_map_id = tile_map.map_id
        logger.log_event("START_MAP_LOADED", level=20, path=str(map_path), map_id=tile_map.map_id)
        return tile_map

    def _load_status_definitions(self) -> dict[str, StatusDefinition]:
        """Execute load status definitions.
        
        Returns:
            Result produced by this operation.
        """
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
        # Convert Tiled object layers into lightweight runtime entities and
        # metadata lists used by gameplay, camera, and debug systems.
        """Execute load map entities.
        """
        player_spawns = self.map_data.object_layers.get("spawns_player", [])
        if player_spawns:
            self.player_spawn = player_spawns[0]
        else:
            self.player_spawn = None

        for object_data in self.map_data.object_layers.get("hazards", []):
            self.hazards.append(
                create_hazard_entity(
                    entity_id=object_data.name or "hazard",
                    x=object_data.x + object_data.width / 2,
                    y=object_data.y,
                    width=int(max(16.0, object_data.width)),
                    height=int(max(16.0, object_data.height)),
                )
            )

        for object_data in self.map_data.object_layers.get("interactables", []):
            self.interactables.append(
                create_interactable_entity(
                    entity_id=object_data.name or "interactable",
                    x=object_data.x + object_data.width / 2,
                    y=object_data.y,
                    width=int(max(16.0, object_data.width)),
                    height=int(max(16.0, object_data.height)),
                )
            )

        for layer_name in ("fauna_markers", "resource_nodes", "points_of_interest"):
            for object_data in self.map_data.object_layers.get(layer_name, []):
                self.observation_markers.append(
                    create_observation_entity(
                        entity_id=object_data.name or layer_name,
                        x=object_data.x + object_data.width / 2,
                        y=object_data.y + object_data.height / 2,
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

        self.route_guides = []
        for object_data in self.map_data.object_layers.get("route_guides", []):
            self.route_guides.append(
                {
                    "x": object_data.x,
                    "y": object_data.y,
                    "width": object_data.width,
                    "height": object_data.height,
                    "kind": object_data.type_name or "route_main",
                    "name": object_data.name,
                }
            )

        exits = self.map_data.object_layers.get("triggers", [])
        for object_data in exits:
            if object_data.name == "slice_exit":
                self.exit_rect = (object_data.x, object_data.y, object_data.width, object_data.height)
                break

    def _spawn_player(self) -> None:
        """Execute spawn player.
        """
        transform = self.player.get("transform")
        if self.player_spawn is not None:
            transform.x = self.player_spawn.x + self.player_spawn.width / 2
            transform.y = self.player_spawn.y
        logger.log_event("PLAYER_SPAWNED", level=20, x=transform.x, y=transform.y)

    def _resolve_horizontal(self, new_x: float) -> float:
        """Execute resolve horizontal.
        
        Args:
            new_x: Input value used by this operation.
        
        Returns:
            Result produced by this operation.
        """
        collider = self.player.get("collider")
        half_width = collider.width / 2
        world_left = half_width
        world_right = self.map_data.pixel_width - half_width
        return max(world_left, min(new_x, world_right))

    def _resolve_vertical(self, new_y: float, velocity) -> float:
        """Execute resolve vertical.
        
        Args:
            new_y: Input value used by this operation.
            velocity: Input value used by this operation.
        
        Returns:
            Result produced by this operation.
        """
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
        """Execute find support tile top.
        
        Args:
            sample_positions: Input value used by this operation.
            feet_y: Input value used by this operation.
        
        Returns:
            Result produced by this operation.
        """
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
        """Execute resolve state.
        
        Args:
            velocity: Input value used by this operation.
        
        Returns:
            Result produced by this operation.
        """
        if not self.on_ground:
            return "jump" if velocity.y < 0.0 else "fall"
        if abs(velocity.x) > 0.1:
            return "run"
        return "idle"

    def _apply_hazards(self) -> None:
        # Passive contact processing. A hazard can apply statuses, change health,
        # log the biota encounter, and show a short HUD message.
        """Execute apply hazards.
        """
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
                hazard_data = hazard.get("hazard")
                applied_statuses: list[str] = []
                for status_id in hazard_data.get("statuses_on_touch", []):
                    if self.status_system.apply(statuses, status_id):
                        applied_statuses.append(status_id)
                health_delta = int(hazard_data.get("health_delta", 0))
                if health_delta != 0:
                    health = self.player.get("health")
                    health.current = max(0, min(health.maximum, health.current + health_delta))
                if applied_statuses or health_delta != 0:
                    if biota is not None:
                        logger.log_biota_event(
                            biota.get("species_id", "unknown"),
                            "PLAYER_CONTACT",
                            level=20,
                            entity_kind=biota.get("entity_kind", "flora"),
                            entity_id=hazard.entity_id,
                            applied_statuses=applied_statuses,
                            health_delta=health_delta,
                        )
                    self._set_message(self.localization.tr(hazard_data.get("message_key", "msg.hazard_contact")))
            elif hazard.entity_id in self._hazard_contact_entities and biota is not None:
                logger.log_biota_event(
                    biota.get("species_id", "unknown"),
                    "PLAYER_LOST",
                    entity_kind=biota.get("entity_kind", "flora"),
                    entity_id=hazard.entity_id,
                )
        self._hazard_contact_entities = current_contacts

    def _update_camera_profile(self) -> None:
        """Update update camera profile.
        """
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
        """Execute check exit.
        """
        if self.world_state.slice_completed:
            return
        transform = self.player.get("transform")
        x, y, width, height = self.exit_rect
        if x <= transform.x <= x + width and y <= transform.y <= y + height:
            self.world_state.slice_completed = True
            logger.log_event("GAME_SLICE_COMPLETED", level=20, map_id=self.map_data.map_id)
            self._set_message(self.localization.tr("msg.slice_complete"), duration=4.0)

    def _handle_global_input(self) -> None:
        # Global hotkeys that are allowed while normal gameplay is active.
        """Handle handle global input.
        """
        if self.input_system.is_action_pressed("toggle_language"):
            self.localization.toggle_language()
        if self.input_system.is_action_pressed("toggle_debug"):
            self.debug_overlay.toggle()
            logger.log_event("DEBUG_OVERLAY_TOGGLED", level=20, enabled=self.debug_overlay.enabled)
        if self.input_system.is_action_pressed("zoom_out"):
            self.camera_system.zoom_out()
        if self.input_system.is_action_pressed("zoom_in"):
            self.camera_system.zoom_in()
        if self.input_system.is_flashlight_cycle_pressed():
            light = self.player.get("light")
            mode = self.light_system.cycle_mode(light)
            self._set_message(self.localization.tr(f"flashlight.mode.{mode}"), duration=1.2)
            logger.log_event("FLASHLIGHT_MODE_CHANGED", level=20, mode=mode)
        if self.input_system.is_communicator_toggle_pressed():
            self.communicator.toggle()
            logger.log_event("COMMUNICATOR_TOGGLED", level=20, open=self.communicator.is_open)

    def _handle_communicator_input(self) -> None:
        # Communicator input is separated from gameplay input so the paused
        # journal/menu cannot accidentally move or interact with the player.
        """Handle handle communicator input.
        """
        if raylib.is_mouse_button_pressed(raylib.MOUSE_BUTTON_LEFT):
            mouse_x, mouse_y = self._mouse_to_internal_position()
            action = self.communicator.handle_click(mouse_x, mouse_y, self.journal_system)
            if self._handle_communicator_action(action):
                return
        if self.communicator.active_menu == "new_game" and not self.communicator.exit_confirmation_visible:
            self._handle_new_game_text_input()
        if self.input_system.is_communicator_activate_pressed():
            action = self.communicator.activate_current_menu()
            if self._handle_communicator_action(action):
                return
        if self.communicator.active_menu == "new_game" and self.input_system.is_communicator_cancel_pressed():
            if self.communicator.handle_new_game_backspace():
                return
        if self.input_system.is_communicator_cancel_pressed():
            self.communicator.cancel_current_dialog()
        if self.input_system.is_communicator_menu_next_pressed():
            self.communicator.select_next_menu()
        if self.input_system.is_communicator_menu_previous_pressed():
            self.communicator.select_previous_menu()
        if self.communicator.active_menu == "journal" and self.input_system.is_communicator_next_pressed():
            self.journal_system.select_next()
        if self.communicator.active_menu == "journal" and self.input_system.is_communicator_previous_pressed():
            self.journal_system.select_previous()
        if self.communicator.active_menu == "settings" and self.input_system.is_communicator_next_pressed():
            self.communicator.select_next_setting()
        if self.communicator.active_menu == "settings" and self.input_system.is_communicator_previous_pressed():
            self.communicator.select_previous_setting()
        if self.communicator.active_menu == "new_game" and self.input_system.is_communicator_next_pressed():
            self.communicator.select_next_new_game_item()
        if self.communicator.active_menu == "new_game" and self.input_system.is_communicator_previous_pressed():
            self.communicator.select_previous_new_game_item()
        if self.input_system.is_communicator_close_pressed():
            self.communicator.close()
            logger.log_event("COMMUNICATOR_CLOSED", level=20)

    def _handle_new_game_text_input(self) -> None:
        """Read text input queued by raylib and pass it to the new-game form."""
        while True:
            codepoint = raylib.get_char_pressed()
            if codepoint <= 0:
                return
            try:
                character = chr(codepoint)
            except (OverflowError, ValueError):
                continue
            self.communicator.handle_new_game_text_input(character)

    def _start_new_game(self, hero_name: str) -> None:
        """Reset runtime state and start a fresh run for the named hero.

        Args:
            hero_name: Player-visible hero name entered in the communicator.
        """
        self.world_state = WorldState(player_name=hero_name)
        self._initialize_world_state()
        self.time_system.reset_to_start_time()
        self.world_state.time_of_day = self.time_system.get_phase_name()
        self.world_state.time_hours = self.time_system.current_time_hours
        self.player = Player()
        self.player_facing = 1.0
        self._configure_player_flashlight()
        self.journal_system = JournalSystem()
        self.discovered_entries.clear()
        self._hazard_contact_entities.clear()
        self.interaction_target = None
        self.interaction_system.clear_context()
        self.world_state.current_map_id = self.map_data.map_id
        self.world_state.slice_completed = False
        self.on_ground = False
        self._spawn_player()
        self.communicator.close()
        self._set_message(self.localization.tr("new_game.started", name=hero_name), duration=2.4)
        logger.log_event("NEW_GAME_STARTED", level=20, hero_name=hero_name, map_id=self.map_data.map_id)

    def _handle_communicator_action(self, action: str | None) -> bool:
        """Handle action emitted by the communicator UI.

        Args:
            action: Action identifier returned by the communicator.

        Returns:
            True if the caller should stop processing communicator input.
        """
        if action is None:
            return False
        if action == "quit":
            self.quit_requested = True
            logger.log_event("QUIT_REQUESTED_FROM_COMMUNICATOR", level=20)
            return True
        if action == "new_game:start":
            self._start_new_game(self.communicator.get_new_game_hero_name(self.localization.tr("new_game.default_name")))
            return True
        if action == "settings:language":
            self.localization.toggle_language()
            language_key = f"language.{self.localization.current_language.value}"
            self._set_message(self.localization.tr("settings.language.changed", language=self.localization.tr(language_key)), duration=1.8)
            return False
        if action == "settings:font_size":
            font_size = self.communicator.cycle_font_size()
            self._set_message(self.localization.tr("settings.text_size.changed", size=font_size), duration=1.8)
            return False
        return False

    def _mouse_to_internal_position(self) -> tuple[int, int]:
        # Mouse clicks arrive in OS window coordinates; UI hitboxes are stored
        # in fixed internal render coordinates.
        """Execute mouse to internal position.
        
        Returns:
            Result produced by this operation.
        """
        scale_x = self.internal_width / max(1, self.window_width)
        scale_y = self.internal_height / max(1, self.window_height)
        mouse_x = int(raylib.get_mouse_x() * scale_x)
        mouse_y = int(raylib.get_mouse_y() * scale_y)
        return mouse_x, mouse_y

    def _update_message(self, delta_time: float) -> None:
        """Update update message.
        
        Args:
            delta_time: Input value used by this operation.
        """
        if self.message_timer > 0.0:
            self.message_timer -= delta_time
            if self.message_timer <= 0.0:
                self.message_text = ""

    def _set_message(self, text: str, duration: float = 2.0) -> None:
        """Execute set message.
        
        Args:
            text: Input value used by this operation.
            duration: Input value used by this operation.
        """
        self.message_text = text
        self.message_timer = duration

    def _draw_background(self, internal_width: int, internal_height: int, camera) -> None:
        """Draw draw background.
        
        Args:
            internal_width: Input value used by this operation.
            internal_height: Input value used by this operation.
            camera: Input value used by this operation.
        """
        raylib.draw_rectangle(0, 0, internal_width, internal_height, colors.CLEAR_COLOR)
        sky_tint = self.time_system.get_sky_tint()
        if sky_tint[3] > 0:
            raylib.draw_rectangle(0, 0, internal_width, internal_height, sky_tint)
        self._draw_stars(internal_width, camera)

    def _draw_stars(self, internal_width: int, camera) -> None:
        """Draw draw stars.
        
        Args:
            internal_width: Input value used by this operation.
            camera: Input value used by this operation.
        """
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
        """Draw draw world tint.
        
        Args:
            internal_width: Input value used by this operation.
            internal_height: Input value used by this operation.
        """
        tint = self.time_system.get_world_tint()
        if tint[3] <= 0:
            return
        raylib.draw_rectangle(0, 0, internal_width, internal_height, tint)

    def _draw_tile_layer(self, layer_name: str, camera, center_x: int, center_y: int) -> None:
        """Draw draw tile layer.
        
        Args:
            layer_name: Input value used by this operation.
            camera: Input value used by this operation.
            center_x: Input value used by this operation.
            center_y: Input value used by this operation.
        """
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

    def _draw_route_guides(self, camera, center_x: int, center_y: int) -> None:
        """Draw draw route guides.
        
        Args:
            camera: Input value used by this operation.
            center_x: Input value used by this operation.
            center_y: Input value used by this operation.
        """
        route_colors = {
            "route_main": colors.ROUTE_MAIN,
            "route_branch": colors.ROUTE_BRANCH,
            "route_risk": colors.ROUTE_RISK,
            "route_return": colors.ROUTE_BRANCH,
            "route_exit": colors.ROUTE_EXIT,
        }
        for guide in self.route_guides:
            color = route_colors.get(guide["kind"], colors.ROUTE_MAIN)
            screen_x = round(center_x + (guide["x"] - camera.x) * camera.zoom)
            screen_y = round(center_y + (guide["y"] - camera.y) * camera.zoom)
            width = max(1, round(guide["width"] * camera.zoom))
            height = max(1, round(guide["height"] * camera.zoom))
            raylib.draw_rectangle(screen_x, screen_y, width, height, color)

    def _draw_flora(self, camera, center_x: int, center_y: int) -> None:
        """Draw draw flora.
        
        Args:
            camera: Input value used by this operation.
            center_x: Input value used by this operation.
            center_y: Input value used by this operation.
        """
        for marker in self.observation_markers:
            self._draw_entity_marker(marker, camera, center_x, center_y, filled=False)
        for hazard in self.hazards:
            self._draw_entity_marker(hazard, camera, center_x, center_y, filled=True)
        for entity in self.interactables:
            if entity.get("consumable")["used"]:
                continue
            self._draw_entity_marker(entity, camera, center_x, center_y, filled=True)

    def _draw_entity_marker(self, entity, camera, center_x: int, center_y: int, filled: bool) -> None:
        """Draw draw entity marker.
        
        Args:
            entity: Input value used by this operation.
            camera: Input value used by this operation.
            center_x: Input value used by this operation.
            center_y: Input value used by this operation.
            filled: Input value used by this operation.
        """
        transform = entity.get("transform")
        sprite = entity.get("sprite")
        screen_x = round(center_x + (transform.x - camera.x) * camera.zoom)
        screen_y = round(center_y + (transform.y - camera.y) * camera.zoom)
        width = max(1, round(sprite.width * camera.zoom))
        height = max(1, round(sprite.height * camera.zoom))
        visual = entity.components.get("visual", {})
        color = self._color_for_visual(visual.get("kind", "gourd"))
        left = screen_x - width // 2
        top = screen_y - height
        if filled:
            raylib.draw_rectangle(left, top, width, height, color)
            raylib.draw_circle(screen_x, top + max(4, height // 4), max(1.0, 4 * camera.zoom), colors.GOURD_CORE)
        else:
            raylib.draw_rectangle(left, top, width, height, color)

    def _color_for_visual(self, kind: str) -> tuple[int, int, int, int]:
        """Execute color for visual.
        
        Args:
            kind: Input value used by this operation.
        
        Returns:
            Result produced by this operation.
        """
        visual_colors = {
            "gourd": colors.GOURD,
            "fern": colors.FERN,
            "succulent": colors.SUCCULENT,
            "pulsefruit": colors.PULSEFRUIT,
            "fig": colors.FIG,
            "vine": colors.VINE,
            "frond": colors.FROND,
            "moss": colors.MOSS,
            "needle": colors.NEEDLE,
            "parasite": colors.PARASITE,
            "fauna": colors.FAUNA_MARKER,
            "mite": colors.MITE_MARKER,
            "frog": colors.FROG_MARKER,
            "shelter": colors.SHELTER_MARKER,
            "predator": colors.PREDATOR_MARKER,
            "poi": colors.POI_MARKER,
        }
        return visual_colors.get(kind, colors.GOURD)

    def _draw_player(self, camera, center_x: int, center_y: int) -> None:
        """Draw draw player.
        
        Args:
            camera: Input value used by this operation.
            center_x: Input value used by this operation.
            center_y: Input value used by this operation.
        """
        transform = self.player.get("transform")
        sprite = self.player.get("sprite")
        screen_x = round(center_x + (transform.x - camera.x) * camera.zoom)
        screen_y = round(center_y + (transform.y - camera.y) * camera.zoom)
        width = max(1, round(sprite.width * camera.zoom))
        height = max(1, round(sprite.height * camera.zoom))
        raylib.draw_rectangle(screen_x - width // 2, screen_y - height, width, height, colors.PLAYER)
        raylib.draw_circle(screen_x + width // 2, screen_y - height + 3, max(1.0, 3 * camera.zoom), (255, 255, 180, 50))

    def _draw_player_flashlight(self, camera, center_x: int, center_y: int) -> None:
        """Draw the currently selected player flashlight mode."""
        transform = self.player.get("transform")
        sprite = self.player.get("sprite")
        light = self.player.get("light")
        screen_x = round(center_x + (transform.x - camera.x) * camera.zoom)
        screen_y = round(center_y + (transform.y - camera.y) * camera.zoom)
        player_height = max(1, round(sprite.height * camera.zoom))
        self.light_system.draw_player_flashlight(
            light=light,
            screen_x=screen_x,
            screen_y=screen_y,
            player_height=player_height,
            facing=self.player_facing,
            zoom=camera.zoom,
        )

    def _draw_exit(self, camera, center_x: int, center_y: int) -> None:
        """Draw draw exit.
        
        Args:
            camera: Input value used by this operation.
            center_x: Input value used by this operation.
            center_y: Input value used by this operation.
        """
        x, y, width, height = self.exit_rect
        screen_x = round(center_x + (x - camera.x) * camera.zoom)
        screen_y = round(center_y + (y - camera.y) * camera.zoom)
        rect_w = max(1, round(width * camera.zoom))
        rect_h = max(1, round(height * camera.zoom))
        raylib.draw_rectangle(screen_x, screen_y, rect_w, rect_h, (35, 75, 42, 90))
        raylib.draw_line(screen_x + rect_w - 4, screen_y, screen_x + rect_w - 4, screen_y + rect_h, colors.EXIT)

    def _overlay_lines(self) -> list[str]:
        """Execute overlay lines.
        
        Returns:
            Result produced by this operation.
        """
        transform = self.player.get("transform")
        velocity = self.player.get("velocity")
        health = self.player.get("health")
        statuses = self.player.get("statuses")
        camera = self.camera_system.controller.get_render_state()
        language_key = f"language.{self.localization.current_language.value}"
        language_name = self.localization.tr(language_key)
        active_status = ", ".join(statuses.names()) if statuses.active else self.localization.tr("status.none")
        metrics = self.debug_metrics.collect(
            fps=raylib.get_fps(),
            raw_frame_time=self.raw_frame_time,
            update_delta_time=self.update_delta_time,
            object_stats=self._collect_object_debug_stats(),
            map_width_tiles=self.map_data.width,
        )
        memory_text = (
            self.localization.tr("debug.memory_unknown")
            if metrics.memory_rss_mb is None
            else self.localization.tr("debug.memory_rss", memory=metrics.memory_rss_mb)
        )
        return [
            self.localization.tr("debug.overlay"),
            self.localization.tr("debug.fps", fps=metrics.fps),
            self.localization.tr("debug.frame_time", frame_time=metrics.frame_time_ms),
            self.localization.tr("debug.update_delta", update_delta=metrics.update_delta_ms),
            memory_text,
            self.localization.tr(
                "debug.objects",
                total=metrics.objects.total_objects,
                active=metrics.objects.active_objects,
                visible=metrics.objects.visible_objects,
            ),
            self.localization.tr(
                "debug.object_breakdown",
                hazards=metrics.objects.hazards,
                interactables=metrics.objects.interactables,
                observations=metrics.objects.observations,
            ),
            self.localization.tr(
                "debug.chunks",
                mode=metrics.chunks.mode,
                loaded=metrics.chunks.loaded_chunks,
                total=metrics.chunks.total_chunks,
                active=metrics.chunks.active_chunks,
                width=metrics.chunks.chunk_width_tiles,
            ),
            self.localization.tr("scene.current", scene=self.world_state.current_scene),
            self.localization.tr("zone.current", zone=self.world_state.current_zone),
            self.localization.tr("map.current", map_id=self.world_state.current_map_id),
            self.localization.tr("debug.flashlight", mode=self.player.get("light").mode),
            self.localization.tr(
                "debug.map_size",
                width=self.map_data.width,
                height=self.map_data.height,
                pixel_width=self.map_data.pixel_width,
                pixel_height=self.map_data.pixel_height,
            ),
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
            self.localization.tr("journal.debug", count=self.journal_system.unlocked_count),
            self.localization.tr("debug.last_event", event=self.status_system.last_event),
        ]

    def _collect_object_debug_stats(self) -> ObjectDebugStats:
        """Execute collect object debug stats.
        
        Returns:
            Result produced by this operation.
        """
        active_interactables = [
            entity
            for entity in self.interactables
            if not entity.get("consumable")["used"]
        ]
        active_observations = [
            entity
            for entity in self.observation_markers
            if not entity.get("consumable")["used"]
        ]
        all_objects = [self.player, *self.hazards, *self.interactables, *self.observation_markers]
        active_objects = [self.player, *self.hazards, *active_interactables, *active_observations]
        visible_objects = sum(1 for entity in active_objects if self._is_entity_visible(entity))
        return ObjectDebugStats(
            total_objects=len(all_objects),
            active_objects=len(active_objects),
            visible_objects=visible_objects,
            hazards=len(self.hazards),
            interactables=len(self.interactables),
            observations=len(self.observation_markers),
        )

    def _is_entity_visible(self, entity) -> bool:
        """Execute is entity visible.
        
        Args:
            entity: Input value used by this operation.
        
        Returns:
            Result produced by this operation.
        """
        transform = entity.get("transform")
        sprite = entity.get("sprite")
        camera = self.camera_system.controller.get_render_state()
        half_width = (self.internal_width / max(camera.zoom, 0.001)) / 2.0
        half_height = (self.internal_height / max(camera.zoom, 0.001)) / 2.0
        entity_half_width = max(1.0, float(sprite.width) / 2.0)
        entity_height = max(1.0, float(sprite.height))
        left = camera.x - half_width - entity_half_width
        right = camera.x + half_width + entity_half_width
        top = camera.y - half_height - entity_height
        bottom = camera.y + half_height + entity_height
        return left <= transform.x <= right and top <= transform.y <= bottom
