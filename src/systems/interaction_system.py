from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.systems.log_system import get_logger

logger = get_logger(__name__)


@dataclass(slots=True)
class InteractionContext:
    """Runtime interaction state for HUD and debug tools."""

    available: bool = False
    target_id: str = "none"
    prompt_key: str = ""


class InteractionSystem:
    """Detects and executes nearby interactions."""

    def __init__(self) -> None:
        self.context = InteractionContext()
        self._last_target_id = "none"

    def find_nearest(self, player_x: float, player_y: float, interactables: list[Any], radius: float = 24.0) -> Any | None:
        nearest = None
        nearest_distance = radius * radius
        for entity in interactables:
            transform = entity.get("transform")
            dx = transform.x - player_x
            dy = transform.y - player_y
            distance = dx * dx + dy * dy
            if distance <= nearest_distance:
                nearest = entity
                nearest_distance = distance
        if nearest is None:
            if self._last_target_id != "none":
                logger.log_event("INTERACTION_TARGET_LOST", target=self._last_target_id)
            self._last_target_id = "none"
            self.context = InteractionContext()
        else:
            self.context = InteractionContext(
                available=True,
                target_id=nearest.entity_id,
                prompt_key="hint.interact",
            )
            if self._last_target_id != nearest.entity_id:
                logger.log_event(
                    "INTERACTION_AVAILABLE",
                    target=nearest.entity_id,
                    distance_sq=round(nearest_distance, 3),
                )
                biota = nearest.components.get("biota")
                if biota is not None:
                    logger.log_biota_event(
                        biota.get("species_id", "unknown"),
                        "PLAYER_NEARBY",
                        entity_kind=biota.get("entity_kind", "flora"),
                        entity_id=nearest.entity_id,
                        distance_sq=round(nearest_distance, 3),
                    )
            self._last_target_id = nearest.entity_id
        return nearest

    def execute(self, entity: Any, player: Any, status_system: Any) -> str:
        interaction = entity.get("interaction")
        clears_statuses = getattr(interaction, "clears_statuses", [])
        logger.log_event(
            "INTERACTION_EXECUTED",
            level=20,
            target=entity.entity_id,
            clears_statuses=clears_statuses,
        )
        biota = entity.components.get("biota")
        if biota is not None:
            logger.log_biota_event(
                biota.get("species_id", "unknown"),
                "INTERACTED",
                level=20,
                entity_kind=biota.get("entity_kind", "flora"),
                entity_id=entity.entity_id,
                clears_statuses=clears_statuses,
            )
        if clears_statuses:
            removed = status_system.remove_many(player.get("statuses"), clears_statuses)
            logger.log_event(
                "INTERACTION_COMPLETED",
                level=20,
                target=entity.entity_id,
                removed=removed,
            )
            return "cleansed" if removed else "used"
        logger.log_event(
            "INTERACTION_NO_EFFECT",
            level=20,
            target=entity.entity_id,
        )
        return "used"
