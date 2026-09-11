"""
skills/voice_dna_ar_eg/rules.py
==================================
راجع skill.md للعقد الكامل. الشكل النهائي (VoiceDNAProfile) موجود في
engine/models.py عشان يبقى قابل للتخزين المباشر في قاعدة البيانات.
"""

from __future__ import annotations

from skills.base import BaseSkill, SkillResult
from engine.models import VoiceDNAProfile

VOICE_DNA_FIELDS = [
    "sentence_length_pattern", "pacing", "question_usage", "audience_address_style",
    "vocabulary_level", "slang_degree", "emotional_degree", "idea_explanation_style",
    "example_building_style", "transition_style", "curiosity_building_style",
    "idea_closing_style", "metaphor_usage", "formality_level", "spontaneity_degree",
]

_EXTRACT_SYSTEM_PROMPT = """أنت محلل أسلوب كتابة متخصص في استخراج "بصمة
صوتية" (Voice DNA) لكاتب سكريبتات يوتيوب باللهجة المصرية.

حلّل العيّنات المرفقة، واستخرج الأنماط المتكررة فقط — مش تلخيص المحتوى.

ممنوع: اختراع سمة غير موجودة، اقتباس جمل كاملة، افتراض تقليد كاتب مشهور.

أعد ردك بصيغة JSON فقط:
{
  "traits": {""" + ", ".join(f'"{f}": "..."' for f in VOICE_DNA_FIELDS) + """},
  "notes": "..."
}"""

_CONSISTENCY_SYSTEM_PROMPT = """أنت مراجع اتساق أسلوب. قيّم مدى التزام
سكريبت جديد ببصمة الكاتب الصوتية المرفقة. لا تعيد كتابة أي جزء.

أعد ردك بصيغة JSON فقط:
{
  "consistency_score": <1-10>,
  "matches": ["..."],
  "deviations": [{"where": "اقتباس أقل من 10 كلمات", "issue": "...", "suggestion": "..."}]
}"""


class VoiceDNASkill(BaseSkill):
    name = "voice_dna_ar_eg"

    def extract(self, writing_samples: list[str], writer_id: str = "default") -> SkillResult:
        if len(writing_samples) < 2:
            return SkillResult(
                skill_name=self.name, mode="extract", ok=False,
                error="محتاج عيّنتين على الأقل لاستخراج أنماط متكررة فعلاً.",
            )
        joined = "\n\n---\n\n".join(f"[عيّنة {i+1}]\n{s}" for i, s in enumerate(writing_samples))
        raw = self._call(_EXTRACT_SYSTEM_PROMPT, joined, temperature=0.2)
        result = SkillResult.parse_json(self.name, "extract", raw)
        if result.ok:
            result.data["writer_id"] = writer_id
        return result

    def consistency_check(self, script_text: str, profile: VoiceDNAProfile) -> SkillResult:
        user_prompt = f"{profile.to_prompt_fragment()}\n\n---\n\nالسكريبت:\n\n{script_text}"
        raw = self._call(_CONSISTENCY_SYSTEM_PROMPT, user_prompt, temperature=0.2)
        return SkillResult.parse_json(self.name, "review", raw)
