"""Communicator UI overlay with journal tabs, menu navigation, and exit confirmation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.ui.text_renderer import text_renderer
from src.utils import colors
from src.utils import rl as raylib


@dataclass(frozen=True)
class Rect:
    """Simple UI rectangle in internal render coordinates."""

    x: int
    y: int
    width: int
    height: int

    def contains(self, point_x: int, point_y: int) -> bool:
        """Return whether the point is inside the rectangle."""
        return self.x <= point_x <= self.x + self.width and self.y <= point_y <= self.y + self.height


class CommunicatorUi:
    """Draws the in-game communicator overlay and handles menu clicks."""

    SETTINGS_ITEMS: tuple[str, ...] = ("language", "font_size", "controls")
    NEW_GAME_ITEMS: tuple[str, ...] = ("hero_name", "scenario", "start", "back")

    MENU_ITEMS: tuple[tuple[str, str], ...] = (
        ("journal", "communicator.menu.communicator"),
        ("new_game", "communicator.menu.new_game"),
        ("save", "communicator.menu.save"),
        ("load", "communicator.menu.load"),
        ("settings", "communicator.menu.settings"),
        ("exit", "communicator.menu.exit"),
    )

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Execute init.
        
        Args:
            config: Input value used by this operation.
        """
        config = config or {}
        self.font_size_options = self._build_font_size_options(config.get("font_size_options"), int(config.get("font_size", 8)))
        self.font_size = int(config.get("font_size", self.font_size_options[0]))
        self.line_height = int(config.get("line_height", max(11, self.font_size + 3)))
        self.is_open = False
        self.active_menu = "journal"
        self.exit_confirmation_visible = False
        self._menu_rects: dict[str, Rect] = {}
        self._journal_entry_rects: list[tuple[int, Rect]] = []
        self._dialog_yes_rect: Rect | None = None
        self._dialog_no_rect: Rect | None = None
        self.settings_selected_index = 0
        self._settings_rects: list[tuple[int, Rect]] = []
        self.new_game_selected_index = 0
        self.new_game_hero_name = str(config.get("default_hero_name", "Survivor"))
        self.new_game_max_name_length = int(config.get("max_hero_name_length", 18))
        self._new_game_rects: list[tuple[int, Rect]] = []

    def toggle(self) -> None:
        # Opening the communicator always returns to the main journal tab, so
        # previous placeholder screens do not trap the player.
        """Execute toggle.
        """
        self.is_open = not self.is_open
        if self.is_open:
            self.active_menu = "journal"
            self.exit_confirmation_visible = False
            return
        self.exit_confirmation_visible = False

    def close(self) -> None:
        """Execute close.
        """
        self.is_open = False
        self.exit_confirmation_visible = False

    def select_next_menu(self) -> None:
        """Select the next top-menu tab without opening modal dialogs."""
        self._select_menu_by_offset(1)

    def select_previous_menu(self) -> None:
        """Select the previous top-menu tab without opening modal dialogs."""
        self._select_menu_by_offset(-1)

    def _select_menu_by_offset(self, offset: int) -> None:
        """Move active top-menu selection by offset with wraparound."""
        if not self.is_open or self.exit_confirmation_visible:
            return
        menu_ids = [menu_id for menu_id, _ in self.MENU_ITEMS]
        try:
            current_index = menu_ids.index(self.active_menu)
        except ValueError:
            current_index = 0
        self.active_menu = menu_ids[(current_index + offset) % len(menu_ids)]
        self.exit_confirmation_visible = False

    def activate_current_menu(self) -> str | None:
        """Activate the currently selected communicator menu item.

        Returns:
            UI action identifier, or None if the action is handled locally.
        """
        if not self.is_open:
            return None
        if self.exit_confirmation_visible:
            return "quit"
        if self.active_menu == "exit":
            self.exit_confirmation_visible = True
            return None
        if self.active_menu == "new_game":
            return self.activate_current_new_game_item()
        if self.active_menu == "settings":
            return self.activate_current_setting()
        return None

    def activate_current_new_game_item(self) -> str | None:
        """Activate the selected new-game row.

        Returns:
            UI action identifier, or None if the row is handled locally.
        """
        item_id = self.NEW_GAME_ITEMS[self.new_game_selected_index]
        if item_id == "start":
            return "new_game:start"
        if item_id == "back":
            self.active_menu = "journal"
            return None
        return None

    def select_next_new_game_item(self) -> None:
        """Select the next new-game row."""
        if self.active_menu != "new_game" or self.exit_confirmation_visible:
            return
        self.new_game_selected_index = (self.new_game_selected_index + 1) % len(self.NEW_GAME_ITEMS)

    def select_previous_new_game_item(self) -> None:
        """Select the previous new-game row."""
        if self.active_menu != "new_game" or self.exit_confirmation_visible:
            return
        self.new_game_selected_index = (self.new_game_selected_index - 1) % len(self.NEW_GAME_ITEMS)

    def handle_new_game_text_input(self, text: str) -> bool:
        """Append printable text to the hero name when the name row is selected.

        Args:
            text: Text entered by the player.

        Returns:
            True when the input changed the hero name.
        """
        if self.active_menu != "new_game" or self.new_game_selected_index != 0:
            return False
        changed = False
        for character in text:
            if not character.isprintable() or character in "\r\n\t":
                continue
            if len(self.new_game_hero_name) >= self.new_game_max_name_length:
                break
            self.new_game_hero_name += character
            changed = True
        return changed

    def handle_new_game_backspace(self) -> bool:
        """Remove one character from the hero name when editing is active.

        Returns:
            True when the hero name changed.
        """
        if self.active_menu != "new_game" or self.new_game_selected_index != 0:
            return False
        if not self.new_game_hero_name:
            return False
        self.new_game_hero_name = self.new_game_hero_name[:-1]
        return True

    def get_new_game_hero_name(self, fallback: str = "Survivor") -> str:
        """Return sanitized hero name for starting a new run.

        Args:
            fallback: Name used when the input field is empty.

        Returns:
            Sanitized hero name.
        """
        name = self.new_game_hero_name.strip()
        return name or fallback

    def format_new_game_hero_name(self, fallback: str = "Survivor") -> str:
        """Return hero-name text with edit cursor and length counter.

        Args:
            fallback: Name displayed when the edit buffer is empty.

        Returns:
            Player-visible hero-name value for the new-game screen.
        """
        display_name = self.new_game_hero_name or fallback
        if self.active_menu == "new_game" and self.new_game_selected_index == 0:
            display_name = f"{display_name}|"
        return f"{display_name} ({len(self.new_game_hero_name)}/{self.new_game_max_name_length})"

    def format_settings_value(self, setting_id: str, value: str, localization: Any) -> str:
        """Format settings value text for active and read-only rows.

        Args:
            setting_id: Internal settings row identifier.
            value: Current value text.
            localization: Localization system used for translated text.

        Returns:
            Player-visible settings value text.
        """
        if setting_id in {"language", "font_size"}:
            return f"< {value} >"
        return localization.tr("settings.readonly", value=value)

    def activate_current_setting(self) -> str | None:
        """Activate the selected settings row.

        Returns:
            UI action identifier, or None if the selected setting is read-only.
        """
        setting_id = self.SETTINGS_ITEMS[self.settings_selected_index]
        if setting_id == "language":
            return "settings:language"
        if setting_id == "font_size":
            return "settings:font_size"
        return None

    def select_next_setting(self) -> None:
        """Select the next settings row."""
        if self.active_menu != "settings" or self.exit_confirmation_visible:
            return
        self.settings_selected_index = (self.settings_selected_index + 1) % len(self.SETTINGS_ITEMS)

    def select_previous_setting(self) -> None:
        """Select the previous settings row."""
        if self.active_menu != "settings" or self.exit_confirmation_visible:
            return
        self.settings_selected_index = (self.settings_selected_index - 1) % len(self.SETTINGS_ITEMS)

    def cancel_current_dialog(self) -> None:
        """Cancel the active communicator dialog, if one is visible."""
        if not self.is_open or not self.exit_confirmation_visible:
            return
        self.exit_confirmation_visible = False
        self.active_menu = "journal"

    def handle_click(self, mouse_x: int, mouse_y: int, journal_system: Any) -> str | None:
        """Handle a mouse click inside the communicator.

        Args:
            mouse_x: Mouse X in internal render coordinates.
            mouse_y: Mouse Y in internal render coordinates.
            journal_system: Journal system used for selecting entries.

        Returns:
            UI action identifier, or None if no external action is requested.
        """
        if not self.is_open:
            return None

        if self.exit_confirmation_visible:
            if self._dialog_yes_rect and self._dialog_yes_rect.contains(mouse_x, mouse_y):
                return "quit"
            if self._dialog_no_rect and self._dialog_no_rect.contains(mouse_x, mouse_y):
                self.exit_confirmation_visible = False
                self.active_menu = "journal"
                return None
            return None

        for menu_id, rect in self._menu_rects.items():
            if not rect.contains(mouse_x, mouse_y):
                continue
            self.active_menu = menu_id
            self.exit_confirmation_visible = menu_id == "exit"
            return None

        if self.active_menu == "journal":
            for entry_index, rect in self._journal_entry_rects:
                if rect.contains(mouse_x, mouse_y):
                    journal_system.select_index(entry_index)
                    return None

        if self.active_menu == "new_game":
            for item_index, rect in self._new_game_rects:
                if rect.contains(mouse_x, mouse_y):
                    self.new_game_selected_index = item_index
                    return self.activate_current_new_game_item()

        if self.active_menu == "settings":
            for setting_index, rect in self._settings_rects:
                if rect.contains(mouse_x, mouse_y):
                    self.settings_selected_index = setting_index
                    return self.activate_current_setting()

        return None

    def draw(self, journal_system: Any, localization: Any, internal_width: int, internal_height: int) -> None:
        """Draw the communicator panel."""
        if not self.is_open:
            return

        # Layout is rebuilt every frame because localization, font size, and
        # available entries can all change at runtime. Cached rectangles are
        # used for mouse hit testing after the draw pass.
        self._reset_layout_cache()
        margin = 18
        font_size = self.font_size
        panel_width = internal_width - margin * 2
        panel_height = internal_height - margin * 2
        raylib.draw_rectangle(margin, margin, panel_width, panel_height, colors.COMMUNICATOR_BG)
        raylib.draw_rectangle(margin + 4, margin + 4, panel_width - 8, 18, colors.COMMUNICATOR_HEADER)

        title = localization.tr("communicator.title")
        counter = localization.tr("communicator.entries", count=journal_system.unlocked_count)
        text_renderer.draw(title, margin + 12, margin + 9, font_size, colors.TEXT)
        text_renderer.draw(counter, margin + 390, margin + 9, font_size, colors.ACCENT)

        self._draw_menu_bar(localization, margin, panel_width, font_size)

        if self.active_menu == "journal":
            self._draw_journal(journal_system, localization, margin, panel_width, panel_height, font_size)
        elif self.active_menu == "new_game":
            self._draw_new_game(localization, margin, panel_width, panel_height, font_size)
        elif self.active_menu == "settings":
            self._draw_settings(localization, margin, panel_width, panel_height, font_size)
        else:
            self._draw_menu_content(localization, margin, panel_width, panel_height, font_size)

        if self.exit_confirmation_visible:
            self._draw_exit_confirmation(localization, internal_width, internal_height, font_size)

    def _reset_layout_cache(self) -> None:
        """Execute reset layout cache.
        """
        self._menu_rects = {}
        self._journal_entry_rects = []
        self._dialog_yes_rect = None
        self._dialog_no_rect = None
        self._settings_rects = []
        self._new_game_rects = []

    def _draw_menu_bar(self, localization: Any, margin: int, panel_width: int, font_size: int) -> None:
        # Top-level communicator tabs. Widths are measured from the active font
        # so Ukrainian/English labels and font-size changes remain clickable.
        """Draw draw menu bar.
        
        Args:
            localization: Input value used by this operation.
            margin: Input value used by this operation.
            panel_width: Input value used by this operation.
            font_size: Input value used by this operation.
        """
        menu_y = margin + 26
        raylib.draw_rectangle(margin + 4, menu_y - 2, panel_width - 8, 18, colors.COMMUNICATOR_MENU_BG)
        x = margin + 12
        for menu_id, label_key in self.MENU_ITEMS:
            label = localization.tr(label_key)
            width = text_renderer.measure_width(label, font_size) + 14
            rect = Rect(x - 4, menu_y - 1, width, 15)
            self._menu_rects[menu_id] = rect
            if self.active_menu == menu_id:
                raylib.draw_rectangle(rect.x, rect.y, rect.width, rect.height, colors.COMMUNICATOR_ACTIVE_TAB)
                color = colors.TEXT
            else:
                color = colors.TEXT_MUTED
            text_renderer.draw(label, x, menu_y + 3, font_size, color)
            x += width + 6

    def _draw_journal(
        self,
        journal_system: Any,
        localization: Any,
        margin: int,
        panel_width: int,
        panel_height: int,
        font_size: int,
    ) -> None:
        # Journal layout: left list uses wrapped titles, right panel uses
        # pixel-width wrapping for descriptions and field advice.
        """Draw draw journal.
        
        Args:
            journal_system: Input value used by this operation.
            localization: Input value used by this operation.
            margin: Input value used by this operation.
            panel_width: Input value used by this operation.
            panel_height: Input value used by this operation.
            font_size: Input value used by this operation.
        """
        line_height = self.line_height
        entries = journal_system.list_unlocked()
        selected = journal_system.selected_entry()
        list_x = margin + 12
        list_y = margin + 58
        detail_x = margin + 244
        detail_y = margin + 58
        list_width = detail_x - list_x - 28
        detail_width = panel_width - (detail_x - margin) - 24

        if not entries:
            text_renderer.draw(localization.tr("communicator.empty"), list_x, list_y, font_size, colors.WARNING)
            text_renderer.draw(localization.tr("communicator.help"), list_x, list_y + 18, font_size, colors.TEXT)
            return

        y = list_y
        max_list_bottom = margin + panel_height - 28
        for index, entry in enumerate(entries):
            label = localization.tr(entry.title_key)
            prefix = ">" if entry == selected else " "
            wrapped_label = self._wrap_to_pixel_width(label, list_width - 18, font_size)
            row_height = max(line_height, len(wrapped_label) * line_height) + 4
            if y + row_height > max_list_bottom:
                break

            rect = Rect(list_x - 4, y - 2, list_width + 10, row_height)
            self._journal_entry_rects.append((index, rect))
            color = colors.ACCENT if entry == selected else colors.TEXT
            if entry == selected:
                raylib.draw_rectangle(rect.x, rect.y, rect.width, rect.height, colors.COMMUNICATOR_ROW_SELECTED)

            for line_index, line in enumerate(wrapped_label):
                line_prefix = prefix if line_index == 0 else " "
                text_renderer.draw(f"{line_prefix} {line}", list_x, y + line_index * line_height, font_size, color)

            y += row_height

        if selected is None:
            return

        detail_title = localization.tr(selected.title_key)
        category = localization.tr(selected.category_key)
        threat = localization.tr(selected.threat_key)
        body = localization.tr(selected.body_key)
        advice = localization.tr(selected.advice_key)

        text_renderer.draw(detail_title, detail_x, detail_y, font_size, colors.ACCENT)
        text_renderer.draw(
            localization.tr("communicator.meta", category=category, threat=threat),
            detail_x,
            detail_y + 16,
            font_size,
            colors.WARNING,
        )

        y = detail_y + 38
        for line in self._wrap_to_pixel_width(body, detail_width, font_size):
            text_renderer.draw(line, detail_x, y, font_size, colors.TEXT)
            y += line_height

        y += 8
        text_renderer.draw(localization.tr("communicator.advice"), detail_x, y, font_size, colors.ACCENT)
        y += 13
        for line in self._wrap_to_pixel_width(advice, detail_width, font_size):
            text_renderer.draw(line, detail_x, y, font_size, colors.TEXT)
            y += line_height

        text_renderer.draw(
            localization.tr("communicator.controls"),
            margin + 12,
            margin + panel_height - 18,
            font_size,
            colors.TEXT,
        )

    def cycle_font_size(self) -> int:
        """Cycle communicator font size through configured options.

        Returns:
            Newly selected font size.
        """
        try:
            current_index = self.font_size_options.index(self.font_size)
        except ValueError:
            current_index = 0
        self.font_size = self.font_size_options[(current_index + 1) % len(self.font_size_options)]
        self.line_height = max(11, self.font_size + 3)
        return self.font_size

    def _draw_new_game(
        self,
        localization: Any,
        margin: int,
        panel_width: int,
        panel_height: int,
        font_size: int,
    ) -> None:
        """Draw the new-game creation screen.

        Args:
            localization: Localization system used for translated text.
            margin: Outer panel margin.
            panel_width: Communicator panel width.
            panel_height: Communicator panel height.
            font_size: Current UI font size.
        """
        content_x = margin + 24
        content_y = margin + 62
        row_width = panel_width - 48
        row_height = max(20, self.line_height + 8)
        title = localization.tr("communicator.section.new_game.title")
        body = localization.tr("communicator.section.new_game.body")
        text_renderer.draw(title, content_x, content_y, font_size, colors.ACCENT)

        y = content_y + 20
        for line in self._wrap_to_pixel_width(body, row_width, font_size):
            text_renderer.draw(line, content_x, y, font_size, colors.TEXT)
            y += self.line_height

        y += 10
        rows = [
            ("new_game.hero_name", self.format_new_game_hero_name(localization.tr("new_game.default_name"))),
            ("new_game.scenario", localization.tr("new_game.scenario.crash_wake")),
            ("new_game.start", localization.tr("new_game.start.value")),
            ("new_game.back", localization.tr("new_game.back.value")),
        ]
        for index, (label_key, value) in enumerate(rows):
            rect = Rect(content_x - 4, y - 4, row_width, row_height)
            self._new_game_rects.append((index, rect))
            if index == self.new_game_selected_index:
                raylib.draw_rectangle(rect.x, rect.y, rect.width, rect.height, colors.COMMUNICATOR_ROW_SELECTED)
                marker = ">"
                label_color = colors.ACCENT
            else:
                marker = " "
                label_color = colors.TEXT
            label = localization.tr(label_key)
            text_renderer.draw(f"{marker} {label}", content_x, y, font_size, label_color)
            if value:
                value_x = content_x + 230
                value_color = colors.ACCENT if index == self.new_game_selected_index else colors.WARNING
                text_renderer.draw(value, value_x, y, font_size, value_color)
            y += row_height + 3

        edit_hint_y = y + 4
        if self.new_game_selected_index == 0:
            text_renderer.draw(localization.tr("new_game.name_edit_hint"), content_x, edit_hint_y, font_size, colors.TEXT_MUTED)

        hint_y = margin + panel_height - 30
        text_renderer.draw(localization.tr("new_game.hint"), margin + 12, hint_y, font_size, colors.TEXT)
        text_renderer.draw(localization.tr("communicator.menu.controls"), margin + 12, hint_y + 12, font_size, colors.TEXT_MUTED)

    def _draw_settings(
        self,
        localization: Any,
        margin: int,
        panel_width: int,
        panel_height: int,
        font_size: int,
    ) -> None:
        """Draw the communicator settings screen.

        Args:
            localization: Localization system used for translated text.
            margin: Outer panel margin.
            panel_width: Communicator panel width.
            panel_height: Communicator panel height.
            font_size: Current UI font size.
        """
        content_x = margin + 24
        content_y = margin + 62
        row_width = panel_width - 48
        row_height = max(20, self.line_height + 8)
        title = localization.tr("communicator.section.settings.title")
        body = localization.tr("communicator.section.settings.body")
        text_renderer.draw(title, content_x, content_y, font_size, colors.ACCENT)

        y = content_y + 20
        for line in self._wrap_to_pixel_width(body, row_width, font_size):
            text_renderer.draw(line, content_x, y, font_size, colors.TEXT)
            y += self.line_height

        y += 10
        language_key = f"language.{localization.current_language.value}"
        rows = [
            ("language", "settings.language", localization.tr(language_key)),
            ("font_size", "settings.text_size", str(self.font_size)),
            ("controls", "settings.controls", localization.tr("settings.controls.value")),
        ]
        for index, (setting_id, label_key, value) in enumerate(rows):
            rect = Rect(content_x - 4, y - 4, row_width, row_height)
            self._settings_rects.append((index, rect))
            if index == self.settings_selected_index:
                raylib.draw_rectangle(rect.x, rect.y, rect.width, rect.height, colors.COMMUNICATOR_ROW_SELECTED)
                marker = ">"
                label_color = colors.ACCENT
            else:
                marker = " "
                label_color = colors.TEXT
            label = localization.tr(label_key)
            text_renderer.draw(f"{marker} {label}", content_x, y, font_size, label_color)
            value_x = content_x + 230
            value_text = self.format_settings_value(setting_id, value, localization)
            value_color = colors.ACCENT if index == self.settings_selected_index else colors.WARNING
            text_renderer.draw(value_text, value_x, y, font_size, value_color)
            if index == self.settings_selected_index and setting_id in {"language", "font_size"}:
                action_hint = localization.tr("settings.change_hint")
                text_renderer.draw(action_hint, value_x, y + self.line_height, font_size, colors.TEXT_MUTED)
            y += row_height + 6

        hint_y = margin + panel_height - 30
        text_renderer.draw(localization.tr("settings.hint"), margin + 12, hint_y, font_size, colors.TEXT)
        text_renderer.draw(localization.tr("communicator.menu.controls"), margin + 12, hint_y + 12, font_size, colors.TEXT_MUTED)

    def _draw_menu_content(
        self,
        localization: Any,
        margin: int,
        panel_width: int,
        panel_height: int,
        font_size: int,
    ) -> None:
        """Draw draw menu content.
        
        Args:
            localization: Input value used by this operation.
            margin: Input value used by this operation.
            panel_width: Input value used by this operation.
            panel_height: Input value used by this operation.
            font_size: Input value used by this operation.
        """
        content_x = margin + 24
        content_y = margin + 62
        content_width = panel_width - 48
        title_key = f"communicator.section.{self.active_menu}.title"
        body_key = f"communicator.section.{self.active_menu}.body"
        text_renderer.draw(localization.tr(title_key), content_x, content_y, font_size, colors.ACCENT)
        y = content_y + 22
        for line in self._wrap_to_pixel_width(localization.tr(body_key), content_width, font_size):
            text_renderer.draw(line, content_x, y, font_size, colors.TEXT)
            y += self.line_height
        text_renderer.draw(
            localization.tr("communicator.menu.controls"),
            margin + 12,
            margin + panel_height - 18,
            font_size,
            colors.TEXT,
        )

    def _draw_exit_confirmation(self, localization: Any, internal_width: int, internal_height: int, font_size: int) -> None:
        # Modal confirmation blocks the rest of the communicator until the
        # player confirms or cancels the exit request.
        """Draw draw exit confirmation.
        
        Args:
            localization: Input value used by this operation.
            internal_width: Input value used by this operation.
            internal_height: Input value used by this operation.
            font_size: Input value used by this operation.
        """
        overlay_color = (0, 0, 0, 160)
        dialog_width = 310
        dialog_height = 105
        dialog_x = (internal_width - dialog_width) // 2
        dialog_y = (internal_height - dialog_height) // 2
        raylib.draw_rectangle(0, 0, internal_width, internal_height, overlay_color)
        raylib.draw_rectangle(dialog_x, dialog_y, dialog_width, dialog_height, colors.COMMUNICATOR_DIALOG_BG)
        raylib.draw_rectangle(dialog_x + 4, dialog_y + 4, dialog_width - 8, 18, colors.COMMUNICATOR_HEADER)
        text_renderer.draw(localization.tr("communicator.exit.confirm.title"), dialog_x + 14, dialog_y + 9, font_size, colors.WARNING)
        text_renderer.draw(localization.tr("communicator.exit.confirm.body"), dialog_x + 14, dialog_y + 38, font_size, colors.TEXT)

        self._dialog_yes_rect = Rect(dialog_x + 70, dialog_y + 70, 62, 20)
        self._dialog_no_rect = Rect(dialog_x + 178, dialog_y + 70, 62, 20)
        raylib.draw_rectangle(
            self._dialog_yes_rect.x,
            self._dialog_yes_rect.y,
            self._dialog_yes_rect.width,
            self._dialog_yes_rect.height,
            colors.COMMUNICATOR_DANGER_BUTTON,
        )
        raylib.draw_rectangle(
            self._dialog_no_rect.x,
            self._dialog_no_rect.y,
            self._dialog_no_rect.width,
            self._dialog_no_rect.height,
            colors.COMMUNICATOR_ACTIVE_TAB,
        )
        text_renderer.draw(localization.tr("communicator.exit.yes"), self._dialog_yes_rect.x + 18, self._dialog_yes_rect.y + 7, font_size, colors.TEXT)
        text_renderer.draw(localization.tr("communicator.exit.no"), self._dialog_no_rect.x + 20, self._dialog_no_rect.y + 7, font_size, colors.TEXT)

    @staticmethod
    def _build_font_size_options(raw_options: Any, fallback: int) -> list[int]:
        """Build sanitized communicator font-size options.

        Args:
            raw_options: Raw config value with possible font sizes.
            fallback: Font size used when config is missing or invalid.

        Returns:
            Sorted unique positive font sizes.
        """
        if not isinstance(raw_options, list):
            return [fallback]
        values = sorted({int(value) for value in raw_options if isinstance(value, (int, float)) and int(value) > 0})
        return values or [fallback]

    @staticmethod
    def _wrap_to_pixel_width(text: str, max_width: int, font_size: int) -> list[str]:
        """Wrap text by rendered pixel width."""
        if max_width <= 0:
            return [text]

        wrapped_lines: list[str] = []
        for paragraph in text.splitlines() or [text]:
            words = paragraph.split()
            if not words:
                wrapped_lines.append("")
                continue

            current_line = ""
            for word in words:
                word_parts = CommunicatorUi._split_word_to_pixel_width(word, max_width, font_size)
                for part in word_parts:
                    candidate = part if not current_line else f"{current_line} {part}"
                    if text_renderer.measure_width(candidate, font_size) <= max_width:
                        current_line = candidate
                        continue

                    if current_line:
                        wrapped_lines.append(current_line)
                    current_line = part

            if current_line:
                wrapped_lines.append(current_line)

        return wrapped_lines

    @staticmethod
    def _split_word_to_pixel_width(word: str, max_width: int, font_size: int) -> list[str]:
        """Split a single long word when it exceeds the available pixel width."""
        if text_renderer.measure_width(word, font_size) <= max_width:
            return [word]

        parts: list[str] = []
        current = ""
        for character in word:
            candidate = f"{current}{character}"
            if current and text_renderer.measure_width(candidate, font_size) > max_width:
                parts.append(current)
                current = character
                continue
            current = candidate

        if current:
            parts.append(current)
        return parts
