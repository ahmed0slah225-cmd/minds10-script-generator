"""Domain model لـVoice DNA."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class VoiceProfile:
    id: str
    name: str
    description: str = ""
    profile_json: str = "{}"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
