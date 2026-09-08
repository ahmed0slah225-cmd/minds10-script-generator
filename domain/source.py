"""Domain model للمصادر."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Source:
    id: str
    project_id: str
    title: str
    source_type: str
    content: str = ""
    url: Optional[str] = None
    mime_type: Optional[str] = None
    file_name: Optional[str] = None
    page_count: Optional[int] = None
    created_at: Optional[datetime] = None
