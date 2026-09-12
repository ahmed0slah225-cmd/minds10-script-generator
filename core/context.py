"""
core/context.py
================
PipelineContext: الحالة المشتركة لمشروع سيناريو واحد وهو يمر عبر المراحل.
القاعدة (بند 62): لا تُمرَّر كل الحقول لكل Skill/Engine؛ كل واحد يطلب فقط ما
يحتاجه عبر دوال .slice_for_xxx() أو بالوصول المباشر للحقول المطلوبة.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class ResearchConfig:
    enabled: bool = False          # الحالة الافتراضية: إيقاف (بند 21)
    depth: str = "قياسي"           # أساسي / قياسي / عميق


@dataclass
class SourceMaterial:
    kind: str                      # "text" | "pdf" | "topic" | "url"
    raw_text: Optional[str] = None
    pdf_path: Optional[str] = None
    pdf_page_start: Optional[int] = None
    pdf_page_end: Optional[int] = None
    url: Optional[str] = None


@dataclass
class KnowledgeItem:
    content: str
    origin: str            # "user_provided" | "source_backed" | "web_research" | "model_inference" | "unverified"
    source_ref: str = ""
    confidence: str = "غير محدد"


@dataclass
class VoiceDNA:
    name: str = "افتراضي"
    sentence_length_profile: str = "متنوع"
    slang_level: str = "متوسط"
    notes: str = ""
    sample_texts: List[str] = field(default_factory=list)


@dataclass
class PipelineContext:
    # إعدادات المشروع
    project_name: str
    duration_minutes: int
    audience: str
    language: str = "العربية المصرية"
    default_model_id: str = "gemini-3.6-flash"
    engine_model_overrides: Dict[str, str] = field(default_factory=dict)
    research_config: ResearchConfig = field(default_factory=ResearchConfig)
    voice_dna: VoiceDNA = field(default_factory=VoiceDNA)

    # مدخلات
    source: Optional[SourceMaterial] = None

    # نواتج المراحل (تُملأ تباعًا بواسطة الـ Orchestrator)
    topic_understanding: Dict[str, Any] = field(default_factory=dict)
    knowledge_base: List[KnowledgeItem] = field(default_factory=list)
    audience_profile: Dict[str, Any] = field(default_factory=dict)
    strategy: Dict[str, Any] = field(default_factory=dict)
    story: Dict[str, Any] = field(default_factory=dict)
    hooks: List[str] = field(default_factory=list)
    outline: List[Dict[str, Any]] = field(default_factory=list)
    draft_script: str = ""
    humanized_script: str = ""
    anti_slop_report: Dict[str, Any] = field(default_factory=dict)
    final_script: str = ""

    # تتبّع
    run_logs: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def model_for(self, engine_name: str) -> str:
        return self.engine_model_overrides.get(engine_name, self.default_model_id)

    def log(self, engine: str, status: str, extra: Optional[Dict[str, Any]] = None):
        entry = {"engine": engine, "status": status}
        if extra:
            entry.update(extra)
        self.run_logs.append(entry)
