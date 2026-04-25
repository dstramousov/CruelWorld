# v7_api_docs_pass

Added Sphinx API documentation scaffolding and module/class/function docstrings across the source tree.

## How to build

```bash
python -m pip install -r requirements-dev.txt
python -m sphinx -b html docs_api/source docs_api/build/html
```

Open:

```text
docs_api/build/html/index.html
```

## Notes

- API documentation is generated from Python docstrings and type hints.
- Inline comments are kept for code-reading context, but Sphinx does not treat them as API docs.
- `raylib` and `pyray` are mocked during documentation builds so docs can be generated on machines without native graphics bindings.
