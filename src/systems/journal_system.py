"""Journal discovery and navigation system for communicator entries."""

from __future__ import annotations

from dataclasses import dataclass

from src.systems.log_system import get_logger
from src.utils.paths import CONTENT_DIR
from src.utils.serialization import load_json

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class JournalEntry:
    """Localized journal entry descriptor."""

    entry_id: str
    title_key: str
    category_key: str
    threat_key: str
    body_key: str
    advice_key: str


class JournalSystem:
    """Stores discovered biota and point-of-interest notes."""

    def __init__(self, content_path: str = "journal_entries.json") -> None:
        # Journal content is data-driven: objects unlock keys, and keys map to
        # localized field entries from content/journal_entries.json.
        """Execute init.
        
        Args:
            content_path: Input value used by this operation.
        """
        self._entries = self._load_entries(content_path)
        self._unlocked: list[str] = []
        self.selected_index = 0

    @property
    def unlocked_count(self) -> int:
        """Execute unlocked count.
        
        Returns:
            Result produced by this operation.
        """
        return len(self._unlocked)

    def unlock(self, entry_id: str) -> bool:
        """Execute unlock.
        
        Args:
            entry_id: Input value used by this operation.
        
        Returns:
            Result produced by this operation.
        """
        if not entry_id:
            return False
        if entry_id not in self._entries:
            logger.log_event("JOURNAL_ENTRY_MISSING", level=30, entry_id=entry_id)
            return False
        if entry_id in self._unlocked:
            return False
        self._unlocked.append(entry_id)
        self.selected_index = len(self._unlocked) - 1
        logger.log_event("JOURNAL_ENTRY_UNLOCKED", level=20, entry_id=entry_id)
        return True

    def select_next(self) -> None:
        """Execute select next.
        """
        if not self._unlocked:
            self.selected_index = 0
            return
        self.selected_index = (self.selected_index + 1) % len(self._unlocked)

    def select_previous(self) -> None:
        """Execute select previous.
        """
        if not self._unlocked:
            self.selected_index = 0
            return
        self.selected_index = (self.selected_index - 1) % len(self._unlocked)

    def select_index(self, index: int) -> None:
        """Select an unlocked journal entry by index."""
        if not self._unlocked:
            self.selected_index = 0
            return
        self.selected_index = max(0, min(index, len(self._unlocked) - 1))

    def list_unlocked(self) -> list[JournalEntry]:
        """Execute list unlocked.
        
        Returns:
            Result produced by this operation.
        """
        return [self._entries[entry_id] for entry_id in self._unlocked]

    def selected_entry(self) -> JournalEntry | None:
        """Execute selected entry.
        
        Returns:
            Result produced by this operation.
        """
        if not self._unlocked:
            return None
        safe_index = max(0, min(self.selected_index, len(self._unlocked) - 1))
        return self._entries[self._unlocked[safe_index]]

    @staticmethod
    def _load_entries(content_path: str) -> dict[str, JournalEntry]:
        """Execute load entries.
        
        Args:
            content_path: Input value used by this operation.
        
        Returns:
            Result produced by this operation.
        """
        raw_entries = load_json(CONTENT_DIR / content_path)
        entries: dict[str, JournalEntry] = {}
        for entry_id, data in raw_entries.items():
            entries[entry_id] = JournalEntry(
                entry_id=entry_id,
                title_key=str(data["title_key"]),
                category_key=str(data["category_key"]),
                threat_key=str(data["threat_key"]),
                body_key=str(data["body_key"]),
                advice_key=str(data["advice_key"]),
            )
        logger.log_event("JOURNAL_ENTRIES_LOADED", level=20, entries=len(entries))
        return entries
