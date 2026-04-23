from __future__ import annotations

from src.components.collider import ColliderComponent
from src.components.gravity import GravityComponent
from src.components.health import HealthComponent
from src.components.light_emitter import LightEmitterComponent
from src.components.sprite import SpriteComponent
from src.components.state import StateComponent
from src.components.statuses import StatusReceiverComponent
from src.components.transform import TransformComponent
from src.components.velocity import VelocityComponent
from src.entities.entity import Entity


class Player(Entity):
    def __init__(self) -> None:
        super().__init__(entity_id="player", name_id="entity.player")
        self.add_component("transform", TransformComponent(x=96.0, y=240.0))
        self.add_component("sprite", SpriteComponent(width=14, height=24))
        self.add_component("collider", ColliderComponent(width=14.0, height=24.0))
        self.add_component("velocity", VelocityComponent())
        self.add_component("gravity", GravityComponent(value=900.0))
        self.add_component("state", StateComponent())
        self.add_component("health", HealthComponent())
        self.add_component("statuses", StatusReceiverComponent())
        self.add_component("light", LightEmitterComponent(enabled=True, radius=72.0))
