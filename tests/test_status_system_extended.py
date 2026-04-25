from __future__ import annotations

from src.components.health import HealthComponent
from src.components.statuses import StatusReceiverComponent
from src.systems.status_system import StatusDefinition, StatusSystem


def _system() -> StatusSystem:
    return StatusSystem(
        {
            "poisoned": StatusDefinition(
                status_id="poisoned",
                name_key="status.poisoned.name",
                description_key="status.poisoned.description",
                duration=5.0,
                tick_interval=1.0,
                tick_damage=2,
                color=(1, 2, 3, 4),
            ),
            "slowed": StatusDefinition(
                status_id="slowed",
                name_key="status.slowed.name",
                description_key="status.slowed.description",
                duration=3.0,
                tick_interval=99.0,
                tick_damage=0,
                color=(5, 6, 7, 8),
            ),
        }
    )


def test_apply_adds_known_status_and_rejects_unknown_status() -> None:
    statuses = StatusReceiverComponent()
    system = _system()

    assert system.apply(statuses, "poisoned") is True
    assert "poisoned" in statuses.active
    assert system.last_event == "applied:poisoned"

    assert system.apply(statuses, "unknown") is False


def test_apply_existing_status_refreshes_remaining_duration() -> None:
    statuses = StatusReceiverComponent()
    system = _system()
    system.apply(statuses, "poisoned")
    statuses.active["poisoned"].remaining = 1.0

    assert system.apply(statuses, "poisoned") is True

    assert statuses.active["poisoned"].remaining == 5.0
    assert system.last_event == "refreshed:poisoned"


def test_update_ticks_damage_and_expires_statuses() -> None:
    statuses = StatusReceiverComponent()
    health = HealthComponent(current=10, maximum=10)
    system = _system()
    system.apply(statuses, "poisoned")

    system.update(statuses, health, 1.0)

    assert health.current == 8
    assert system.last_event == "tick:poisoned"

    system.update(statuses, health, 4.0)

    assert "poisoned" not in statuses.active
    assert system.last_event == "expired:poisoned"


def test_remove_many_returns_removed_statuses_only() -> None:
    statuses = StatusReceiverComponent()
    system = _system()
    system.apply(statuses, "poisoned")
    system.apply(statuses, "slowed")

    removed = system.remove_many(statuses, ["missing", "poisoned"])

    assert removed == ["poisoned"]
    assert statuses.names() == ["slowed"]
