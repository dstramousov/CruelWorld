from __future__ import annotations

from src.components.interaction import InteractionComponent
from src.components.sprite import SpriteComponent
from src.entities.flora_entity import FloraEntity


def create_grave_lace_vine(entity_id: str, x: float, y: float, width: int, height: int) -> FloraEntity:
    """Create a hazard flora entity."""
    entity = FloraEntity(
        entity_id=entity_id,
        name_id="flora.grave_lace_vine.name",
        x=x,
        y=y,
        species_id="grave_lace_vine",
    )
    entity.add_component("sprite", SpriteComponent(width=width, height=height))
    entity.add_component("hazard", {"status_on_touch": "poisoned"})
    return entity



def create_blue_mercy_gourd(entity_id: str, x: float, y: float, width: int, height: int) -> FloraEntity:
    """Create a healing flora entity."""
    entity = FloraEntity(
        entity_id=entity_id,
        name_id="flora.blue_mercy_gourd.name",
        x=x,
        y=y,
        species_id="blue_mercy_gourd",
    )
    entity.add_component("sprite", SpriteComponent(width=width, height=height))
    entity.add_component(
        "interaction",
        InteractionComponent(
            interaction_id="cleanse_poison",
            prompt_key="hint.interact",
            clears_statuses=["poisoned"],
        ),
    )
    entity.add_component("consumable", {"single_use": True, "used": False})
    return entity
