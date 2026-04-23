from __future__ import annotations

from src.components.interaction import InteractionComponent
from src.components.state import StateComponent
from src.components.transform import TransformComponent
from src.entities.entity import Entity


class FloraEntity(Entity):
    """Basic flora entity."""

    def __init__(
        self,
        entity_id: str,
        name_id: str,
        x: float,
        y: float,
        *,
        species_id: str,
    ) -> None:
        super().__init__(entity_id=entity_id, name_id=name_id)
        self.add_component("transform", TransformComponent(x=x, y=y))
        self.add_component("state", StateComponent())
        self.add_component("interaction", InteractionComponent())
        self.add_component(
            "biota",
            {
                "entity_kind": "flora",
                "species_id": species_id,
            },
        )
