# v8 Russian language pass

Added Russian as the third supported UI language.

## Changes

- Added `i18n/rus.lng`.
- Added `Language.RUS` to `src/utils/enums.py`.
- Updated `LocalizationSystem.toggle_language()` to cycle through all languages declared in the `Language` enum.
- Updated `config/game.json`:

```json
"supported_languages": [
  "eng",
  "ukr",
  "rus"
]
```

- Added `language.rus` labels to English and Ukrainian bundles.
- Added localization tests for Russian loading and language cycling.

## Current language cycle

```text
eng -> ukr -> rus -> eng
```

## Notes

The localization bundle loader now iterates over `Language`, so adding future languages requires adding the enum value and the corresponding `i18n/<code>.lng` file.
