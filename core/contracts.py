"""
core/contracts.py
==================
العقد الموحّد لأي Engine أو Skill في المشروع (بند 3، 40، 60).
لا تُعتبر أي وحدة "Skill حقيقية" إلا إذا التزمت بهذا العقد وتم تسجيلها في
core/registry.py وربطها بالـ Orchestrator.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from core.context import PipelineContext


@dataclass
class StepResult:
    ok: bool
    output: Any = None
    warnings: List[str] = field(default_factory=list)
    error: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)


class Engine(ABC):
    """
    محرك = مسؤول عن مرحلة كاملة في الـ Pipeline (فهم، بحث، معرفة، استراتيجية...).
    """
    name: str = "base_engine"
    stage: str = "unknown"  # اسم المرحلة في الـ Pipeline

    requires_llm: bool = True

    @abstractmethod
    def run(self, ctx: PipelineContext, provider) -> StepResult:
        """ينفذ المرحلة، يقرأ ما يحتاجه من ctx فقط، ويعيد StepResult."""
        ...

    def validate_output(self, result: StepResult) -> bool:
        """تحقق افتراضي بسيط؛ يمكن للـ Engine الفرعي تخصيصه (بند 57 بوابات الجودة)."""
        return result.ok and result.output is not None


class Skill(ABC):
    """
    مهارة = قدرة متخصصة قابلة للاستخدام داخل محرك واحد أو أكثر (بند 4).
    يجب أن تحدد: النوع، مرحلة التنفيذ، القيود، التبعيات (بند 3، 41).
    """
    name: str = "base_skill"
    skill_type: str = "generation"  # generation | planning | analysis | review | rewrite | routing | profile | validation
    execution_stage: str = "post_write"  # planning | writing | post_write | review | edit | final_check
    depends_on: List[str] = []
    conflicts_with: List[str] = []
    requires_llm: bool = True
    deterministic_validation: bool = True

    @abstractmethod
    def run(self, ctx: PipelineContext, provider, **kwargs) -> StepResult:
        ...

    # قيود صارمة يجب على أي Skill إعادة كتابة/أنسنة الالتزام بها (بند 45)
    HARD_CONSTRAINTS_AR = [
        "لا تخترع معلومة غير موجودة في المصدر أو المعرفة",
        "لا تخترع مصدرًا أو اقتباسًا",
        "لا تغيّر الحقيقة أو المعنى الواقعي",
        "لا تكتب فوق دليل مهم",
        "حافظ على الحمض النووي الصوتي (Voice DNA) دون جعله جامدًا",
    ]
