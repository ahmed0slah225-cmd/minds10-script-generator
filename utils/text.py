"""وظائف نصية صغيرة لا تعتمد على الـUI."""

from __future__ import annotations

import re


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text or ""))


def clean_text(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", (text or "").strip())
