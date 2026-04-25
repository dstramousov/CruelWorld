"""Configurable input binding system used by gameplay and UI code."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from src.systems.log_system import get_logger
from src.utils import rl as raylib

logger = get_logger(__name__)


class InputSystem:
    """Maps configurable actions to raylib key checks."""

    _DEFAULT_BINDINGS: dict[str, list[str]] = {
        "move_left": ["A", "LEFT"],
        "move_right": ["D", "RIGHT"],
        "jump": ["SPACE", "W", "UP"],
        "interact": ["F"],
        "communicator_toggle": ["TAB", "J"],
        "communicator_close": ["ESCAPE", "TAB", "J"],
        "communicator_next": ["DOWN", "S"],
        "communicator_previous": ["UP", "W"],
        "communicator_menu_next": ["RIGHT"],
        "communicator_menu_previous": ["LEFT"],
        "communicator_activate": ["ENTER"],
        "communicator_cancel": ["BACKSPACE"],
        "flashlight_cycle": ["L"],
        "toggle_language": ["F1"],
        "toggle_debug": ["LEFT_SHIFT+D", "RIGHT_SHIFT+D"],
        "zoom_out": ["Q"],
        "zoom_in": ["E"],
    }

    def __init__(self, bindings: Mapping[str, Sequence[str]] | None = None) -> None:
        """Execute init.
        
        Args:
            bindings: Input value used by this operation.
        """
        self._bindings = self._normalize_bindings(bindings)

    def horizontal_axis(self) -> float:
        # Convert configured left/right bindings into one normalized movement axis.
        """Execute horizontal axis.
        
        Returns:
            Result produced by this operation.
        """
        axis = 0.0
        if self.is_action_down("move_left"):
            axis -= 1.0
        if self.is_action_down("move_right"):
            axis += 1.0
        return axis

    def is_jump_pressed(self) -> bool:
        """Return whether jump pressed is true.
        
        Returns:
            Result produced by this operation.
        """
        return self.is_action_pressed("jump")

    def is_interact_pressed(self) -> bool:
        """Return whether interact pressed is true.
        
        Returns:
            Result produced by this operation.
        """
        return self.is_action_pressed("interact")

    def is_communicator_toggle_pressed(self) -> bool:
        """Return whether communicator toggle pressed is true.
        
        Returns:
            Result produced by this operation.
        """
        return self.is_action_pressed("communicator_toggle")

    def is_communicator_close_pressed(self) -> bool:
        """Return whether communicator close pressed is true.
        
        Returns:
            Result produced by this operation.
        """
        return self.is_action_pressed("communicator_close")

    def is_communicator_next_pressed(self) -> bool:
        """Return whether communicator next pressed is true.
        
        Returns:
            Result produced by this operation.
        """
        return self.is_action_pressed("communicator_next")

    def is_communicator_previous_pressed(self) -> bool:
        """Return whether communicator previous pressed is true.
        
        Returns:
            Result produced by this operation.
        """
        return self.is_action_pressed("communicator_previous")

    def is_communicator_menu_next_pressed(self) -> bool:
        """Return whether communicator menu next pressed is true.
        
        Returns:
            Result produced by this operation.
        """
        return self.is_action_pressed("communicator_menu_next")

    def is_communicator_menu_previous_pressed(self) -> bool:
        """Return whether communicator menu previous pressed is true.
        
        Returns:
            Result produced by this operation.
        """
        return self.is_action_pressed("communicator_menu_previous")

    def is_communicator_activate_pressed(self) -> bool:
        """Return whether communicator activation key was pressed.

        Returns:
            True when the configured activation key was pressed.
        """
        return self.is_action_pressed("communicator_activate")

    def is_communicator_cancel_pressed(self) -> bool:
        """Return whether communicator cancel key was pressed.

        Returns:
            True when the configured cancel key was pressed.
        """
        return self.is_action_pressed("communicator_cancel")

    def is_flashlight_cycle_pressed(self) -> bool:
        """Return whether flashlight cycle pressed is true.
        
        Returns:
            Result produced by this operation.
        """
        return self.is_action_pressed("flashlight_cycle")

    def is_action_down(self, action: str) -> bool:
        """Return whether action down is true.
        
        Args:
            action: Input value used by this operation.
        
        Returns:
            Result produced by this operation.
        """
        return any(self._chord_down(chord) for chord in self._bindings.get(action, ()))

    def is_action_pressed(self, action: str) -> bool:
        """Return whether action pressed is true.
        
        Args:
            action: Input value used by this operation.
        
        Returns:
            Result produced by this operation.
        """
        return any(self._chord_pressed(chord) for chord in self._bindings.get(action, ()))

    @classmethod
    def _normalize_bindings(cls, bindings: Mapping[str, Sequence[str]] | None) -> dict[str, list[tuple[int, ...]]]:
        # Merge defaults with config values and pre-parse strings like
        # "LEFT_SHIFT+D" into raylib key-code tuples for fast checks.
        """Execute normalize bindings.
        
        Args:
            bindings: Input value used by this operation.
        
        Returns:
            Result produced by this operation.
        """
        raw_bindings: dict[str, Sequence[str]] = dict(cls._DEFAULT_BINDINGS)
        if bindings:
            raw_bindings.update(bindings)

        normalized: dict[str, list[tuple[int, ...]]] = {}
        for action, chords in raw_bindings.items():
            normalized[action] = []
            for chord in chords:
                try:
                    normalized[action].append(cls._parse_chord(chord))
                except ValueError as exc:
                    logger.log_exception_event("INPUT_BINDING_IGNORED", exc, action=action, chord=chord)
        return normalized

    @classmethod
    def _parse_chord(cls, chord: str) -> tuple[int, ...]:
        """Execute parse chord.
        
        Args:
            chord: Input value used by this operation.
        
        Returns:
            Result produced by this operation.
        """
        parts = [part.strip() for part in chord.upper().split("+") if part.strip()]
        if not parts:
            raise ValueError("Empty key chord")
        return tuple(cls._key_code(part) for part in parts)

    @staticmethod
    def _key_code(name: str) -> int:
        """Execute key code.
        
        Args:
            name: Input value used by this operation.
        
        Returns:
            Result produced by this operation.
        """
        constant_name = f"KEY_{name}"
        if not hasattr(raylib, constant_name):
            raise ValueError(f"Unknown key name: {name}")
        return int(getattr(raylib, constant_name))

    @staticmethod
    def _chord_down(chord: tuple[int, ...]) -> bool:
        """Execute chord down.
        
        Args:
            chord: Input value used by this operation.
        
        Returns:
            Result produced by this operation.
        """
        return all(raylib.is_key_down(key) for key in chord)

    @staticmethod
    def _chord_pressed(chord: tuple[int, ...]) -> bool:
        """Execute chord pressed.
        
        Args:
            chord: Input value used by this operation.
        
        Returns:
            Result produced by this operation.
        """
        if len(chord) == 1:
            return raylib.is_key_pressed(chord[0])
        *modifiers, trigger = chord
        return all(raylib.is_key_down(key) for key in modifiers) and raylib.is_key_pressed(trigger)
