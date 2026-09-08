"""Domain model للمراجعات."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


@dataclass
class ReviewResult:
    id: str
    project_id: str
    review_type: str
    score: Optional[float]
    verdict: str
    result_json: str
    created_at: Optional[datetime] = None
