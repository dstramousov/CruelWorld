# v7_tests_pass

Added pytest-style coverage for the main non-rendering systems.

Covered areas:

- project path resolving and JSON loading;
- config validation, including negative validation cases;
- Tiled/TMX map parsing and tile map dimensions;
- configurable input bindings and modifier chords;
- journal unlock, selection, duplicate and missing-entry behavior;
- debug metrics and future chunk-stat calculations;
- status application, refresh, ticking, expiration and removal;
- interaction detection and execution payloads;
- entity factories for hazards, interactables and observation markers;
- base entity/component behavior and player component composition;
- localization parsing, fallback and formatting;
- text-renderer glyph codepoint generation;
- communicator menu click state, exit confirmation and wrapped-text helper logic.

Notes:

- Tests avoid opening a raylib window.
- Render/UI draw calls are not integration-tested yet; only pure state/layout helpers are covered.
- In this container, `/usr/bin/python3` does not have `pytest`, while `/opt/pyvenv/bin/python -m pytest` hangs before test execution. Test files were syntax-checked with `py_compile`.
