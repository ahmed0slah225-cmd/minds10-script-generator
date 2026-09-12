from dataclasses import dataclass, field
from typing import Callable, Dict, List


@dataclass(frozen=True)
class SkillSpec:
    name: str
    kind: str
    phase: str
    requires_llm: bool
    dependencies: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)


SKILLS = [
    SkillSpec("voice_dna_ar_eg", "profile", "pre_write", False),
    SkillSpec("viral_hooks_ar_eg", "generation_review", "planning", True, ["voice_dna_ar_eg"]),
    SkillSpec("storytelling_ar_eg", "planning_generation", "planning", True, ["voice_dna_ar_eg"]),
    SkillSpec("retention_ar_eg", "planning_review", "planning_review", True, ["viral_hooks_ar_eg"]),
    SkillSpec("dumpify_ar_eg", "rewrite", "explanation", True),
    SkillSpec("humanize_ar_eg", "rewrite", "post_write", True, ["voice_dna_ar_eg"]),
    SkillSpec("anti_slop_ar_eg", "review", "post_write", True, ["voice_dna_ar_eg"]),
]

REGISTRY: Dict[str, SkillSpec] = {skill.name: skill for skill in SKILLS}


def get_skill(name: str) -> SkillSpec:
    return REGISTRY[name]
