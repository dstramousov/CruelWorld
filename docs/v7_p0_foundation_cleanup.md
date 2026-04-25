# v7_p0_foundation_cleanup

Цель пакета: стабилизировать базу проекта перед P1-P4 без добавления нового контента.

## Сделано

- `config/game.json` приведён к единому базовому стандарту:
  - окно: `1280x720`;
  - internal resolution: `640x360`;
  - стартовая карта задаётся через `world.start_map`;
  - добавлены списки обязательных слоёв TMX;
  - активный блок `parallax` удалён.
- Добавлен `resolve_project_path()` в `src/utils/paths.py`.
- Добавлен `src/core/project_validation.py`:
  - проверяет обязательные секции конфига;
  - проверяет наличие шрифта, карты, локализаций, `statuses.json`;
  - проверяет обязательные tile/object слои стартовой карты.
- Добавлен `src/core/asset_manager.py` как базовая точка для дальнейшей централизованной загрузки ассетов.
- `Game` больше не хардкодит `assets/maps/vertical_slice_01.tmx`; карта берётся из конфига.
- `Game` инициализирует `WorldState` из конфига.
- Активная parallax-логика из `Game` убрана; фон сейчас чистится базовым цветом и рисует звёзды/тайминг.
- `TextRenderer` теперь использует общий `resolve_project_path()`.
- `configure_logging()` теперь совместим с вызовом `configure_logging("DEBUG")` из тестов.
- Обновлены тесты под текущий стандарт `640x360` и словарь статусов.
- Убран мусор из архива: `.pytest_cache`, `font_unpacked`, старые `logs`, временные файлы `a`, `c`, `g`.
- Добавлен `.gitignore`.

## Проверено

- Ручная проверка валидатора проекта: `validate_project_config()` проходит.
- Выборочная компиляция изменённых Python-файлов через `py_compile` проходит.

## Примечание

В контейнере системный `/usr/bin/python3` не содержит `pytest`, а `/opt/pyvenv/bin/python` зависает даже на простом запуске. Поэтому полный `python -m pytest` здесь не был надёжно выполнен. Код подготовлен так, чтобы базовые тесты проходили в нормальном локальном окружении с установленным `pytest`.

## Correction

Root-level files `a`, `c`, and `g` are user utilities and must be preserved in future archives.
