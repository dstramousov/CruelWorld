"""Status System module for runtime gameplay systems."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.components.statuses import StatusInstance, StatusReceiverComponent
from src.systems.log_system import get_logger

logger = get_logger(__name__)


@dataclass(slots=True)
class StatusDefinition:
    """Static data describing a status effect."""

    status_id: str
    name_key: str
    description_key: str
    duration: float
    tick_interval: float
    tick_damage: int
    color: tuple[int, int, int, int]


class StatusSystem:
    """Applies and updates status effects on entities."""

    def __init__(self, definitions: dict[str, StatusDefinition]) -> None:
        """Execute init.
        
        Args:
            definitions: Input value used by this operation.
        """
        self._definitions = definitions
        self._last_event: str = "none"

    @property
    def last_event(self) -> str:
        """Execute last event.
        
        Returns:
            Result produced by this operation.
        """
        return self._last_event

    def apply(self, receiver: StatusReceiverComponent, status_id: str) -> bool:
        """Execute apply.
        
        Args:
            receiver: Input value used by this operation.
            status_id: Input value used by this operation.
        
        Returns:
            Result produced by this operation.
        """
        definition = self._definitions.get(status_id)
        if definition is None:
            logger.log_event("STATUS_UNKNOWN_REQUESTED", level=40, status=status_id)
            return False

        current = receiver.active.get(status_id)
        if current is not None:
            current.remaining = max(current.remaining, definition.duration)
            current.next_tick_in = min(current.next_tick_in, definition.tick_interval)
            self._last_event = f"refreshed:{status_id}"
            logger.log_event(
                "STATUS_REFRESHED",
                level=20,
                status=status_id,
                duration=current.remaining,
                tick_interval=current.tick_interval,
            )
            return True

        receiver.active[status_id] = StatusInstance(
            status_id=status_id,
            remaining=definition.duration,
            tick_interval=definition.tick_interval,
            next_tick_in=definition.tick_interval,
            tick_damage=definition.tick_damage,
        )
        self._last_event = f"applied:{status_id}"
        logger.log_event(
            "STATUS_APPLIED",
            level=20,
            status=status_id,
            duration=definition.duration,
            tick_interval=definition.tick_interval,
            tick_damage=definition.tick_damage,
        )
        return True

    def remove(self, receiver: StatusReceiverComponent, status_id: str) -> bool:
        """Execute remove.
        
        Args:
            receiver: Input value used by this operation.
            status_id: Input value used by this operation.
        
        Returns:
            Result produced by this operation.
        """
        if status_id not in receiver.active:
            return False
        receiver.active.pop(status_id)
        self._last_event = f"removed:{status_id}"
        logger.log_event("STATUS_REMOVED", level=20, status=status_id)
        return True

    def remove_many(self, receiver: StatusReceiverComponent, statuses: list[str]) -> list[str]:
        """Execute remove many.
        
        Args:
            receiver: Input value used by this operation.
            statuses: Input value used by this operation.
        
        Returns:
            Result produced by this operation.
        """
        removed: list[str] = []
        for status_id in statuses:
            if self.remove(receiver, status_id):
                removed.append(status_id)
        return removed

    def update(self, receiver: StatusReceiverComponent, health: Any, delta_time: float) -> None:
        """Update update.
        
        Args:
            receiver: Input value used by this operation.
            health: Input value used by this operation.
            delta_time: Input value used by this operation.
        """
        expired: list[str] = []
        for status in receiver.active.values():
            status.remaining -= delta_time
            status.next_tick_in -= delta_time
            if status.tick_damage > 0 and status.next_tick_in <= 0.0:
                health.current = max(0, health.current - status.tick_damage)
                status.next_tick_in += status.tick_interval
                self._last_event = f"tick:{status.status_id}"
                logger.log_event(
                    "STATUS_TICK",
                    status=status.status_id,
                    damage=status.tick_damage,
                    health=health.current,
                    remaining=round(status.remaining, 3),
                )
            if status.remaining <= 0.0:
                expired.append(status.status_id)

        for status_id in expired:
            receiver.active.pop(status_id, None)
            self._last_event = f"expired:{status_id}"
            logger.log_event("STATUS_EXPIRED", level=20, status=status_id)

    def get_definition(self, status_id: str) -> StatusDefinition | None:
        """Return definition.
        
        Args:
            status_id: Input value used by this operation.
        
        Returns:
            Result produced by this operation.
        """
        return self._definitions.get(status_id)
