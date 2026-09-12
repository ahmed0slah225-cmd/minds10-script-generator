from dataclasses import dataclass
from .skill_loader import load_skill

@dataclass(frozen=True)
class SkillSpec:
    name: str
    kind: str
    phase: str
    requires_llm: bool
    dependencies: tuple[str,...]=()
    conflicts: tuple[str,...]=()
    deterministic_checks: tuple[str,...]=()

SKILLS={
'voice_dna_ar_eg':SkillSpec('voice_dna_ar_eg','profile','analysis+shared',True,deterministic_checks=('schema',)),
'viral_hooks_ar_eg':SkillSpec('viral_hooks_ar_eg','generation+review','hook',True),
'storytelling_ar_eg':SkillSpec('storytelling_ar_eg','generation+planning','story',True),
'retention_ar_eg':SkillSpec('retention_ar_eg','planning+review','strategy+outline+hook+post_write',True),
'dumpify_ar_eg':SkillSpec('dumpify_ar_eg','rewrite','pre_write+edit',True),
'humanize_ar_eg':SkillSpec('humanize_ar_eg','rewrite','post_write',True,('voice_dna_ar_eg',)),
'anti_slop_ar_eg':SkillSpec('anti_slop_ar_eg','review','post_write',True,('voice_dna_ar_eg',)),
'addictive_writing_ar_eg':SkillSpec('addictive_writing_ar_eg','generation+rewrite+review','strategy+story+script',True),
'deep_research_ar_eg':SkillSpec('deep_research_ar_eg','analysis','research',True),
'deep_thinking_ar_eg':SkillSpec('deep_thinking_ar_eg','planning+analysis','topic+source+knowledge+audience',True),
'repetition_ar_eg':SkillSpec('repetition_ar_eg','review','post_write',True),
'egyptian_editor_ar_eg':SkillSpec('egyptian_editor_ar_eg','rewrite','post_review',True,('voice_dna_ar_eg',)),
'truth_check_ar_eg':SkillSpec('truth_check_ar_eg','validation','pre_final',True),
'final_editor_ar_eg':SkillSpec('final_editor_ar_eg','rewrite+validation','final',True,('anti_slop_ar_eg','repetition_ar_eg','truth_check_ar_eg')),
}

def get_skill(name):
    if name not in SKILLS: raise KeyError(name)
    return SKILLS[name]

def validate_dependencies(names):
    selected=set(names); errors=[]
    for n in names:
        s=get_skill(n)
        for dep in s.dependencies:
            if dep not in selected: errors.append(f'{n} requires {dep}')
        for conflict in s.conflicts:
            if conflict in selected: errors.append(f'{n} conflicts with {conflict}')
    return errors
