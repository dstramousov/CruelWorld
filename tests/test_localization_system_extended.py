from __future__ import annotations

from pathlib import Path

from src.systems.localization_system import LocalizationSystem
from src.utils.enums import Language


def test_localization_formats_placeholders() -> None:
    localization = LocalizationSystem(default_language=Language.ENG)

    assert localization.tr("communicator.entries", count=3).endswith("3")


def test_localization_falls_back_to_key_for_missing_values() -> None:
    localization = LocalizationSystem(default_language=Language.ENG)

    assert localization.tr("missing.localization.key") == "missing.localization.key"


def test_localization_get_all_values_includes_loaded_bundles() -> None:
    localization = LocalizationSystem(default_language=Language.ENG)

    values = localization.get_all_values()

    assert "Kingdom Fall" in values
    assert any("Комунікатор" in value for value in values)
    assert any("Коммуникатор" in value for value in values)


def test_load_lng_ignores_comments_empty_lines_and_malformed_lines(tmp_path: Path) -> None:
    lng_path = tmp_path / "test.lng"
    lng_path.write_text(
        "# comment\n\nvalid.key = Valid value\nmalformed line\n spaced.key = spaced value \n",
        encoding="utf-8",
    )

    data = LocalizationSystem._load_lng(lng_path)

    assert data == {"valid.key": "Valid value", "spaced.key": "spaced value"}


def test_localization_set_language_changes_active_bundle() -> None:
    localization = LocalizationSystem(default_language=Language.ENG)

    localization.set_language(Language.RUS)

    assert localization.current_language == Language.RUS
    assert localization.tr("communicator.section.settings.title") == "Настройки"
