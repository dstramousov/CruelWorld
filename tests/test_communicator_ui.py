from __future__ import annotations

from dataclasses import dataclass

from src.ui.communicator import CommunicatorUi, Rect


@dataclass
class DummyJournal:
    selected_index: int = 0

    def select_index(self, index: int) -> None:
        self.selected_index = index


def test_rect_contains_edges_and_rejects_outside_points() -> None:
    rect = Rect(10, 20, 30, 40)

    assert rect.contains(10, 20) is True
    assert rect.contains(40, 60) is True
    assert rect.contains(41, 60) is False
    assert rect.contains(40, 61) is False


def test_toggle_opens_journal_tab_and_close_hides_dialog() -> None:
    ui = CommunicatorUi({"font_size": 10, "line_height": 14})
    ui.active_menu = "settings"
    ui.exit_confirmation_visible = True

    ui.toggle()

    assert ui.is_open is True
    assert ui.active_menu == "journal"
    assert ui.exit_confirmation_visible is False
    assert ui.font_size == 10
    assert ui.line_height == 14

    ui.close()

    assert ui.is_open is False
    assert ui.exit_confirmation_visible is False


def test_handle_click_ignores_clicks_when_closed() -> None:
    ui = CommunicatorUi()

    assert ui.handle_click(1, 1, DummyJournal()) is None
    assert ui.active_menu == "journal"


def test_handle_click_selects_menu_and_shows_exit_confirmation() -> None:
    ui = CommunicatorUi()
    ui.is_open = True
    ui._menu_rects = {"settings": Rect(0, 0, 20, 20), "exit": Rect(30, 0, 20, 20)}

    assert ui.handle_click(5, 5, DummyJournal()) is None
    assert ui.active_menu == "settings"
    assert ui.exit_confirmation_visible is False

    assert ui.handle_click(35, 5, DummyJournal()) is None
    assert ui.active_menu == "exit"
    assert ui.exit_confirmation_visible is True


def test_handle_click_exit_dialog_yes_returns_quit_and_no_cancels() -> None:
    ui = CommunicatorUi()
    ui.is_open = True
    ui.exit_confirmation_visible = True
    ui.active_menu = "exit"
    ui._dialog_yes_rect = Rect(0, 0, 20, 20)
    ui._dialog_no_rect = Rect(30, 0, 20, 20)

    assert ui.handle_click(5, 5, DummyJournal()) == "quit"

    ui.exit_confirmation_visible = True
    assert ui.handle_click(35, 5, DummyJournal()) is None
    assert ui.exit_confirmation_visible is False
    assert ui.active_menu == "journal"


def test_handle_click_selects_journal_entry_when_journal_tab_is_active() -> None:
    ui = CommunicatorUi()
    ui.is_open = True
    ui.active_menu = "journal"
    ui._journal_entry_rects = [(2, Rect(10, 10, 50, 20))]
    journal = DummyJournal()

    assert ui.handle_click(20, 20, journal) is None

    assert journal.selected_index == 2


def test_wrap_to_pixel_width_splits_long_words(monkeypatch) -> None:
    monkeypatch.setattr("src.ui.communicator.text_renderer.measure_width", lambda text, size: len(text) * size)

    wrapped = CommunicatorUi._wrap_to_pixel_width("longword tiny", max_width=16, font_size=4)

    assert wrapped == ["long", "word", "tiny"]


def test_menu_keyboard_navigation_wraps_without_opening_exit_dialog() -> None:
    ui = CommunicatorUi()
    ui.is_open = True

    ui.select_next_menu()
    assert ui.active_menu == "new_game"
    assert ui.exit_confirmation_visible is False

    ui.select_previous_menu()
    assert ui.active_menu == "journal"
    assert ui.exit_confirmation_visible is False

    ui.select_previous_menu()
    assert ui.active_menu == "exit"
    assert ui.exit_confirmation_visible is False


def test_menu_keyboard_navigation_is_ignored_while_exit_dialog_is_visible() -> None:
    ui = CommunicatorUi()
    ui.is_open = True
    ui.active_menu = "exit"
    ui.exit_confirmation_visible = True

    ui.select_next_menu()

    assert ui.active_menu == "exit"
    assert ui.exit_confirmation_visible is True


def test_enter_activation_opens_exit_confirmation() -> None:
    ui = CommunicatorUi()
    ui.is_open = True
    ui.active_menu = "exit"

    assert ui.activate_current_menu() is None

    assert ui.exit_confirmation_visible is True
    assert ui.active_menu == "exit"


def test_enter_activation_confirms_visible_exit_dialog() -> None:
    ui = CommunicatorUi()
    ui.is_open = True
    ui.active_menu = "exit"
    ui.exit_confirmation_visible = True

    assert ui.activate_current_menu() == "quit"


def test_cancel_current_dialog_returns_to_journal_tab() -> None:
    ui = CommunicatorUi()
    ui.is_open = True
    ui.active_menu = "exit"
    ui.exit_confirmation_visible = True

    ui.cancel_current_dialog()

    assert ui.exit_confirmation_visible is False
    assert ui.active_menu == "journal"


def test_settings_selection_and_activation() -> None:
    ui = CommunicatorUi({"font_size": 8, "font_size_options": [8, 10, 12]})
    ui.is_open = True
    ui.active_menu = "settings"

    assert ui.activate_current_menu() == "settings:language"

    ui.select_next_setting()
    assert ui.activate_current_menu() == "settings:font_size"

    ui.select_next_setting()
    assert ui.activate_current_menu() is None

    ui.select_previous_setting()
    assert ui.activate_current_menu() == "settings:font_size"


def test_settings_font_size_cycles_through_configured_options() -> None:
    ui = CommunicatorUi({"font_size": 8, "font_size_options": [8, 10, 12]})

    assert ui.cycle_font_size() == 10
    assert ui.line_height == 13
    assert ui.cycle_font_size() == 12
    assert ui.line_height == 15
    assert ui.cycle_font_size() == 8
    assert ui.line_height == 11


def test_settings_click_selects_and_activates_row() -> None:
    ui = CommunicatorUi()
    ui.is_open = True
    ui.active_menu = "settings"
    ui._settings_rects = [(1, Rect(10, 10, 60, 20))]

    assert ui.handle_click(15, 15, DummyJournal()) == "settings:font_size"
    assert ui.settings_selected_index == 1


def test_new_game_selection_text_input_and_backspace() -> None:
    ui = CommunicatorUi({"default_hero_name": "Survivor", "max_hero_name_length": 8})
    ui.is_open = True
    ui.active_menu = "new_game"

    ui.new_game_hero_name = ""
    assert ui.handle_new_game_text_input("Dimas!") is True
    assert ui.new_game_hero_name == "Dimas!"

    assert ui.handle_new_game_backspace() is True
    assert ui.new_game_hero_name == "Dimas"

    assert ui.handle_new_game_text_input("_LongName") is True
    assert ui.new_game_hero_name == "Dimas_Lo"


def test_new_game_activation_start_and_back() -> None:
    ui = CommunicatorUi()
    ui.is_open = True
    ui.active_menu = "new_game"

    ui.new_game_selected_index = 2
    assert ui.activate_current_menu() == "new_game:start"

    ui.new_game_selected_index = 3
    assert ui.activate_current_menu() is None
    assert ui.active_menu == "journal"


def test_new_game_selection_wraps() -> None:
    ui = CommunicatorUi()
    ui.is_open = True
    ui.active_menu = "new_game"

    ui.select_previous_new_game_item()
    assert ui.new_game_selected_index == 3

    ui.select_next_new_game_item()
    assert ui.new_game_selected_index == 0


def test_new_game_empty_name_uses_fallback() -> None:
    ui = CommunicatorUi()
    ui.new_game_hero_name = "   "

    assert ui.get_new_game_hero_name("Fallback") == "Fallback"


def test_new_game_name_display_shows_cursor_and_limit_when_selected() -> None:
    ui = CommunicatorUi({"default_hero_name": "Survivor", "max_hero_name_length": 8})
    ui.is_open = True
    ui.active_menu = "new_game"
    ui.new_game_selected_index = 0
    ui.new_game_hero_name = "Dimas"

    assert ui.format_new_game_hero_name("Fallback") == "Dimas| (5/8)"

    ui.new_game_hero_name = ""
    assert ui.format_new_game_hero_name("Fallback") == "Fallback| (0/8)"


def test_settings_value_format_marks_editable_and_readonly_rows() -> None:
    class LocalizationStub:
        def tr(self, key: str, **kwargs: object) -> str:
            if key == "settings.readonly":
                return str(kwargs["value"])
            return key

    ui = CommunicatorUi()
    localization = LocalizationStub()

    assert ui.format_settings_value("language", "Русский", localization) == "< Русский >"
    assert ui.format_settings_value("font_size", "10", localization) == "< 10 >"
    assert ui.format_settings_value("controls", "config/game.json", localization) == "config/game.json"
