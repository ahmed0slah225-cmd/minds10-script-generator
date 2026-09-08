"""Domain models للسكريبت والنسخ."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ScriptVersion:
    id: str
    project_id: str
    version_number: int
    stage: str
    content: str
    word_count: int = 0
    created_at: Optional[datetime] = None
    parent_version_id: Optional[str] = None
