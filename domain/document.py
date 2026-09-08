"""Domain models للمستندات وصفحات PDF."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class DocumentMetadata:
    source_id: str
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    language: Optional[str] = None
    description: Optional[str] = None
    confidence: float = 0.0


@dataclass
class DocumentPage:
    id: str
    source_id: str
    page_number: int
    text: str
    word_count: int = 0
