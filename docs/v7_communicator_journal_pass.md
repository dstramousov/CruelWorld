# v7_communicator_journal_pass

## Сделано

- Добавлен конфиг управления в `config/game.json`.
- Все текущие игровые кнопки теперь читаются через `InputSystem`, а не захардкожены в `Game`.
- Добавлен `JournalSystem` для записей коммуникатора.
- Добавлен `content/journal_entries.json` с первыми 20 записями.
- Добавлен UI коммуникатора: `src/ui/communicator.py`.
- Коммуникатор открывается через `Tab` или `J`.
- В коммуникаторе можно листать записи через `Up/Down` или `W/S`.
- Закрытие: `Esc`, `Tab` или `J`.
- Взаимодействия с флорой, фауной и POI теперь открывают записи журнала.
- При открытом коммуникаторе игровой мир ставится на паузу на уровне `Game.update`.
- `a`, `c`, `g` сохранены как пользовательские утилиты.

## Конфиг кнопок

Новый раздел:

```json
"controls": {
  "move_left": ["A", "LEFT"],
  "move_right": ["D", "RIGHT"],
  "jump": ["SPACE", "W", "UP"],
  "interact": ["F"],
  "communicator_toggle": ["TAB", "J"],
  "communicator_close": ["ESCAPE", "TAB", "J"],
  "communicator_next": ["DOWN", "S"],
  "communicator_previous": ["UP", "W"],
  "toggle_language": ["F1"],
  "toggle_debug": ["LEFT_SHIFT+D", "RIGHT_SHIFT+D"],
  "zoom_out": ["Q"],
  "zoom_in": ["E"]
}
```

Поддерживаются простые клавиши и комбинации вида `LEFT_SHIFT+D`.

## Проверка

- JSON-конфиги парсятся.
- `validate_project_config()` проходит.
- Изменённые Python-файлы проходят `py_compile`.
- Архив проверен через `unzip -t`.

## Hotfix: journal text wrapping

- Added automatic communicator text wrapping by measured pixel width.
- Wrapping now follows the active font and font size instead of a fixed character count.
- This prevents long journal lines from leaving the right panel when the font size changes.

## Left journal list wrapping fix

- Journal titles in the left panel now wrap by rendered pixel width.
- Wrapping uses the active font metrics, so it adapts when the UI font size changes.
- Long single words are split safely if they exceed the available column width.
