"""
skills/base.py
================
العقد المشترك لكل الـ9 Skills. أي Skill هنا بيرجّع SkillResult موحّد،
وبيستخدم GeminiClient (من engine/gemini_client.py) بدل ما يعمل استدعاء
مباشر بنفسه.

الفرق عن الـEngines: الـSkill مالوش حالة (Stateless) ومالوش وصول مباشر
لقاعدة البيانات — بياخد نص ومعطيات، ويرجّع نتيجة. الـEngine هو اللي بيقرر
يستخدم أنهي Skill وإمتى، ويحفظ النتيجة في الـProjectContext.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Optional

from engine.gemini_client import GeminiClient


@dataclass
class SkillResult:
    skill_name: str
    mode: str  # "review" | "rewrite" | "extract" | "plan"
    ok: bool
    data: dict = field(default_factory=dict)
    raw_response: Optional[str] = None
    error: Optional[str] = None

    @staticmethod
    def parse_json(skill_name: str, mode: str, raw: str) -> "SkillResult":
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.strip()
        try:
            data = json.loads(cleaned)
            return SkillResult(skill_name=skill_name, mode=mode, ok=True, data=data, raw_response=raw)
        except json.JSONDecodeError as e:
            return SkillResult(
                skill_name=skill_name, mode=mode, ok=False, data={}, raw_response=raw,
                error=f"فشل تفسير رد الموديل كـJSON: {e}",
            )


class BaseSkill:
    """كل Skill بيرث من الكلاس ده. بيوفر نداء موحّد لـGemini."""

    name: str = "base"

    def __init__(self, llm: Optional[GeminiClient] = None):
        self.llm = llm or GeminiClient()

    def _call(self, system_prompt: str, user_prompt: str, *, temperature: float = 0.4) -> str:
        return self.llm.generate(system_prompt, user_prompt, temperature=temperature)
