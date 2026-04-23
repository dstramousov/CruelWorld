from __future__ import annotations

from src.utils import rl as raylib

from src.core.game import Game
from src.systems.log_system import configure_logging, get_logger
from src.utils.paths import CONFIG_DIR
from src.utils.serialization import load_json

logger = get_logger(__name__)


def main() -> int:
    configure_logging()
    game_config = load_json(CONFIG_DIR / "game.json")

    window_cfg = game_config["window"]
    render_cfg = game_config["render"]
    application_cfg = game_config.get("application", {})
    timing_cfg = game_config.get("timing", {})
    pause_on_focus_lost = bool(application_cfg.get("pause_on_focus_lost", True))
    max_delta_time = float(timing_cfg.get("max_delta_time", 1.0 / 30.0))

    raylib.set_config_flags(raylib.FLAG_VSYNC_HINT)
    raylib.init_window(window_cfg["width"], window_cfg["height"], window_cfg["title"])
    raylib.set_target_fps(window_cfg["target_fps"])

    target = raylib.load_render_texture(
        render_cfg["internal_width"],
        render_cfg["internal_height"],
    )
    game = Game(config=game_config)
    logger.log_event(
        "APP_STARTED",
        level=20,
        window_width=window_cfg["width"],
        window_height=window_cfg["height"],
        internal_width=render_cfg["internal_width"],
        internal_height=render_cfg["internal_height"],
        pause_on_focus_lost=pause_on_focus_lost,
        max_delta_time=max_delta_time,
    )

    last_focus_state = raylib.is_window_focused()
    if last_focus_state:
        logger.log_event("APP_FOCUS_GAINED", level=20)
    else:
        logger.log_event("APP_FOCUS_LOST", level=30)

    try:
        while not raylib.window_should_close():
            current_focus_state = raylib.is_window_focused()
            if current_focus_state != last_focus_state:
                if current_focus_state:
                    logger.log_event("APP_FOCUS_GAINED", level=20)
                else:
                    logger.log_event("APP_FOCUS_LOST", level=30)
                last_focus_state = current_focus_state

            raw_delta_time = raylib.get_frame_time()
            delta_time = min(raw_delta_time, max_delta_time)
            if raw_delta_time > max_delta_time:
                logger.log_event(
                    "APP_DELTA_TIME_CLAMPED",
                    raw_delta_time=round(raw_delta_time, 6),
                    clamped_delta_time=round(delta_time, 6),
                )

            if not (pause_on_focus_lost and not current_focus_state):
                game.update(delta_time)

            raylib.begin_texture_mode(target)
            game.draw(
                internal_width=render_cfg["internal_width"],
                internal_height=render_cfg["internal_height"],
            )
            raylib.end_texture_mode()

            raylib.begin_drawing()
            raylib.clear_background(raylib.BLACK)
            source = raylib.Rectangle(
                0,
                0,
                float(render_cfg["internal_width"]),
                float(-render_cfg["internal_height"]),
            )
            destination = raylib.Rectangle(
                0,
                0,
                float(window_cfg["width"]),
                float(window_cfg["height"]),
            )
            raylib.draw_texture_pro(
                target.texture,
                source,
                destination,
                raylib.Vector2(0.0, 0.0),
                0.0,
                raylib.WHITE,
            )
            game.draw_debug_overlay(
                window_width=window_cfg["width"],
                window_height=window_cfg["height"],
            )
            raylib.end_drawing()
    finally:
        game.shutdown()
        raylib.unload_render_texture(target)
        raylib.close_window()
        logger.log_event("APP_STOPPED", level=20)

    return 0
