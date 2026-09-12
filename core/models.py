from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Literal
from pydantic import BaseModel, Field

Provenance = Literal['user_provided','user_file','web_research','model_inference','unverified']

class Source(BaseModel):
    id: str; title: str; url: str|None=None; kind: str='unknown'; provenance: Provenance='unverified'; collected_at: str|None=None; original: bool|None=None; confidence: float=0.0; content: str=''; page_start: int|None=None; page_end: int|None=None

class KnowledgeItem(BaseModel):
    id: str; kind: Literal['idea','fact','claim','evidence','story','example','number','quote','source_note','contradiction','uncertainty']; text: str; provenance: Provenance; source_ids: list[str]=Field(default_factory=list); confidence: float=0.0; verified: bool=False

class ReviewIssue(BaseModel):
    id: str; reviewer: str; dimension: str; score: float|None=None; severity: Literal['low','medium','high','critical']='medium'; location: str=''; problem: str; reason: str; suggested_fix: str=''; priority: int=3

class ReviewResult(BaseModel):
    reviewer: str; passed: bool; scores: dict[str,float]=Field(default_factory=dict); issues: list[ReviewIssue]=Field(default_factory=list); summary: str=''

class VoiceDNA(BaseModel):
    profile_id: str='default'; sentence_length: str=''; rhythm: str=''; colloquial_level: str=''; vocabulary: str=''; question_style: str=''; viewer_address: str=''; emotion: str=''; explanation_style: str=''; example_style: str=''; storytelling_style: str=''; transitions: str=''; curiosity_style: str=''; metaphors: str=''; endings: str=''; formality: str=''; spontaneity: str=''; forbidden_tells: list[str]=Field(default_factory=list)

class ProjectSettings(BaseModel):
    name: str='مشروع جديد'; duration_minutes: int=30; audience: str='شباب وبنات مصريين يحبوا الحكي والأمثلة ومش المحاضرات'; language: str='ar-EG'; model_label: str='Gemini 3.6 Flash'; web_research: bool=False; research_depth: Literal['basic','standard','deep']='standard'; voice_profile_id: str='default'; pdf_page_start: int|None=None; pdf_page_end: int|None=None

class ProjectState(BaseModel):
    project_id: str; version: int=1; created_at: str=Field(default_factory=lambda:datetime.now(timezone.utc).isoformat()); updated_at: str=Field(default_factory=lambda:datetime.now(timezone.utc).isoformat()); settings: ProjectSettings; input_text: str=''; source_text: str=''; topic_analysis: dict[str,Any]=Field(default_factory=dict); audience_analysis: dict[str,Any]=Field(default_factory=dict); strategy: dict[str,Any]=Field(default_factory=dict); story_plan: dict[str,Any]=Field(default_factory=dict); retention_plan: dict[str,Any]=Field(default_factory=dict); hook_set: list[Any]=Field(default_factory=list); outline: list[dict[str,Any]]=Field(default_factory=list); draft: str=''; final_script: str=''; sources: list[Source]=Field(default_factory=list); knowledge: list[KnowledgeItem]=Field(default_factory=list); reviews: list[ReviewResult]=Field(default_factory=list); voice_dna: VoiceDNA=Field(default_factory=VoiceDNA); metadata: dict[str,Any]=Field(default_factory=dict)
