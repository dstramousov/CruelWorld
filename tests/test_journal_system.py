from __future__ import annotations

from src.systems.journal_system import JournalSystem


def test_journal_unlock_adds_known_entry_and_selects_it() -> None:
    journal = JournalSystem()

    assert journal.unlock("disc.blue_mercy_gourd") is True

    assert journal.unlocked_count == 1
    assert journal.selected_entry() is not None
    assert journal.selected_entry().entry_id == "disc.blue_mercy_gourd"


def test_journal_unlock_rejects_duplicates_missing_and_empty_ids() -> None:
    journal = JournalSystem()

    assert journal.unlock("") is False
    assert journal.unlock("missing.entry") is False
    assert journal.unlock("disc.blue_mercy_gourd") is True
    assert journal.unlock("disc.blue_mercy_gourd") is False
    assert journal.unlocked_count == 1


def test_journal_selection_wraps_and_clamps() -> None:
    journal = JournalSystem()
    journal.unlock("disc.blue_mercy_gourd")
    journal.unlock("disc.ash_milk_fern")

    journal.select_next()
    assert journal.selected_entry().entry_id == "disc.blue_mercy_gourd"

    journal.select_previous()
    assert journal.selected_entry().entry_id == "disc.ash_milk_fern"

    journal.select_index(-100)
    assert journal.selected_entry().entry_id == "disc.blue_mercy_gourd"

    journal.select_index(100)
    assert journal.selected_entry().entry_id == "disc.ash_milk_fern"


def test_empty_journal_selection_is_safe() -> None:
    journal = JournalSystem()

    journal.select_next()
    journal.select_previous()
    journal.select_index(10)

    assert journal.selected_entry() is None
    assert journal.selected_index == 0
    assert journal.list_unlocked() == []
