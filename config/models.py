"""نماذج تشغيلية بسيطة للـconfiguration والـAI tasks."""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class GenerationOptions:
    model: Optional[str] = None
    temperature: float = 0.8
    max_output_tokens: int = 12000
    response_mime_type: Optional[str] = None
    response_schema: Any = None


@dataclass(frozen=True)
class GenerationResult:
    text: str
    model: str
    raw_response: Any = None
    usage: dict[str, Any] = field(default_factory=dict)
