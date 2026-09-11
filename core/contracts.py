"""
عقود المشروع — Manifests, Results
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SkillManifest:
    name: str
    version: str = "1.0.0"
    # generation | planning | analysis | review | rewrite | validation
    skill_type: str = "generation"
    # pre_write | during_write | post_write | review | edit | final
    stage: str = "post_write"
    description: str = ""
    depends_on: List[str] = field(default_factory=list)
    conflicts_with: List[str] = field(default_factory=list)
    requires_llm: bool = True
    engine: str = ""  # اسم الـEngine اللي بتُستخدم داخله
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillResult:
    skill_name: str
    output: Any = None
    warnings: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None