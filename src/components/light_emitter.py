"""Light emitter component used by player-held and world light sources."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class LightEmitterComponent:
    """Store flashlight/light-source runtime state.

    Attributes:
        enabled: Whether the light source can emit light.
        mode: Current flashlight mode: ``off``, ``radial``, or ``beam``.
        radius: Radial light radius in world pixels.
        beam_distance: Beam light distance in world pixels.
        beam_half_width: Half-width of the beam end in world pixels.
    """

    enabled: bool = True
    mode: str = "off"
    radius: float = 72.0
    beam_distance: float = 132.0
    beam_half_width: float = 34.0
