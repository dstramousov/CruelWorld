"""Flora Entity module for entity definitions and factories for gameplay objects."""

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
        """Execute init.
        
        Args:
            entity_id: Input value used by this operation.
            name_id: Input value used by this operation.
            x: Input value used by this operation.
            y: Input value used by this operation.
            species_id: Input value used by this operation.
        """
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
