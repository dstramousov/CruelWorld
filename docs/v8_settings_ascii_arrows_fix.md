# v8_settings_ascii_arrows_fix

- Replaced non-ASCII setting value brackets with ASCII `< >`.
- This avoids missing glyph fallback in bitmap fonts where `‹ ›` render as `?`.
- No module structure changes; `docs_api/source/*.rst` was not changed.
