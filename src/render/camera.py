from __future__ import annotations

from dataclasses import dataclass

from src.utils.math2d import lerp


def snap_camera_axis(value: float, zoom: float) -> float:
    """Snap a camera axis to the internal pixel grid for stable world rendering."""
    if zoom <= 0.0:
        return round(value)
    return round(value * zoom) / zoom


@dataclass(slots=True)
class CameraState:
    x: float = 0.0
    y: float = 0.0
    zoom: float = 1.0
    follow_speed: float = 0.085
    look_ahead_x: float = 28.0


class CameraController:
    def __init__(self) -> None:
        self.state = CameraState(x=0.0, y=0.0)

    def update(self, target_x: float, target_y: float, move_dir: float) -> None:
        desired_x = target_x + move_dir * self.state.look_ahead_x
        desired_y = target_y
        self.state.x = lerp(self.state.x, desired_x, self.state.follow_speed)
        self.state.y = lerp(self.state.y, desired_y, self.state.follow_speed)

    def get_render_state(self) -> CameraState:
        return CameraState(
            x=snap_camera_axis(self.state.x, self.state.zoom),
            y=snap_camera_axis(self.state.y, self.state.zoom),
            zoom=self.state.zoom,
            follow_speed=self.state.follow_speed,
            look_ahead_x=self.state.look_ahead_x,
        )
