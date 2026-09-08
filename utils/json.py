"""JSON helpers."""

from __future__ import annotations

import json
from typing import Any


def dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def loads(text: str) -> Any:
    return json.loads(text)
