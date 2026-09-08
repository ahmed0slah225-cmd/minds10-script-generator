"""Domain model للمشروع."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Project:
    id: str
    title: str
    description: str = ""
    task_type: str = "build_video"
    status: str = "draft"
    language: str = "ar-EG"
    target_minutes: Optional[int] = None
    target_words: Optional[int] = None
    active_stage: str = "input"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
