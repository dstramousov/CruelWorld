# v7_code_comments_pass

Добавлены короткие инженерные комментарии к главным блокам кода без изменения игровой логики.

Покрытые области:

- `main.py` — точка входа приложения.
- `src/core/app.py` — запуск, окно, главный цикл, рендер во внутренний буфер, shutdown.
- `src/core/game.py` — сборка runtime-систем, update, draw, ввод, интеракции, hazards, загрузка объектов карты.
- `src/ui/communicator.py` — верхнее меню, journal layout, hitbox cache, dialog flow.
- `src/systems/input_system.py` — конфигурируемые бинды и chord parsing.
- `src/systems/interaction_system.py` — поиск ближайшего интерактива и применение результата.
- `src/systems/journal_system.py` — data-driven журнал наблюдений.
- `src/systems/debug_metrics.py` — runtime metrics и будущая логика чанков.
- `src/ui/text_renderer.py` — загрузка шрифта, fallback и codepoints для локализации.
- `src/world/tiled_loader.py` — загрузка TMX tile/object layers.
- `src/core/asset_manager.py` — освобождение ассетов.
- `src/core/project_validation.py` — предварительная проверка проекта.

Важно:

- Логика не менялась.
- Комментарии внутри кода написаны на английском по текущему code style.
- Утилиты `a`, `c`, `g` сохранены.
