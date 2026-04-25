"""Factories module for entity definitions and factories for gameplay objects."""

from __future__ import annotations

from dataclasses import dataclass

from src.components.interaction import InteractionComponent
from src.components.sprite import SpriteComponent
from src.entities.flora_entity import FloraEntity


@dataclass(frozen=True, slots=True)
class FloraSpec:
    """Static data used to create flora and observation entities."""

    species_id: str
    name_id: str
    color_kind: str
    interaction_id: str
    message_key: str
    discovery_key: str = ""
    clears_statuses: tuple[str, ...] = ()
    applies_statuses: tuple[str, ...] = ()
    health_delta: int = 0
    single_use: bool = True


HAZARD_SPECS: dict[str, FloraSpec] = {
    "grave_lace_vine": FloraSpec(
        species_id="grave_lace_vine",
        name_id="flora.grave_lace_vine.name",
        color_kind="vine",
        interaction_id="hazard_contact",
        message_key="msg.hazard_grave_lace",
        applies_statuses=("poisoned",),
        single_use=False,
    ),
    "ribbon_frond_tangle": FloraSpec(
        species_id="ribbon_frond",
        name_id="flora.ribbon_frond.name",
        color_kind="frond",
        interaction_id="hazard_slowing_fronds",
        message_key="msg.hazard_ribbon_frond",
        applies_statuses=("slowed",),
        single_use=False,
    ),
    "sleep_bell_moss_edge": FloraSpec(
        species_id="sleep_bell_moss",
        name_id="flora.sleep_bell_moss.name",
        color_kind="moss",
        interaction_id="hazard_drowsy_moss",
        message_key="msg.hazard_sleep_moss",
        applies_statuses=("drowsy",),
        single_use=False,
    ),
    "needle_halo_bush": FloraSpec(
        species_id="needle_halo_bush",
        name_id="flora.needle_halo_bush.name",
        color_kind="needle",
        interaction_id="hazard_needles",
        message_key="msg.hazard_needle_bush",
        health_delta=-4,
        single_use=False,
    ),
    "wet_lowland_parasite_patch": FloraSpec(
        species_id="wet_lowland_parasite_patch",
        name_id="flora.parasite_patch.name",
        color_kind="parasite",
        interaction_id="hazard_parasites",
        message_key="msg.hazard_parasites",
        applies_statuses=("marked",),
        health_delta=-2,
        single_use=False,
    ),
    "night_edge_vine": FloraSpec(
        species_id="night_edge_vine",
        name_id="flora.night_edge_vine.name",
        color_kind="vine",
        interaction_id="hazard_night_edge",
        message_key="msg.hazard_night_edge",
        applies_statuses=("marked",),
        single_use=False,
    ),
}

INTERACTION_SPECS: dict[str, FloraSpec] = {
    "blue_mercy_gourd": FloraSpec(
        species_id="blue_mercy_gourd",
        name_id="flora.blue_mercy_gourd.name",
        color_kind="gourd",
        interaction_id="cleanse_poison",
        message_key="msg.poison_removed",
        discovery_key="disc.blue_mercy_gourd",
        clears_statuses=("poisoned", "marked"),
        health_delta=4,
    ),
    "ash_milk_fern": FloraSpec(
        species_id="ash_milk_fern",
        name_id="flora.ash_milk_fern.name",
        color_kind="fern",
        interaction_id="seal_small_wounds",
        message_key="msg.used_ash_milk_fern",
        discovery_key="disc.ash_milk_fern",
        health_delta=8,
    ),
    "halo_tear_succulent": FloraSpec(
        species_id="halo_tear_succulent",
        name_id="flora.halo_tear_succulent.name",
        color_kind="succulent",
        interaction_id="clean_bio_slime",
        message_key="msg.used_halo_tear",
        discovery_key="disc.halo_tear_succulent",
        clears_statuses=("marked",),
    ),
    "pulsefruit_column": FloraSpec(
        species_id="pulsefruit_column",
        name_id="flora.pulsefruit_column.name",
        color_kind="pulsefruit",
        interaction_id="drink_electrolytes",
        message_key="msg.used_pulsefruit",
        discovery_key="disc.pulsefruit_column",
        clears_statuses=("drowsy",),
        health_delta=6,
    ),
    "blood_lantern_fig": FloraSpec(
        species_id="blood_lantern_fig",
        name_id="flora.blood_lantern_fig.name",
        color_kind="fig",
        interaction_id="eat_high_energy_fig",
        message_key="msg.used_blood_lantern_fig",
        discovery_key="disc.blood_lantern_fig",
        applies_statuses=("marked",),
        health_delta=12,
    ),
    "funnel_grazer_cleaning_sign": FloraSpec(
        species_id="funnel_tongue_grazer",
        name_id="fauna.funnel_tongue_grazer.name",
        color_kind="fauna",
        interaction_id="read_cleaning_sign",
        message_key="msg.read_funnel_grazer_sign",
        discovery_key="disc.funnel_tongue_grazer",
        clears_statuses=("marked",),
        single_use=False,
    ),
}

OBSERVATION_SPECS: dict[str, FloraSpec] = {
    "mossback_grazer_herd": FloraSpec("mossback_grazer", "fauna.mossback_grazer.name", "fauna", "observe_fauna", "msg.observe_mossback_grazer", "disc.mossback_grazer", single_use=False),
    "lantern_mite_swarm": FloraSpec("lantern_mite", "fauna.lantern_mite.name", "mite", "observe_fauna", "msg.observe_lantern_mite", "disc.lantern_mite", applies_statuses=("marked",), single_use=False),
    "needle_skipper_pocket": FloraSpec("needle_skipper", "fauna.needle_skipper.name", "fauna", "observe_fauna", "msg.observe_needle_skipper", "disc.needle_skipper", health_delta=-2, single_use=False),
    "drift_tortoise_shelter": FloraSpec("drift_tortoise", "fauna.drift_tortoise.name", "shelter", "observe_fauna", "msg.observe_drift_tortoise", "disc.drift_tortoise", single_use=False),
    "rain_choir_frog_pool": FloraSpec("rain_choir_frog", "fauna.rain_choir_frog.name", "frog", "observe_fauna", "msg.observe_rain_frog", "disc.rain_choir_frog", single_use=False),
    "rain_choir_frog_exit_pool": FloraSpec("rain_choir_frog", "fauna.rain_choir_frog.name", "frog", "observe_fauna", "msg.observe_rain_frog", "disc.rain_choir_frog", single_use=False),
    "funnel_tongue_grazer_route": FloraSpec("funnel_tongue_grazer", "fauna.funnel_tongue_grazer.name", "fauna", "observe_fauna", "msg.observe_funnel_grazer", "disc.funnel_tongue_grazer", clears_statuses=("marked",), single_use=False),
    "velvet_snapjaw_hint": FloraSpec("velvet_snapjaw", "fauna.velvet_snapjaw.name", "predator", "observe_fauna", "msg.observe_velvet_snapjaw", "disc.velvet_snapjaw", single_use=False),
    "capsule_wake_point": FloraSpec("capsule_wake_point", "poi.capsule_wake_point.name", "poi", "inspect_poi", "msg.poi_capsule", "disc.capsule_wake_point", single_use=False),
    "first_herd_reading_scene": FloraSpec("first_herd_reading_scene", "poi.first_herd_reading_scene.name", "poi", "inspect_poi", "msg.poi_herd", "disc.first_herd_reading_scene", single_use=False),
    "frond_visibility_gate": FloraSpec("frond_visibility_gate", "poi.frond_visibility_gate.name", "poi", "inspect_poi", "msg.poi_fronds", "disc.frond_visibility_gate", single_use=False),
    "wet_lobe_false_safety": FloraSpec("wet_lobe_false_safety", "poi.wet_lobe_false_safety.name", "poi", "inspect_poi", "msg.poi_wet_lobe", "disc.wet_lobe_false_safety", single_use=False),
    "ridge_first_overlook": FloraSpec("ridge_first_overlook", "poi.ridge_first_overlook.name", "poi", "inspect_poi", "msg.poi_ridge", "disc.ridge_first_overlook", single_use=False),
    "tortoise_rain_shelter_scene": FloraSpec("tortoise_rain_shelter_scene", "poi.tortoise_rain_shelter_scene.name", "poi", "inspect_poi", "msg.poi_tortoise", "disc.tortoise_rain_shelter_scene", single_use=False),
    "night_demasking_field": FloraSpec("night_demasking_field", "poi.night_demasking_field.name", "poi", "inspect_poi", "msg.poi_night_field", "disc.night_demasking_field", single_use=False),
    "lowland_transition_warning": FloraSpec("lowland_transition_warning", "poi.lowland_transition_warning.name", "poi", "inspect_poi", "msg.poi_lowland_warning", "disc.lowland_transition_warning", single_use=False),
}


def _match_spec(name: str, specs: dict[str, FloraSpec], fallback: FloraSpec) -> FloraSpec:
    """Execute match spec.
    
    Args:
        name: Input value used by this operation.
        specs: Input value used by this operation.
        fallback: Input value used by this operation.
    
    Returns:
        Result produced by this operation.
    """
    for prefix, spec in specs.items():
        if name.startswith(prefix):
            return spec
    return fallback


def _create_entity(entity_id: str, x: float, y: float, width: int, height: int, spec: FloraSpec, entity_kind: str) -> FloraEntity:
    """Create create entity.
    
    Args:
        entity_id: Input value used by this operation.
        x: Input value used by this operation.
        y: Input value used by this operation.
        width: Input value used by this operation.
        height: Input value used by this operation.
        spec: Input value used by this operation.
        entity_kind: Input value used by this operation.
    
    Returns:
        Result produced by this operation.
    """
    entity = FloraEntity(entity_id=entity_id, name_id=spec.name_id, x=x, y=y, species_id=spec.species_id)
    entity.components["biota"]["entity_kind"] = entity_kind
    entity.add_component("sprite", SpriteComponent(width=width, height=height))
    entity.add_component("visual", {"kind": spec.color_kind})
    return entity


def create_hazard_entity(entity_id: str, x: float, y: float, width: int, height: int) -> FloraEntity:
    """Create a contact hazard entity from its map object name."""
    fallback = HAZARD_SPECS["grave_lace_vine"]
    spec = _match_spec(entity_id, HAZARD_SPECS, fallback)
    entity = _create_entity(entity_id, x, y, width, height, spec, "flora")
    entity.add_component(
        "hazard",
        {
            "statuses_on_touch": list(spec.applies_statuses),
            "health_delta": spec.health_delta,
            "message_key": spec.message_key,
        },
    )
    return entity


def create_interactable_entity(entity_id: str, x: float, y: float, width: int, height: int) -> FloraEntity:
    """Create an interactable flora entity from its map object name."""
    fallback = INTERACTION_SPECS["blue_mercy_gourd"]
    spec = _match_spec(entity_id, INTERACTION_SPECS, fallback)
    entity = _create_entity(entity_id, x, y, width, height, spec, "flora")
    entity.add_component(
        "interaction",
        InteractionComponent(
            interaction_id=spec.interaction_id,
            prompt_key="hint.interact",
            message_key=spec.message_key,
            discovery_key=spec.discovery_key,
            clears_statuses=list(spec.clears_statuses),
            applies_statuses=list(spec.applies_statuses),
            health_delta=spec.health_delta,
            single_use=spec.single_use,
        ),
    )
    entity.add_component("consumable", {"single_use": spec.single_use, "used": False})
    return entity


def create_observation_entity(entity_id: str, x: float, y: float, width: int, height: int) -> FloraEntity:
    """Create an observation marker entity from a map object name."""
    fallback = FloraSpec("unknown_observation", "poi.unknown.name", "poi", "inspect", "msg.poi_unknown", single_use=False)
    spec = _match_spec(entity_id, OBSERVATION_SPECS, fallback)
    entity = _create_entity(entity_id, x, y, width, height, spec, "observation")
    entity.add_component(
        "interaction",
        InteractionComponent(
            interaction_id=spec.interaction_id,
            prompt_key="hint.inspect",
            message_key=spec.message_key,
            discovery_key=spec.discovery_key,
            clears_statuses=list(spec.clears_statuses),
            applies_statuses=list(spec.applies_statuses),
            health_delta=spec.health_delta,
            single_use=spec.single_use,
        ),
    )
    entity.add_component("consumable", {"single_use": spec.single_use, "used": False})
    return entity


# Backward-compatible constructors used by older tests and docs.
def create_grave_lace_vine(entity_id: str, x: float, y: float, width: int, height: int) -> FloraEntity:
    """Create a Grave Lace Vine hazard entity."""
    return create_hazard_entity(entity_id, x, y, width, height)


def create_blue_mercy_gourd(entity_id: str, x: float, y: float, width: int, height: int) -> FloraEntity:
    """Create a Blue Mercy Gourd interactable entity."""
    return create_interactable_entity(entity_id, x, y, width, height)
