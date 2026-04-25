# v7_communicator_ui_config_pass

## Изменения

- Настройки размера текста коммуникатора вынесены в `config/game.json`.
- `CommunicatorUi` больше не использует захардкоженный `font_size = 8`.
- Межстрочный интервал журнала и placeholder-экранов коммуникатора берётся из конфига.

## Где менять

```json
"ui": {
  "communicator": {
    "font_size": 8,
    "line_height": 11
  }
}
```

Файл шрифта по-прежнему задаётся в секции:

```json
"font": {
  "path": "assets/fonts/PressStart2P-Regular.ttf",
  "base_size": 8,
  "spacing": 1.0
}
```

## Важно

- `font.path` отвечает за файл шрифта.
- `font.base_size` отвечает за загрузку glyph/codepoints.
- `ui.communicator.font_size` отвечает за фактический размер текста в коммуникаторе.
- `ui.communicator.line_height` отвечает за вертикальный шаг строк в списках и описаниях.
