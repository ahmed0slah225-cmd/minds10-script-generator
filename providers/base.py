"""
providers/base.py
==================
واجهة موحّدة لأي مزوّد LLM (بند 32/65). الـ Engines لا تتعامل مع Gemini API
مباشرة أبدًا؛ تتعامل فقط مع LLMProvider.generate(...).
هذا يسمح مستقبلاً بإضافة OpenAI / Anthropic / نماذج محلية بدون تعديل أي Engine.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class LLMSource:
    """مصدر معلومة عائد من البحث المؤرض (grounding)، لتتبع مصدر المصدر (بند 25)."""
    title: str
    url: str
    snippet: str = ""


@dataclass
class LLMResponse:
    text: str
    model_id: str
    provider: str
    input_tokens: int = 0
    output_tokens: int = 0
    used_web_search: bool = False
    sources: List[LLMSource] = field(default_factory=list)
    raw: Optional[Any] = None
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None


@dataclass
class LLMRequest:
    system_prompt: str
    user_prompt: str
    model_id: str
    enable_web_search: bool = False           # قرار المستخدم فقط (بند 21/22)
    thinking_level: str = "medium"
    temperature: Optional[float] = None
    max_output_tokens: Optional[int] = None
    pdf_bytes: Optional[bytes] = None          # لإرفاق PDF مباشرة عند الحاجة
    response_schema: Optional[Dict[str, Any]] = None  # لطلب JSON منظم


class LLMProvider(ABC):
    """كل مزوّد (Gemini، مستقبلاً OpenAI ...) يطبّق هذه الواجهة فقط."""

    provider_name: str = "base"

    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        ...

    @abstractmethod
    def supports(self, capability: str) -> bool:
        ...
