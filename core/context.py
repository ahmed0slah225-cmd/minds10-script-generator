"""
PipelineContext — الحامل الوحيد لكل حالة المشروع داخل التنفيذ.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ProjectSettings:
    project_name: str = "مشروع بدون اسم"
    duration_minutes: int = 15
    audience: str = ""
    language: str = "ar-EG"
    output_format: str = "youtube-long-form"
    voice_dna_id: Optional[str] = None


@dataclass
class ResearchConfig:
    enabled: bool = False
    depth: str = "standard"  # basic | standard | deep
    timestamp: Optional[str] = None
    run_id: Optional[str] = None


@dataclass
class ModelConfig:
    default_model: str = "gemini-3.6-flash"
    engine_overrides: Dict[str, str] = field(default_factory=dict)
    allow_auto_fallback: bool = False

    def model_for(self, engine_name: str) -> str:
        return self.engine_overrides.get(engine_name, self.default_model)


@dataclass
class KnowledgeItem:
    text: str
    kind: str = "fact"  # fact | quote | number | story | example | contradiction | doubt
    source: str = ""
    source_type: str = "user"  # user | research | model_inference
    confidence: str = "medium"  # high | medium | low | unverified


@dataclass
class PipelineContext:
    project_settings: ProjectSettings = field(default_factory=ProjectSettings)
    raw_input: str = ""
    source_type: str = "text"
    source_files: List[Any] = field(default_factory=list)
    pdf_page_range: Optional[tuple] = None

    research_config: ResearchConfig = field(default_factory=ResearchConfig)
    model_config: ModelConfig = field(default_factory=ModelConfig)

    topic_analysis: Optional[Dict[str, Any]] = None
    research_results: List[Dict[str, Any]] = field(default_factory=list)
    knowledge_base: List[KnowledgeItem] = field(default_factory=list)
    audience_profile: Optional[Dict[str, Any]] = None
    strategy: Optional[Dict[str, Any]] = None
    story: Optional[Dict[str, Any]] = None
    outline: Optional[Dict[str, Any]] = None
    hook: Optional[str] = None
    draft: Optional[str] = None
    humanized: Optional[str] = None
    slop_report: Optional[Dict[str, Any]] = None
    retention_report: Optional[Dict[str, Any]] = None
    final_script: Optional[str] = None

    voice_dna: Optional[Dict[str, Any]] = None
    reviews: List[Dict[str, Any]] = field(default_factory=list)
    run_log: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)