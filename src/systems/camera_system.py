from __future__ import annotations

from dataclasses import dataclass

from src.render.camera import CameraController
from src.systems.log_system import get_logger

logger = get_logger(__name__)


@dataclass(slots=True)
class CameraProfile:
    name: str
    zoom: float
    follow_speed: float
    look_ahead_x: float
    offset_y: float = 0.0


class CameraSystem:
    def __init__(self) -> None:
        self.controller = CameraController()
        self.profiles = {
            "default_exploration": CameraProfile(
                name="default_exploration",
                zoom=1.0,
                follow_speed=0.085,
                look_ahead_x=22.0,
                offset_y=-12.0,
            ),
            "threat_focus": CameraProfile(
                name="threat_focus",
                zoom=1.12,
                follow_speed=0.1,
                look_ahead_x=32.0,
                offset_y=-18.0,
            ),
            "threat_reveal": CameraProfile(
                name="threat_reveal",
                zoom=1.12,
                follow_speed=0.1,
                look_ahead_x=32.0,
                offset_y=-18.0,
            ),
            "recovery_pocket": CameraProfile(
                name="recovery_pocket",
                zoom=1.08,
                follow_speed=0.075,
                look_ahead_x=18.0,
                offset_y=-18.0,
            ),
        }
        self.profile_name = "default_exploration"
        self.active_trigger = "none"
        self.set_profile(self.profile_name)
        logger.log_event("CAMERA_RENDER_PIXEL_SNAP_ENABLED", level=20)

    def set_profile(self, profile_name: str, trigger_name: str = "none") -> None:
        if profile_name not in self.profiles:
            logger.log_event(
                "CAMERA_PROFILE_UNKNOWN",
                level=30,
                profile=profile_name,
                trigger=trigger_name,
            )
            return
        previous_profile = self.profile_name
        profile = self.profiles[profile_name]
        state = self.controller.state
        state.zoom = profile.zoom
        state.follow_speed = profile.follow_speed
        state.look_ahead_x = profile.look_ahead_x
        self.profile_name = profile_name
        self.active_trigger = trigger_name
        logger.log_event(
            "CAMERA_PROFILE_CHANGED",
            level=20,
            previous=previous_profile,
            current=profile_name,
            trigger=trigger_name,
            zoom=profile.zoom,
            follow_speed=profile.follow_speed,
            look_ahead_x=profile.look_ahead_x,
        )

    def update(self, target_x: float, target_y: float, move_dir: float) -> None:
        profile = self.profiles[self.profile_name]
        self.controller.update(
            target_x=target_x,
            target_y=target_y + profile.offset_y,
            move_dir=move_dir,
        )

    def zoom_in(self) -> None:
        self.controller.state.zoom = min(self.controller.state.zoom + 0.05, 1.8)
        logger.log_event("CAMERA_ZOOM_IN", zoom=self.controller.state.zoom)

    def zoom_out(self) -> None:
        self.controller.state.zoom = max(self.controller.state.zoom - 0.05, 0.7)
        logger.log_event("CAMERA_ZOOM_OUT", zoom=self.controller.state.zoom)
