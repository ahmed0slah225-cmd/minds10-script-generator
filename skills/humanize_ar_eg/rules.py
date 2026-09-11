"""
skills/humanize_ar_eg/rules.py
================================
راجع skill.md في نفس المجلد للعقد الكامل. هنا التنفيذ فقط.
"""

from __future__ import annotations

from skills.base import BaseSkill, SkillResult

NINE_LEVERS_AR = [
    "تنويع إيقاع الجملة",
    "تفاصيل ملموسة مدعومة من السياق",
    "التردد الطبيعي (يعني/بصراحة/وقفة قبل فكرة مهمة)",
    "مخاطبة مباشرة بصيغة إنت",
    "أسئلة داخلية بدل الجزم الدائم",
    "مفردات يومية بدل المصطلحات الرسمية",
    "انتقالات كلامية طبيعية بدل الجاهزة",
    "الاعتراف بالتعقيد بدل الحلول شديدة البساطة",
    "إيقاف الجملة المثالية المقفولة بإحكام",
]

_SYSTEM_PROMPT = f"""أنت محرر "أنسنة" متخصص في سكريبتات يوتيوب باللهجة
المصرية. مهمتك تحويل مسودة مكتوبة بشكل صحيح ومنظم إلى نص حاسس إن إنسان
حقيقي بيقوله قدام كاميرا، مش نص بيتقرأ.

استخدم الروافع التسعة دي حسب ما يناسب النص (مش شرط كلهم في كل فقرة):
{chr(10).join(f"{i+1}. {lever}" for i, lever in enumerate(NINE_LEVERS_AR))}

ممنوع تمامًا:
- إضافة أي معلومة أو حدث أو تجربة شخصية غير موجودة في النص الأصلي.
- تغيير المعنى أو حذف معلومة موجودة.
- المبالغة في العامية لدرجة الخروج عن الطبيعية.
- تحويل كل الجمل لنفس الطول القصير.

أعد ردك بصيغة JSON فقط:
{{
  "humanized_text": "النص الكامل بعد الأنسنة",
  "levers_applied": ["..."],
  "change_log": [{{"before": "اقتباس أقل من 15 كلمة", "after": "اقتباس أقل من 15 كلمة", "why": "..."}}]
}}"""


class HumanizeSkill(BaseSkill):
    name = "humanize_ar_eg"

    def run(
        self,
        script_text: str,
        voice_dna_fragment: str = "",
        known_facts: list[str] | None = None,
    ) -> SkillResult:
        parts = [f"السكريبت المطلوب أنسنته:\n\n{script_text}"]
        if voice_dna_fragment:
            parts.append(voice_dna_fragment)
        if known_facts:
            parts.append("معلومات موثقة (لا تخرج عنها):\n" + "\n".join(f"- {f}" for f in known_facts))
        user_prompt = "\n\n---\n\n".join(parts)
        raw = self._call(_SYSTEM_PROMPT, user_prompt, temperature=0.6)
        return SkillResult.parse_json(self.name, "rewrite", raw)
