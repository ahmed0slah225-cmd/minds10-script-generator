from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import uuid4


def new_id() -> str:
    return uuid4().hex

@dataclass
class Project:
    id: str
    title: str
    request: str
    duration_minutes: int
    audience: str = "مشاهد عربي/مصري عام مهتم بالموضوع"
    language: str = "ar-eg"
    current_stage: str = "input"

@dataclass
class Source:
    id: str
    project_id: str
    kind: str
    title: str
    locator: str = ""
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PipelineState:
    project: Project
    raw_input: str
    sources: List[Source] = field(default_factory=list)
    topic: Dict[str, Any] = field(default_factory=dict)
    research: Dict[str, Any] = field(default_factory=dict)
    knowledge: Dict[str, Any] = field(default_factory=dict)
    audience: Dict[str, Any] = field(default_factory=dict)
    strategy: Dict[str, Any] = field(default_factory=dict)
    story: Dict[str, Any] = field(default_factory=dict)
    retention: Dict[str, Any] = field(default_factory=dict)
    hook: Dict[str, Any] = field(default_factory=dict)
    script: str = ""
    humanized_script: str = ""
    anti_slop: Dict[str, Any] = field(default_factory=dict)
    retention_review: Dict[str, Any] = field(default_factory=dict)
    repetition_review: Dict[str, Any] = field(default_factory=dict)
    egyptian_edit: Dict[str, Any] = field(default_factory=dict)
    voice_dna: Dict[str, Any] = field(default_factory=dict)
    final_review: Dict[str, Any] = field(default_factory=dict)
    final_script: str = ""
    citations: List[Dict[str, Any]] = field(default_factory=list)
    stage_outputs: Dict[str, Any] = field(default_factory=dict)
