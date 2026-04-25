"""Serialization module for shared utility functions and wrappers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    """Load json.
    
    Args:
        path: Input value used by this operation.
    
    Returns:
        Result produced by this operation.
    """
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)
