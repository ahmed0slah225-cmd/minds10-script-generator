"""
engine/models.py
-----------------
تعريفات البيانات الأساسية للمشروع. دي مش ORM كامل، دي Data Contracts
بسيطة (dataclasses) تتحول لـ dict عشان تتخزن في Turso/SQLite كـ JSON
في أعمدة نصية، وده كافٍ جدًا لحجم المشروع ده وأسرع من بناء ORM ضخم.
"""

from __future__ import annotations
import uuid
import time
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any


def new_id(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:12]}"


def now_ts() -> float:
    return time.time()


@dataclass
class VoiceProfile:
    """تمثيل منظم لبصمة الكاتب (Voice DNA) — انظر skills/voice_dna_ar_eg."""
    id: str = field(default_factory=lambda: new_id("voice_"))
    name: str = "بصمتي الافتراضية"
    avg_sentence_length: str = ""      # قصيرة / متوسطة / طويلة / متنوعة
    pacing: str = ""                    # سريع / هادئ / متغير
    question_usage: str = ""            # يسأل المشاهد كتير / قليل
    vocabulary_notes: str = ""
    slang_level: str = ""               # عامية خفيفة / عامية كثيفة
    emotion_level: str = ""
    explanation_style: str = ""
    example_style: str = ""
    transition_style: str = ""
    curiosity_style: str = ""
    ending_style: str = ""
    metaphor_usage: str = ""
    formality_level: str = ""
    direct_address_style: str = ""      # طريقة مخاطبة المشاهد
    raw_traits_summary: str = ""        # ملخص حر كتبه الـ Voice Engine
    sample_snippets: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=now_ts)


@dataclass
class SourceDoc:
    id: str = field(default_factory=lambda: new_id("src_"))
    project_id: str = ""
    kind: str = "text"           # text | url | pdf
    title: str = ""
    raw_text: str = ""           # للنصوص/المقالات
    url: str = ""
    file_path: str = ""          # مسار الـ PDF لو موجود
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    extracted_text: str = ""     # النص المستخرج من نطاق الصفحات المطلوب
    notes: str = ""
    created_at: float = field(default_factory=now_ts)


@dataclass
class KnowledgeItem:
    id: str = field(default_factory=lambda: new_id("know_"))
    project_id: str = ""
    claim: str = ""
    evidence: str = ""
    source_ref: str = ""         # اسم/معرف المصدر اللي جابت منه المعلومة
    confidence: str = "موثق"      # موثق | غير موثق / يحتاج تحقق
    usable_in_script: bool = True


@dataclass
class ReviewNote:
    engine: str = ""              # اسم الـ Skill/Engine اللي طلعت منه الملاحظة
    dimension: str = ""           # مثلاً: الطبيعية / كثافة المعلومات / الوضوح ...
    score: Optional[int] = None
    issue: str = ""
    location_hint: str = ""       # جملة أو فقرة تقريبية
    suggestion: str = ""


@dataclass
class Project:
    id: str = field(default_factory=lambda: new_id("proj_"))
    title: str = "مشروع بدون اسم"
    original_request: str = ""
    audience: str = ""
    duration_minutes: int = 10
    voice_profile_id: Optional[str] = None

    status: str = "draft"          # draft | in_progress | completed
    current_stage: str = "input_understanding"

    # مخرجات كل مرحلة (تتحدث تباعًا أثناء تنفيذ الـ pipeline)
    topic_understanding: str = ""
    research_notes: str = ""
    knowledge_base: List[Dict[str, Any]] = field(default_factory=list)
    audience_insight: str = ""
    strategy: str = ""
    story_architecture: str = ""
    hook_options: List[str] = field(default_factory=list)
    chosen_hook: str = ""
    draft_script: str = ""
    humanized_script: str = ""
    anti_slop_report: Dict[str, Any] = field(default_factory=dict)
    retention_report: Dict[str, Any] = field(default_factory=dict)
    repetition_report: Dict[str, Any] = field(default_factory=dict)
    egyptian_edited_script: str = ""
    voice_consistency_report: Dict[str, Any] = field(default_factory=dict)
    final_review_notes: List[Dict[str, Any]] = field(default_factory=list)
    final_script: str = ""

    stage_log: List[Dict[str, Any]] = field(default_factory=list)
    created_at: float = field(default_factory=now_ts)
    updated_at: float = field(default_factory=now_ts)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Project":
        return Project(**d)

    def log_stage(self, stage: str, summary: str = ""):
        self.stage_log.append({"stage": stage, "summary": summary, "ts": now_ts()})
        self.current_stage = stage
        self.updated_at = now_ts()
