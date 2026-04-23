from src.systems.localization_system import LocalizationSystem
from src.utils.enums import Language


def test_localization_loads_default_bundle() -> None:
    localization = LocalizationSystem(default_language=Language.ENG)
    assert localization.tr("app.title") == "Kingdom Fall"
