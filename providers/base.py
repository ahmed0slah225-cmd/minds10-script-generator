"""
providers/base.py
==================
LLMProvider: الواجهة المجردة التي تفصل الـ Engines عن أي API خارجي محدد
(القسم 32/65). أي Engine يستدعي دائمًا:

    provider = get_provider(model_id)
    result = provider.generate(prompt=..., system=..., structured_schema=...)

ولا يعرف أبدًا أنه Gemini أو OpenAI أو غيره.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class GenerationRequest:
    prompt: str
    system: Optional[str] = None
    model_id: str = ""
    temperature: float = 0.7
    max_output_tokens: Optional[int] = None
    structured_schema: Optional[dict[str, Any]] = None   # JSON schema إن كان الإخراج منظمًا
    enable_search: bool = False
    documents: list[dict[str, Any]] = field(default_factory=list)  # PDFs/صور مرفقة إن وُجدت


@dataclass
class GenerationResult:
    text: str
    model_id: str
    tokens_in: int = 0
    tokens_out: int = 0
    structured_output: Optional[dict[str, Any]] = None
    search_sources: list[dict[str, Any]] = field(default_factory=list)
    raw: Any = None


class LLMProvider(ABC):
    """كل موفر (Gemini/OpenAI/...) يطبّق هذه الواجهة فقط."""

    provider_name: str = "base"

    @abstractmethod
    def generate(self, request: GenerationRequest) -> GenerationResult:
        ...

    @abstractmethod
    def supports(self, capability: str) -> bool:
        """يسأل الموفر مباشرة، كطبقة تحقق إضافية فوق model_registry."""
        ...


_PROVIDERS: dict[str, LLMProvider] = {}


def register_provider(name: str, provider: LLMProvider) -> None:
    _PROVIDERS[name] = provider


def get_provider(provider_name: str) -> LLMProvider:
    if provider_name not in _PROVIDERS:
        raise KeyError(
            f"موفر LLM غير مسجّل: {provider_name}. "
            f"المسجّلون حاليًا: {list(_PROVIDERS.keys())}"
        )
    return _PROVIDERS[provider_name]
