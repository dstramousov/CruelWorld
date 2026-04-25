from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.utils.paths import ROOT_DIR, resolve_project_path
from src.utils.serialization import load_json


def test_resolve_project_path_keeps_absolute_path(tmp_path: Path) -> None:
    absolute_path = tmp_path / "file.json"
    assert resolve_project_path(absolute_path) == absolute_path


def test_resolve_project_path_resolves_relative_to_project_root() -> None:
    assert resolve_project_path("config/game.json") == ROOT_DIR / "config" / "game.json"


def test_load_json_reads_utf8_objects(tmp_path: Path) -> None:
    json_path = tmp_path / "sample.json"
    json_path.write_text(json.dumps({"name": "Комунікатор"}, ensure_ascii=False), encoding="utf-8")

    assert load_json(json_path) == {"name": "Комунікатор"}


def test_load_json_raises_for_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_json(tmp_path / "missing.json")
