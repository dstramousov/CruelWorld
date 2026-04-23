from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Entity:
    entity_id: str
    name_id: str
    components: dict[str, Any] = field(default_factory=dict)

    def add_component(self, name: str, component: Any) -> None:
        self.components[name] = component

    def get(self, name: str) -> Any:
        return self.components[name]
