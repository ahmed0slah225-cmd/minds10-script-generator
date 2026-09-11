"""
engine/models.py
==================
هنا التمثيل المركزي لحالة المشروع (Project Context) اللي بيتحرك بين كل
الـEngines. ده التطبيق الفعلي لمبدأ "Context Flow" اللي اتشرح في مواصفة
المشروع: كل مرحلة تضيف بياناتها هنا، والمرحلة اللي بعدها تقرأ منها.

نفس الـclass ده هو اللي بيتحوّل لـJSON ويتخزن في project_versions في
قاعدة البيانات، عشان المشروع يبقى قابل للاستكمال (Resumable).
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional


def new_id(prefix: str = "") -> str:
    suffix = uuid.uuid4().hex[:12]
    return f"{prefix}_{suffix}" if prefix else suffix


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class SourceItem:
    """أي مادة خام دخلت المشروع: عنوان / فكرة / نص / PDF / رابط."""

    id: str
    kind: str  # "title" | "idea" | "question" | "text" | "pdf" | "url"
    title: str = ""
    raw_text: str = ""          # للنصوص المباشرة
    file_path: str = ""         # للـPDF
    url: str = ""               # للروابط
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    added_at: str = field(default_factory=now_iso)


@dataclass
class KnowledgeItem:
    """
    عنصر معرفة واحد داخل الـKnowledge Base.
    confidence بيوضح هل المعلومة موثقة من مصدر فعلي، ولا محتاجة بحث،
    ولا لسه غير مؤكدة — عشان نمنع اختراع معلومات في أي مرحلة لاحقة.
    """

    id: str
    content: str
    kind: str  # "idea" | "evidence" | "story" | "number" | "quote" | "relation"
    source_ids: list[str] = field(default_factory=list)
    confidence: str = "unconfirmed"  # "confirmed" | "unconfirmed" | "needs_research"


@dataclass
class VoiceDNAProfile:
    """البصمة الأسلوبية للكاتب — نفس الحقول المتفق عليها في مواصفة voice_dna."""

    writer_id: str = "default"
    traits: dict = field(default_factory=dict)
    notes: str = ""

    def to_prompt_fragment(self) -> str:
        if not self.traits:
            return ""
        lines = [f"بصمة الكاتب الصوتية (Voice DNA) الخاصة بـ {self.writer_id}:"]
        for key, value in self.traits.items():
            if value:
                lines.append(f"- {key}: {value}")
        if self.notes:
            lines.append(f"ملاحظات: {self.notes}")
        lines.append(
            "استخدم هذه السمات كأسلوب عام موجّه فقط. لا تنسخ جملة حرفية من عيّنات "
            "سابقة، ولا تقلّد كاتبًا آخر."
        )
        return "\n".join(lines)


@dataclass
class ReviewFinding:
    """نتيجة موحّدة من أي مرحلة مراجعة (Anti-Slop / Retention / Repetition)."""

    review_type: str  # "anti_slop" | "retention" | "repetition" | "final_human"
    score: Optional[float] = None
    issues: list[dict] = field(default_factory=list)
    raw: dict = field(default_factory=dict)


@dataclass
class ProjectContext:
    """
    الحالة الكاملة لمشروع واحد. هي دي اللي بتتخزن وتتحمّل من قاعدة
    البيانات عشان المشروع يكون Resumable.
    """

    project_id: str = field(default_factory=lambda: new_id("proj"))
    title: str = ""
    audience: str = ""
    duration_minutes: int = 10
    writer_id: str = "default"

    sources: list[SourceItem] = field(default_factory=list)

    topic_understanding: dict = field(default_factory=dict)
    core_ideas: list[str] = field(default_factory=list)

    research_notes: list[dict] = field(default_factory=list)
    knowledge_base: list[KnowledgeItem] = field(default_factory=list)

    audience_pain_point: str = ""

    strategy: dict = field(default_factory=dict)  # angle, promise, central_question, order
    outline: list[str] = field(default_factory=list)
    retention_plan: dict = field(default_factory=dict)

    hook_text: str = ""
    draft_script: str = ""
    humanized_script: str = ""

    reviews: dict = field(default_factory=dict)  # review_type -> ReviewFinding (as dict)
    egyptian_final_script: str = ""

    voice_dna: VoiceDNAProfile = field(default_factory=VoiceDNAProfile)
    voice_dna_consistency: dict = field(default_factory=dict)

    final_script: str = ""

    current_stage: str = "input_intelligence"
    created_at: str = field(default_factory=now_iso)
    updated_at: str = field(default_factory=now_iso)

    # -- تحويل من/إلى JSON للتخزين في project_versions ------------------
    def to_json(self) -> str:
        data = asdict(self)
        return json.dumps(data, ensure_ascii=False)

    @staticmethod
    def from_json(raw: str) -> "ProjectContext":
        data = json.loads(raw)
        data["sources"] = [SourceItem(**s) for s in data.get("sources", [])]
        data["knowledge_base"] = [KnowledgeItem(**k) for k in data.get("knowledge_base", [])]
        if data.get("voice_dna"):
            data["voice_dna"] = VoiceDNAProfile(**data["voice_dna"])
        return ProjectContext(**data)

    def touch(self, stage: str | None = None) -> None:
        self.updated_at = now_iso()
        if stage:
            self.current_stage = stage

    def confirmed_facts(self) -> list[str]:
        """
        كل الـSkills والـEngines اللي محتاجة تعرف "إيه اللي نعرفه فعلًا"
        بتستخدم الدالة دي بدل ما تتعامل مع الـKnowledge Base الخام —
        عشان نمنع استخدام معلومة غير موثقة كأنها حقيقة.
        """
        return [k.content for k in self.knowledge_base if k.confidence == "confirmed"]
