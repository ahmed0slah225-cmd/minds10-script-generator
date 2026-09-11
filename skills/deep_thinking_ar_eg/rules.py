"""
skills/deep_thinking_ar_eg/rules.py
======================================
راجع skill.md للعقد الكامل.
"""

from __future__ import annotations

from skills.base import BaseSkill, SkillResult

_ANALYZE_TOPIC_PROMPT = """أنت محلل موضوعات لسكريبتات يوتيوب باللهجة
المصرية. مبدأك الأساسي: "المشروع لا يبدأ بالكتابة، المشروع يبدأ بالفهم."

المطلوب: خد المدخل الخام وفكّكه. الموضوع الظاهري حاجة، والمشكلة
الإنسانية تحته حاجة تانية غالبًا. لا تفترض المعنى الأول اللي هيجيلك في
دماغك — استكشف احتمالات متعددة.

أعد ردك بصيغة JSON فقط:
{
  "surface_topic": "الموضوع الظاهري كما ورد",
  "possible_underlying_problems": ["احتمال 1", "احتمال 2", "..."],
  "core_ideas": ["فكرة رئيسية ممكن يُبنى عليها الفيديو", "..."]
}"""

_FIND_ANGLE_PROMPT = """أنت استراتيجي محتوى لسكريبتات يوتيوب باللهجة
المصرية. من فهم الموضوع وألم المشاهد والمعرفة الموثقة المرفقة، حدد:

- زاوية الفيديو (Angle): إيه أعمق زاوية ممكن نتناول بيها الموضوع؟
- السؤال المركزي اللي الفيديو بيجاوب عليه.
- الوعد للمشاهد (Promise): إيه اللي هياخده لو كمّل للآخر.
- التحول (Viewer Shift): إيه اللي هيتغير في تفكيره بعد الفيديو.

قاعدة صارمة: الزاوية لازم تُبنى على المعرفة الموثقة المرفقة فقط، بدون
اختراع أي حقيقة أو رقم لدعمها.

أعد ردك بصيغة JSON فقط:
{
  "angle": "...",
  "central_question": "...",
  "promise_to_viewer": "...",
  "viewer_shift": "..."
}"""


class DeepThinkingSkill(BaseSkill):
    name = "deep_thinking_ar_eg"

    def analyze_topic(self, raw_input: str) -> SkillResult:
        raw = self._call(_ANALYZE_TOPIC_PROMPT, f"المدخل الخام:\n\n{raw_input}", temperature=0.5)
        return SkillResult.parse_json(self.name, "extract", raw)

    def find_angle(
        self, topic_understanding: dict, audience_pain_point: str, known_facts: list[str]
    ) -> SkillResult:
        user_prompt = (
            f"فهم الموضوع:\n{topic_understanding}\n\n"
            f"ألم المشاهد:\n{audience_pain_point}\n\n"
            f"معرفة موثقة:\n" + "\n".join(f"- {f}" for f in known_facts)
        )
        raw = self._call(_FIND_ANGLE_PROMPT, user_prompt, temperature=0.5)
        return SkillResult.parse_json(self.name, "plan", raw)
