"""
engine/editor_engine.py
==========================
مرحلة "Egyptian Arabic Editing" — النداء التاني والأخير المسموح فيه
Rewrite في الـpipeline كله (الأول كان Humanization). هنا بيتجمّع:

- ملاحظات Anti-Slop Review
- ملاحظات Retention Review
- ملاحظات Repetition Review
- قواعد Dumbify (كفقرة إرشادية، مش نداء منفصل)
- بصمة الكاتب الصوتية

وكل ده بيتبعت في Prompt واحد بس، فيطلع السكريبت المصري النهائي.
ده اللي بيحقق قاعدة "استدعاء Rewrite واحد نهائي بكل الملاحظات مجمّعة"
اللي اتفقنا عليها لتجنب تكرار الكتابة وزيادة التكلفة.
"""

from __future__ import annotations

from typing import Optional

from engine.gemini_client import GeminiClient
from engine.models import ProjectContext
from skills import DUMBIFY_PROMPT_FRAGMENT_AR
from skills.base import SkillResult

_SYSTEM_PROMPT = f"""أنت المحرر النهائي (Final Editor) لسكريبتات يوتيوب
باللهجة المصرية. معاك سكريبت اتكتب وانأنس بالفعل، ومعاك قائمة ملاحظات
من 3 مراجعات مختلفة. مهمتك: تطبيق أقل تعديل ممكن يحل كل مشكلة، مش
إعادة كتابة السكريبت من جديد.

{DUMBIFY_PROMPT_FRAGMENT_AR}

قواعد صارمة:
- التزم بترتيب الأولوية: المعنى أولاً، ثم الوضوح، ثم الإنسانية، ثم الإيقاع.
- حافظ على كل الحقائق والمصادر كما هي.
- أي تعديل ما يجوزش يغيّر الفكرة الأساسية للسكريبت.
- لو ملاحظة مراجعتين بتتعارض، رجّح اللي بيحافظ على المعنى والمصداقية.
- طبّق بس الملاحظات المرفقة فعليًا — ما تضيفش تعديلات من عندك من غير سبب.

أعد ردك بصيغة JSON فقط:
{{
  "final_text": "السكريبت الكامل بعد التحرير النهائي",
  "applied_fixes_count": 0,
  "skipped_fixes": [{{"issue": "...", "why_skipped": "..."}}]
}}"""


class EditorEngine:
    def __init__(self, llm: Optional[GeminiClient] = None):
        self.llm = llm or GeminiClient()

    def run(self, ctx: ProjectContext, retention_review: dict) -> ProjectContext:
        anti_slop_issues = ctx.reviews.get("anti_slop", {}).get("issues", [])
        repetition_issues = ctx.reviews.get("repetition", {}).get("issues", [])

        user_prompt = (
            f"السكريبت (بعد الأنسنة):\n\n{ctx.humanized_script}\n\n---\n\n"
            f"ملاحظات Anti-Slop:\n{anti_slop_issues}\n\n"
            f"ملاحظات Retention Review:\n{retention_review}\n\n"
            f"ملاحظات Repetition Review:\n{repetition_issues}\n\n"
            f"{ctx.voice_dna.to_prompt_fragment()}"
        )
        raw = self.llm.generate(_SYSTEM_PROMPT, user_prompt, temperature=0.3)
        result = SkillResult.parse_json("editor_engine", "rewrite", raw)
        if result.ok:
            ctx.egyptian_final_script = result.data.get("final_text", ctx.humanized_script)
        else:
            ctx.egyptian_final_script = ctx.humanized_script
        ctx.reviews["retention"] = retention_review
        ctx.touch("egyptian_arabic_editing")
        return ctx
