"""
skills/viral_hooks_ar_eg/rules.py
====================================
راجع skill.md للعقد الكامل.
"""

from __future__ import annotations

from skills.base import BaseSkill, SkillResult

_SYSTEM_PROMPT = """أنت متخصص في هوكات سكريبتات يوتيوب باللهجة المصرية.

مبدأك الأساسي: الهوك وعد للمشاهد، مش جملة جذابة فاضية. الهوك القوي فيه:
موقف + ألم + سؤال/غموض + وعد ضمني بتفسير أو اكتشاف قادم.

ممنوع:
- "استنى للآخر" بدون وعد حقيقي وراها.
- سؤال عام سطحي ("هل حسيت يومًا إنك...").
- أي مبالغة أو وعد لا يستطيع الفيديو الوفاء به.

اقترح 3 هوكات مختلفة، وحدد أنسبهم.

أعد ردك بصيغة JSON فقط:
{
  "hooks": [
    {"text": "...", "why_it_works": "...", "risk": "none"}
  ],
  "recommended_index": 0
}"""


class ViralHooksSkill(BaseSkill):
    name = "viral_hooks_ar_eg"

    def build_hooks(
        self,
        opening_situation: str,
        promise: str,
        audience_pain_point: str,
        voice_dna_fragment: str = "",
    ) -> SkillResult:
        parts = [
            f"الموقف الافتتاحي:\n{opening_situation}",
            f"وعد الفيديو:\n{promise}",
            f"ألم المشاهد:\n{audience_pain_point}",
        ]
        if voice_dna_fragment:
            parts.append(voice_dna_fragment)
        user_prompt = "\n\n---\n\n".join(parts)
        raw = self._call(_SYSTEM_PROMPT, user_prompt, temperature=0.7)
        return SkillResult.parse_json(self.name, "plan", raw)
