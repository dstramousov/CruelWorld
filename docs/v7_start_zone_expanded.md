# v7_start_zone_expanded

Стартовая карта `assets/maps/vertical_slice_01.tmx` расширена из 80x23 тайлов до 360x36 тайлов. Это примерно 7.0x по площади относительно прежней тестовой карты.

## География

Карта теперь разбита на семь читаемых участков: место пробуждения, пастбищная поляна, лентовые заросли, влажная ложбина, каменная гряда, ночная охотничья кромка и выход к будущим низинам.

## Функциональные объекты текущего движка

- `hazards`: 14 опасных зон. Текущий код всё ещё создаёт их как `Grave Lace Vine`, но имена и свойства уже размечают роли других растений/патчей.
- `interactables`: 18 ресурсных точек. Текущий код всё ещё создаёт их как `Blue Mercy Gourd`, но карта уже размечает разные ресурсные роли.
- `camera_zones`: 7 регионов камеры под разные части маршрута.
- `triggers`: выход перенесён в дальний правый край карты.

## Дизайн-маркеры для следующего шага

Добавлены неиспользуемые пока движком слои: `fauna_markers`, `resource_nodes`, `points_of_interest`, `weather_reaction_zones`. Они нужны, чтобы P1/P4 дальше могли превратить размеченные места в реальные сущности, события и погодные реакции без повторного проектирования карты.

## Route readability pass

Added a route readability pass over `vertical_slice_01.tmx`.

Changes:

- Added a clear main safe route from the capsule wake point to the lowlands exit.
- Added an optional upper ridge route for overview, resources, and safer scouting.
- Added a lower wet bypass route with more risk and resource pressure.
- Added a clearer final approach to the exit transition.
- Added `route_guides` object layer with route metadata:
  - `route_main` — main readable route;
  - `route_branch` — optional upper branch;
  - `route_risk` — dangerous lowland bypass;
  - `route_return` — branch return to the main route;
  - `route_exit` — exit guidance.
- Added subtle route guide rendering in `Game` so routes are visible in the current placeholder art style.

Notes:

- Existing user utilities `a`, `c`, `g` are preserved.
- The map size remains `360x36` tiles.
- The pass is focused on readability and traversal, not on adding new gameplay systems.
