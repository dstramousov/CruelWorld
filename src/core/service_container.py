from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ServiceContainer:
    """Simple runtime service registry.

    This lightweight container is intentionally minimal for early project stages.
    It allows systems or utilities to be registered and retrieved by string key.
    """

    _services: dict[str, Any] = field(default_factory=dict)

    def register(self, name: str, service: Any) -> None:
        """Register a service instance under the given name."""
        self._services[name] = service

    def get(self, name: str, default: Any | None = None) -> Any:
        """Return a service by name or default when missing."""
        return self._services.get(name, default)

    def has(self, name: str) -> bool:
        """Check whether a service exists in the container."""
        return name in self._services

    def clear(self) -> None:
        """Remove all registered services."""
        self._services.clear()
