"""Interaction System module for runtime gameplay systems."""

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


@dataclass(frozen=True, slots=True)
class InteractionResult:
    """Result returned after an interaction is executed."""

    message_key: str
    discovery_key: str = ""
    removed_statuses: tuple[str, ...] = ()
    applied_statuses: tuple[str, ...] = ()
    health_delta: int = 0


class InteractionSystem:
    """Detects and executes nearby interactions."""

    def __init__(self) -> None:
        """Execute init.
        """
        self.context = InteractionContext()
        self._last_target_id = "none"

    def clear_context(self) -> None:
        """Clear the current interaction prompt state."""
        self.context = InteractionContext()
        self._last_target_id = "none"

    def find_nearest(self, player_x: float, player_y: float, interactables: list[Any], radius: float = 34.0) -> Any | None:
        # Scan nearby interactables every frame and keep context data for HUD
        # prompts and biota proximity logging.
        """Execute find nearest.
        
        Args:
            player_x: Input value used by this operation.
            player_y: Input value used by this operation.
            interactables: Input value used by this operation.
            radius: Input value used by this operation.
        
        Returns:
            Result produced by this operation.
        """
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
            interaction = nearest.get("interaction")
            self.context = InteractionContext(
                available=True,
                target_id=nearest.entity_id,
                prompt_key=interaction.prompt_key,
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

    def execute(self, entity: Any, player: Any, status_system: Any) -> InteractionResult:
        # Apply the data-driven interaction payload to the player and return a
        # compact result for messages and journal unlocks.
        """Execute execute.
        
        Args:
            entity: Input value used by this operation.
            player: Input value used by this operation.
            status_system: Input value used by this operation.
        
        Returns:
            Result produced by this operation.
        """
        interaction = entity.get("interaction")
        statuses = player.get("statuses")
        health = player.get("health")
        removed = tuple(status_system.remove_many(statuses, interaction.clears_statuses))
        applied: list[str] = []
        for status_id in interaction.applies_statuses:
            if status_system.apply(statuses, status_id):
                applied.append(status_id)

        if interaction.health_delta != 0:
            health.current = max(0, min(health.maximum, health.current + interaction.health_delta))

        logger.log_event(
            "INTERACTION_EXECUTED",
            level=20,
            target=entity.entity_id,
            interaction_id=interaction.interaction_id,
            removed_statuses=removed,
            applied_statuses=applied,
            health_delta=interaction.health_delta,
        )
        biota = entity.components.get("biota")
        if biota is not None:
            logger.log_biota_event(
                biota.get("species_id", "unknown"),
                "INTERACTED",
                level=20,
                entity_kind=biota.get("entity_kind", "flora"),
                entity_id=entity.entity_id,
                interaction_id=interaction.interaction_id,
            )

        return InteractionResult(
            message_key=interaction.message_key,
            discovery_key=interaction.discovery_key,
            removed_statuses=removed,
            applied_statuses=tuple(applied),
            health_delta=interaction.health_delta,
        )
