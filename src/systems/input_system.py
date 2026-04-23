from __future__ import annotations

from src.utils import rl as raylib


class InputSystem:
    def horizontal_axis(self) -> float:
        axis = 0.0
        if raylib.is_key_down(raylib.KEY_A) or raylib.is_key_down(raylib.KEY_LEFT):
            axis -= 1.0
        if raylib.is_key_down(raylib.KEY_D) or raylib.is_key_down(raylib.KEY_RIGHT):
            axis += 1.0
        return axis

    @staticmethod
    def is_jump_pressed() -> bool:
        return raylib.is_key_pressed(raylib.KEY_SPACE) or raylib.is_key_pressed(raylib.KEY_W)

    @staticmethod
    def is_interact_pressed() -> bool:
        return raylib.is_key_pressed(raylib.KEY_F)
