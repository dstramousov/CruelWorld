from __future__ import annotations

from src.entities.factories import (
    create_hazard_entity,
    create_interactable_entity,
    create_observation_entity,
)


def test_create_hazard_entity_uses_matching_spec_prefix() -> None:
    entity = create_hazard_entity("needle_halo_bush_03", 10.0, 20.0, 16, 24)

    assert entity.entity_id == "needle_halo_bush_03"
    assert entity.get("transform").x == 10.0
    assert entity.get("sprite").width == 16
    assert entity.components["biota"]["species_id"] == "needle_halo_bush"
    assert entity.components["hazard"]["health_delta"] == -4


def test_create_interactable_entity_adds_interaction_and_consumable_components() -> None:
    entity = create_interactable_entity("blood_lantern_fig_01", 1.0, 2.0, 8, 9)
    interaction = entity.get("interaction")

    assert entity.components["biota"]["species_id"] == "blood_lantern_fig"
    assert interaction.interaction_id == "eat_high_energy_fig"
    assert interaction.applies_statuses == ["marked"]
    assert interaction.health_delta == 12
    assert entity.components["consumable"] == {"single_use": True, "used": False}


def test_create_observation_entity_uses_observation_kind() -> None:
    entity = create_observation_entity("rain_choir_frog_pool_01", 1.0, 2.0, 8, 9)

    assert entity.components["biota"]["entity_kind"] == "observation"
    assert entity.components["biota"]["species_id"] == "rain_choir_frog"
    assert entity.get("interaction").prompt_key == "hint.inspect"


def test_unknown_hazard_uses_safe_fallback_spec() -> None:
    entity = create_hazard_entity("unknown_hazard_01", 0.0, 0.0, 1, 1)

    assert entity.components["biota"]["species_id"] == "grave_lace_vine"
