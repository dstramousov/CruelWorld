from __future__ import annotations

import pytest

from src.components.statuses import StatusInstance, StatusReceiverComponent
from src.entities.entity import Entity
from src.entities.player import Player


def test_entity_add_and_get_component() -> None:
    entity = Entity("id", "name")
    component = {"value": 1}

    entity.add_component("test", component)

    assert entity.get("test") is component


def test_entity_get_missing_component_raises_key_error() -> None:
    entity = Entity("id", "name")

    with pytest.raises(KeyError):
        entity.get("missing")


def test_status_receiver_names_returns_active_status_ids() -> None:
    receiver = StatusReceiverComponent()
    receiver.active["poisoned"] = StatusInstance("poisoned", 1.0, 1.0, 1.0)

    assert receiver.names() == ["poisoned"]


def test_player_has_required_core_components() -> None:
    player = Player()

    for component_name in (
        "transform",
        "sprite",
        "collider",
        "velocity",
        "gravity",
        "state",
        "health",
        "statuses",
        "light",
    ):
        assert component_name in player.components

    assert player.entity_id == "player"
    assert player.get("health").current == 100
