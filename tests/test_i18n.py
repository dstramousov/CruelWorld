from src.systems.localization_system import LocalizationSystem
from src.utils.enums import Language


def test_localization_loads_default_bundle() -> None:
    localization = LocalizationSystem(default_language=Language.ENG)
    assert localization.tr("app.title") == "Kingdom Fall"


def test_localization_loads_russian_bundle() -> None:
    localization = LocalizationSystem(default_language=Language.RUS)

    assert localization.tr("app.title") == "Царство падальщиков"
    assert localization.tr("communicator.menu.save") == "Сохранить"


def test_localization_cycles_all_supported_languages() -> None:
    localization = LocalizationSystem(default_language=Language.ENG)

    assert localization.current_language == Language.ENG
    localization.toggle_language()
    assert localization.current_language == Language.UKR
    localization.toggle_language()
    assert localization.current_language == Language.RUS
    localization.toggle_language()
    assert localization.current_language == Language.ENG
