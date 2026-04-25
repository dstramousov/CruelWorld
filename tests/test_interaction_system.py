from __future__ import annotations

from src.components.health import HealthComponent
from src.components.interaction import InteractionComponent
from src.components.statuses import StatusReceiverComponent
from src.components.transform import TransformComponent
from src.entities.entity import Entity
from src.systems.interaction_system import InteractionSystem
from src.systems.status_system import StatusDefinition, StatusSystem


def _status_system() -> StatusSystem:
    return StatusSystem(
        {
            "marked": StatusDefinition("marked", "name", "desc", 10.0, 99.0, 0, (0, 0, 0, 255)),
            "poisoned": StatusDefinition("poisoned", "name", "desc", 10.0, 99.0, 0, (0, 0, 0, 255)),
        }
    )


def _player() -> Entity:
    player = Entity("player", "entity.player")
    player.add_component("statuses", StatusReceiverComponent())
    player.add_component("health", HealthComponent(current=50, maximum=100))
    return player


def _interactable(entity_id: str, x: float, y: float, prompt_key: str = "hint.interact") -> Entity:
    entity = Entity(entity_id, entity_id)
    entity.add_component("transform", TransformComponent(x=x, y=y))
    entity.add_component(
        "interaction",
        InteractionComponent(
            interaction_id="test",
            prompt_key=prompt_key,
            message_key="msg.test",
            discovery_key="disc.test",
            clears_statuses=["poisoned"],
            applies_statuses=["marked"],
            health_delta=12,
        ),
    )
    entity.add_component("biota", {"species_id": "test_species", "entity_kind": "flora"})
    return entity


def test_find_nearest_sets_context_for_closest_interactable() -> None:
    system = InteractionSystem()
    far = _interactable("far", 40.0, 0.0)
    near = _interactable("near", 10.0, 0.0)

    result = system.find_nearest(0.0, 0.0, [far, near], radius=50.0)

    assert result is near
    assert system.context.available is True
    assert system.context.target_id == "near"
    assert system.context.prompt_key == "hint.interact"


def test_find_nearest_clears_context_when_nothing_is_in_range() -> None:
    system = InteractionSystem()
    result = system.find_nearest(0.0, 0.0, [_interactable("far", 100.0, 0.0)], radius=10.0)

    assert result is None
    assert system.context.available is False
    assert system.context.target_id == "none"


def test_execute_applies_interaction_payload_to_player() -> None:
    system = InteractionSystem()
    status_system = _status_system()
    player = _player()
    status_system.apply(player.get("statuses"), "poisoned")
    entity = _interactable("blue_mercy_gourd_01", 0.0, 0.0)

    result = system.execute(entity, player, status_system)

    assert result.message_key == "msg.test"
    assert result.discovery_key == "disc.test"
    assert result.removed_statuses == ("poisoned",)
    assert result.applied_statuses == ("marked",)
    assert result.health_delta == 12
    assert player.get("health").current == 62
    assert player.get("statuses").names() == ["marked"]


def test_execute_clamps_health_to_maximum() -> None:
    system = InteractionSystem()
    status_system = _status_system()
    player = _player()
    player.get("health").current = 95
    entity = _interactable("healing_resource", 0.0, 0.0)

    system.execute(entity, player, status_system)

    assert player.get("health").current == 100
