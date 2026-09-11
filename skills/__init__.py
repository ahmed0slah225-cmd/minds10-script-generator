"""
skills package
================
تصدير موحّد لكل الـ9 Skills. راجع مجلد كل Skill لملف skill.md بتاعه
للعقد الكامل (Input/Output Contract + القواعد + المسموح والممنوع).
"""

from .base import BaseSkill, SkillResult
from .humanize_ar_eg.rules import HumanizeSkill, NINE_LEVERS_AR
from .addictive_writing_ar_eg.rules import AddictiveWritingSkill
from .stop_slop_ar_eg.rules import StopSlopSkill, REVIEW_THRESHOLD_TOTAL
from .storytelling_ar_eg.rules import StorytellingSkill, STORY_ARC_AR
from .viral_hooks_ar_eg.rules import ViralHooksSkill
from .dumbify_ar_eg.rules import DumbifySkill, DUMBIFY_PROMPT_FRAGMENT_AR
from .voice_dna_ar_eg.rules import VoiceDNASkill
from .deep_research_ar_eg.rules import DeepResearchSkill
from .deep_thinking_ar_eg.rules import DeepThinkingSkill

__all__ = [
    "BaseSkill", "SkillResult",
    "HumanizeSkill", "NINE_LEVERS_AR",
    "AddictiveWritingSkill",
    "StopSlopSkill", "REVIEW_THRESHOLD_TOTAL",
    "StorytellingSkill", "STORY_ARC_AR",
    "ViralHooksSkill",
    "DumbifySkill", "DUMBIFY_PROMPT_FRAGMENT_AR",
    "VoiceDNASkill",
    "DeepResearchSkill",
    "DeepThinkingSkill",
]
