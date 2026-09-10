"""
core/context.py
================
هذا الملف يعرّف الكائن الأساسي اللي بيتنقل بين كل الـ Engines والـ Skills:
`ProjectContext`.

الفكرة: أي مرحلة (Engine) أو مهارة (Skill) بتاخد الـ Context كامل، تقرأ منه
اللي محتاجاه، وترجعه بعد ما تضيف نتيجتها في الحقل الخاص بيها فقط.
ده هو تطبيق فكرة "Context Flow" و"Knowledge Base" اللي اتشرحت في تصميم المشروع.

الكائن ده هو أيضًا اللي بيتحفظ في Turso بعد كل مرحلة، عشان المشروع يبقى
قابل للاستكمال (Resumable Project).
"""

from __future__ import annotations

import uuid
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Optional


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class SourceRef:
    """مصدر معرفي: رابط، PDF، أو نص مدخل من المستخدم."""
    kind: str  # "url" | "pdf" | "text" | "book"
    label: str
    content: str = ""          # النص المستخرج (أو ملخص عنه لو طويل جدًا)
    pages: Optional[str] = None  # مثلاً "1-20" لو المصدر PDF بنطاق صفحات
    trusted: bool = True


@dataclass
class VoiceDNAProfile:
    """البصمة الصوتية للكاتب - ناتج skills/voice_dna.py"""
    avg_sentence_length: Optional[float] = None
    rhythm_notes: str = ""
    question_usage: str = ""
    vocabulary_level: str = ""
    slang_level: str = ""      # درجة العامية
    emotion_level: str = ""
    transition_style: str = ""
    example_style: str = ""
    closing_style: str = ""
    raw_notes: str = ""        # ملاحظات نثرية حرة يصعب تكميمها
    sample_count: int = 0

    def as_prompt_guidance(self) -> str:
        """تحويل البصمة لتعليمات نثرية تتحط جوه أي Prompt لأي Engine."""
        if self.sample_count == 0:
            return "لا توجد بصمة صوتية محفوظة بعد لهذا الكاتب - استخدم مصري طبيعي عام."
        return (
            f"بصمة الكاتب الصوتية (Voice DNA):\n"
            f"- متوسط طول الجملة: {self.avg_sentence_length or 'غير محدد'}\n"
            f"- إيقاع الكلام: {self.rhythm_notes}\n"
            f"- استخدام الأسئلة: {self.question_usage}\n"
            f"- مستوى المفردات: {self.vocabulary_level}\n"
            f"- درجة العامية: {self.slang_level}\n"
            f"- درجة العاطفة: {self.emotion_level}\n"
            f"- أسلوب الانتقالات: {self.transition_style}\n"
            f"- أسلوب الأمثلة: {self.example_style}\n"
            f"- أسلوب إنهاء الفكرة: {self.closing_style}\n"
            f"- ملاحظات إضافية: {self.raw_notes}\n"
            "التزم بالسمات دي كإرشاد عام، من غير ما تنسخ أي نص سابق حرفيًا."
        )


@dataclass
class ReviewResult:
    """نتيجة عامة لأي مرحلة مراجعة (Anti-Slop, Retention, Repetition, Final...)."""
    passed: bool = True
    scores: dict = field(default_factory=dict)   # مثلاً {"الطبيعية": 8, ...}
    issues: list = field(default_factory=list)   # كل عنصر: {"location":..,"problem":..,"suggestion":..}
    summary: str = ""


@dataclass
class ProjectContext:
    # هوية المشروع
    project_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    # INPUT
    raw_input_type: str = ""     # title | idea | question | text | book_pdf | mixed
    raw_input_text: str = ""
    sources: list[SourceRef] = field(default_factory=list)

    # إعدادات الفيديو
    audience_description: str = ""
    duration_minutes: int = 10
    allow_web_search: bool = False

    # نواتج المراحل (Intelligence Layer)
    topic_understanding: dict = field(default_factory=dict)
    research_findings: dict = field(default_factory=dict)
    knowledge_base: dict = field(default_factory=dict)
    audience_insight: dict = field(default_factory=dict)
    strategy: dict = field(default_factory=dict)
    story_architecture: dict = field(default_factory=dict)
    retention_plan: dict = field(default_factory=dict)
    hook_options: dict = field(default_factory=dict)

    # الكتابة
    script_draft: str = ""
    humanized_script: str = ""
    egyptian_edited_script: str = ""
    final_script: str = ""

    # المراجعات (Skills)
    anti_slop_report: dict = field(default_factory=dict)
    retention_review: dict = field(default_factory=dict)
    repetition_review: dict = field(default_factory=dict)
    voice_dna_consistency_report: dict = field(default_factory=dict)
    final_human_review: dict = field(default_factory=dict)

    # Voice DNA (طبقة مشتركة تُمرَّر لعدة Engines/Skills)
    voice_dna_profile: VoiceDNAProfile = field(default_factory=VoiceDNAProfile)

    # تتبع تنفيذ الـ Workflow (لدعم الاستكمال لاحقًا)
    completed_stages: list[str] = field(default_factory=list)
    current_stage: str = ""
    status: str = "in_progress"  # in_progress | done | failed

    # -------- Helpers --------
    def mark_stage_done(self, stage_name: str) -> None:
        if stage_name not in self.completed_stages:
            self.completed_stages.append(stage_name)
        self.updated_at = _now()

    def to_json(self) -> str:
        d = asdict(self)
        return json.dumps(d, ensure_ascii=False)

    @staticmethod
    def from_json(raw: str) -> "ProjectContext":
        d = json.loads(raw)
        vdna = d.pop("voice_dna_profile", {}) or {}
        sources = d.pop("sources", []) or []
        ctx = ProjectContext(**d)
        ctx.voice_dna_profile = VoiceDNAProfile(**vdna)
        ctx.sources = [SourceRef(**s) for s in sources]
        return ctx
