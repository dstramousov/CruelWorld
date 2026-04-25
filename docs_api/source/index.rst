Kingdom Fall API Documentation
==============================

Эта документация генерируется из Python module/class/function docstrings и type hints.
Обычные inline-комментарии остаются в исходниках и не являются основным источником API-документации.

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   modules

Сборка
------

Из корня проекта::

   python -m pip install -r requirements-dev.txt
   python -m sphinx -b html docs_api/source docs_api/build/html

Готовый HTML будет доступен в ``docs_api/build/html/index.html``.
