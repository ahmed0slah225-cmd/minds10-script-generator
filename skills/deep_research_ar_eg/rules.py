"""
skills/deep_research_ar_eg/rules.py
======================================
راجع skill.md للعقد الكامل.
"""

from __future__ import annotations

from skills.base import BaseSkill, SkillResult

_SYSTEM_PROMPT = """أنت باحث متخصص في تجميع معرفة تخدم سكريبت يوتيوب
باللهجة المصرية. مش مطلوب منك تثبت إنك بحثت — مطلوب منك معلومة تخدم
الفكرة فعلًا.

قواعد صارمة:
- ممنوع اختراع دراسة أو رقم أو مصدر غير موجود في المدخلات.
- كل نتيجة لازم توضّح مصدرها: user_source (من مصادر المستخدم) أو
  web_search (من بحث خارجي مرفق).
- لو معلومة غير مؤكدة، وضّح إنها needs_verification بدل ما تعرضها
  كحقيقة.
- ركّز على المعلومات اللي فعلًا تخدم زاوية الفيديو، مش كل حاجة موجودة.

أعد ردك بصيغة JSON فقط:
{
  "findings": [
    {"content": "...", "origin": "user_source", "relevance": "...", "confidence": "confirmed"}
  ],
  "gaps": ["..."]
}"""


class DeepResearchSkill(BaseSkill):
    name = "deep_research_ar_eg"

    def synthesize(
        self,
        topic_understanding: dict,
        user_source_excerpts: list[str],
        web_snippets: list[dict] | None = None,
    ) -> SkillResult:
        parts = [f"فهم الموضوع:\n{topic_understanding}"]
        if user_source_excerpts:
            parts.append("مقتطفات من مصادر المستخدم:\n" + "\n".join(f"- {e}" for e in user_source_excerpts))
        if web_snippets:
            web_text = "\n".join(f"- [{s.get('title','')}] {s.get('snippet','')}" for s in web_snippets)
            parts.append(f"نتائج بحث خارجي (استخدمها فقط لو فعلًا تخدم الفكرة):\n{web_text}")
        else:
            parts.append("لا يوجد بحث خارجي متاح لهذه الدورة — اعتمد على مصادر المستخدم فقط.")
        user_prompt = "\n\n---\n\n".join(parts)
        raw = self._call(_SYSTEM_PROMPT, user_prompt, temperature=0.3)
        return SkillResult.parse_json(self.name, "extract", raw)
