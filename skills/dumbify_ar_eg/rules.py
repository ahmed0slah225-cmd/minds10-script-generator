"""
skills/dumbify_ar_eg/rules.py
================================
راجع skill.md — القاعدة هنا معدّة أصلًا للحقن جوه Prompt الـEditor
الواحد، مش لعمل نداء Gemini منفصل في المسار الافتراضي.
"""

from __future__ import annotations

from skills.base import BaseSkill, SkillResult

DUMBIFY_PROMPT_FRAGMENT_AR = """قاعدة التبسيط (Dumbify — بدون تسطيح):
- استبدل أي مصطلح رسمي بمرادف يومي بدون فقدان الدقة.
- قصّر الجملة المركبة الطويلة بدون حذف أي جزء من معناها.
- لو فكرة معقدة، اشرحها بمثال بدل ما تحذفها أو تبسطها لدرجة تفقد قيمتها.
- ممنوع تحويل كل الفقرة لجمل قصيرة متتالية بنفس الشكل."""

_STANDALONE_SYSTEM_PROMPT = f"""أنت متخصص في تبسيط اللغة لسكريبتات يوتيوب
باللهجة المصرية بدون تسطيح الأفكار.

{DUMBIFY_PROMPT_FRAGMENT_AR}

أعد ردك بصيغة JSON فقط:
{{
  "simplified_text": "...",
  "change_log": [{{"before": "اقتباس أقل من 15 كلمة", "after": "اقتباس أقل من 15 كلمة", "why": "..."}}]
}}"""


class DumbifySkill(BaseSkill):
    name = "dumbify_ar_eg"

    def run(self, text: str, known_facts: list[str] | None = None) -> SkillResult:
        """
        استخدام مستقل (مثلاً فيتشر يدوي في الواجهة: 'بسّط الفقرة دي').
        غير مستخدمة في المسار الافتراضي للـpipeline — استخدم
        DUMBIFY_PROMPT_FRAGMENT_AR بدل كده جوه engine/editor_engine.py.
        """
        facts_note = ""
        if known_facts:
            facts_note = "\n\nمعلومات موثقة:\n" + "\n".join(f"- {f}" for f in known_facts)
        user_prompt = f"النص:\n\n{text}{facts_note}"
        raw = self._call(_STANDALONE_SYSTEM_PROMPT, user_prompt, temperature=0.4)
        return SkillResult.parse_json(self.name, "rewrite", raw)
