"""Entity module for entity definitions and factories for gameplay objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Entity:
    """Represent the Entity runtime concept."""
    entity_id: str
    name_id: str
    components: dict[str, Any] = field(default_factory=dict)

    def add_component(self, name: str, component: Any) -> None:
        """Execute add component.
        
        Args:
            name: Input value used by this operation.
            component: Input value used by this operation.
        """
        self.components[name] = component

    def get(self, name: str) -> Any:
        """Execute get.
        
        Args:
            name: Input value used by this operation.
        
        Returns:
            Result produced by this operation.
        """
        return self.components[name]
