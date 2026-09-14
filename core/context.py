"""
core/context.py
================
PipelineContext: الحالة المشتركة لمشروع سكريبت واحد وهو يمر عبر المراحل.

القاعدة 62: لا تمرر كل شيء لكل Skill — كل Skill تأخذ فقط ما تحتاجه عبر
دالة `slice_for(skill_manifest)`، حتى لو كان الكائن الكامل موجودًا هنا.

هذا الكائن هو ما يُحفظ/يُستعاد لكل "مشروع" (القسم 50) — أي تمثيل لقاعدة
بيانات (Turso) يجب أن يُسلسل (serialize) هذا الكائن، وليس session_state.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class ResearchDepth(str, Enum):
    BASIC = "basic"
    STANDARD = "standard"
    DEEP = "deep"


@dataclass
class ResearchConfig:
    """القسم 21-25: البحث اختياري، افتراضيًا OFF، ولا يتغير سرًا."""
    enabled: bool = False
    depth: ResearchDepth = ResearchDepth.STANDARD
    run_id: Optional[str] = None
    timestamp: Optional[str] = None
    sources: list[dict[str, Any]] = field(default_factory=list)  # كل مصدر: url, retrieved_at, trust_level


@dataclass
class ModelSelection:
    """القسم 26-34: اختيار الموديل على مستوى المشروع + Override اختياري لكل Engine."""
    project_default: str = "gemini-3-6-flash"
    engine_overrides: dict[str, str] = field(default_factory=dict)  # engine_name -> model_id
    allow_silent_fallback: bool = False  # يظل False دائمًا إلا لو المستخدم فعّلها صراحة

    def model_for(self, engine_name: str) -> str:
        return self.engine_overrides.get(engine_name, self.project_default)


@dataclass
class SourceRef:
    """مصدر معلومة واحد — القسم 25: مصدر المصدر."""
    origin: str                 # "user_input" | "user_pdf" | "web_research" | "user_provided_link"
    content: str
    retrieved_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    is_primary: bool = False    # القسم 24: مصدر المستخدم الأساسي يبقى مميزًا دائمًا
    trust_level: str = "unverified"  # "verified" | "inferred" | "unverified"
    page_range: Optional[tuple[int, int]] = None


@dataclass
class VoiceDNAProfile:
    """ملف الحمض النووي الصوتي — القسم 9-10. سمات أسلوبية، وليس نسخة من نص قديم."""
    name: str = "default"
    sentence_length_pattern: Optional[str] = None
    rhythm_notes: Optional[str] = None
    vocabulary_level: Optional[str] = None
    slang_intensity: Optional[str] = None
    question_usage: Optional[str] = None
    viewer_address_style: Optional[str] = None
    emotion_style: Optional[str] = None
    explanation_style: Optional[str] = None
    example_style: Optional[str] = None
    storytelling_style: Optional[str] = None
    transition_style: Optional[str] = None
    curiosity_building: Optional[str] = None
    metaphor_style: Optional[str] = None
    idea_closing_style: Optional[str] = None
    formality_level: Optional[str] = None
    spontaneity_level: Optional[str] = None


@dataclass
class PipelineContext:
    """الحاوية الكاملة لحالة مشروع سكريبت واحد."""
    project_id: str
    project_name: str
    raw_input: str = ""

    duration_minutes: Optional[int] = None
    audience: Optional[str] = None
    output_language: str = "egyptian_arabic"

    sources: list[SourceRef] = field(default_factory=list)
    research: ResearchConfig = field(default_factory=ResearchConfig)
    model_selection: ModelSelection = field(default_factory=ModelSelection)
    voice_dna: VoiceDNAProfile = field(default_factory=VoiceDNAProfile)

    # نواتج المراحل المتتالية — تُملأ تباعًا بواسطة الـ Engines
    topic_understanding: dict[str, Any] = field(default_factory=dict)
    knowledge_base: list[dict[str, Any]] = field(default_factory=list)
    strategy: dict[str, Any] = field(default_factory=dict)
    story: dict[str, Any] = field(default_factory=dict)
    outline: dict[str, Any] = field(default_factory=dict)
    hooks: list[dict[str, Any]] = field(default_factory=list)
    draft_script: Optional[str] = None
    humanized_script: Optional[str] = None
    review_notes: list[dict[str, Any]] = field(default_factory=list)
    final_script: Optional[str] = None

    constraints: dict[str, Any] = field(default_factory=dict)  # مثال: قيود المصدر، ممنوعات
    version: int = 1
    run_log: list[dict[str, Any]] = field(default_factory=list)  # القسم 54 و 78: observability

    def slice_for(self, required_keys: tuple[str, ...]) -> dict[str, Any]:
        """يُعيد فقط المفاتيح التي طلبتها الـ Skill عبر manifest.required_inputs،
        بدل تمرير الـ Context كله. مفاتيح غير موجودة تُهمل بصمت (تتحقق منها
        الـ Skill نفسها في validate_input)."""
        full = asdict(self)
        return {k: full[k] for k in required_keys if k in full}

    def log_run(self, *, engine: str, skill: Optional[str], model_id: Optional[str],
                status: str, duration_ms: int = 0, tokens_in: int = 0,
                tokens_out: int = 0, error: Optional[str] = None) -> None:
        """القسم 54/78: سجل قابل للملاحظة لكل استدعاء."""
        self.run_log.append({
            "project_id": self.project_id,
            "engine": engine,
            "skill": skill,
            "model_id": model_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": status,
            "duration_ms": duration_ms,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "error": error,
        })
