"""
skills/storytelling_ar_eg/rules.py
=====================================
راجع skill.md للعقد الكامل.
"""

from __future__ import annotations

from skills.base import BaseSkill, SkillResult

STORY_ARC_AR = ["سؤال", "حيرة", "اكتشاف", "تفسير", "تعقيد", "مفاجأة", "فهم جديد"]

_SYSTEM_PROMPT = f"""أنت مهندس حكاية (Story Architect) لسكريبتات يوتيوب
باللهجة المصرية. مهمتك بناء هيكل حكاية يبدأ من الإنسان مش من المعلومة.

استخدم القوس السردي التالي بالترتيب ده:
موقف يومي محسوس → {" → ".join(STORY_ARC_AR)}

قواعد:
- الموقف الافتتاحي (opening_situation) لازم يكون مشهد محسوس وملموس،
  مش تعريف أكاديمي ولا سؤال عام مباشر.
- كل Beat لازم يبني على اللي قبله، ومترابط بالأفكار الأساسية المرفقة.
- لا تخترع حقائق أو أرقام غير موجودة في المعرفة الموثقة المرفقة.

أعد ردك بصيغة JSON فقط:
{{
  "opening_situation": "...",
  "beats": [
    {{"beat": "سؤال", "content": "..."}},
    {{"beat": "حيرة", "content": "..."}},
    {{"beat": "اكتشاف", "content": "..."}},
    {{"beat": "تفسير", "content": "..."}},
    {{"beat": "تعقيد", "content": "..."}},
    {{"beat": "مفاجأة", "content": "..."}},
    {{"beat": "فهم جديد", "content": "..."}}
  ]
}}"""


class StorytellingSkill(BaseSkill):
    name = "storytelling_ar_eg"

    def build_story_beats(
        self,
        topic_understanding: dict,
        core_ideas: list[str],
        audience_pain_point: str,
        knowledge_facts: list[str],
    ) -> SkillResult:
        user_prompt = (
            f"فهم الموضوع:\n{topic_understanding}\n\n"
            f"الأفكار الأساسية:\n" + "\n".join(f"- {i}" for i in core_ideas) + "\n\n"
            f"ألم المشاهد:\n{audience_pain_point}\n\n"
            f"معرفة موثقة متاحة:\n" + "\n".join(f"- {f}" for f in knowledge_facts)
        )
        raw = self._call(_SYSTEM_PROMPT, user_prompt, temperature=0.6)
        return SkillResult.parse_json(self.name, "plan", raw)
