"""
engines/understanding_engine.py
================================
المبدأ الحاكم: لا تبدأ بالكتابة. ابدأ بالفهم.
يحلل المادة الخام (نص/PDF/موضوع) ويستخرج: الموضوع، المشكلة الإنسانية،
الفكرة المركزية، الزاوية، ما نعرفه، ما نحتاج للبحث عنه.
"""

from __future__ import annotations
import json

from core.contracts import Engine, StepResult
from core.context import PipelineContext
from engines.common import call_llm

SYSTEM_PROMPT = """
أنت محرك "فهم الموضوع" داخل منصة إنتاج سكريبتات يوتيوب.
مهمتك الوحيدة: فهم المادة الخام المُعطاة قبل أي كتابة، وليس كتابة أي جزء من السكريبت.
أعد الإجابة بصيغة JSON فقط بالحقول التالية بالضبط، وبالعربية:
{
  "topic": "...",
  "human_problem": "...",
  "central_idea": "...",
  "angle": "...",
  "what_we_know": ["..."],
  "what_we_need_to_research": ["..."],
  "video_promise_to_viewer": "..."
}
لا تكتب أي مقدمة أو تعليق خارج الـ JSON.
"""


class UnderstandingEngine(Engine):
    name = "understanding_engine"
    stage = "topic_understanding"

    def run(self, ctx: PipelineContext, provider) -> StepResult:
        src = ctx.source
        raw = ""
        if src:
            if src.kind == "text":
                raw = src.raw_text or ""
            elif src.kind == "topic":
                raw = src.raw_text or ""
            elif src.kind == "pdf":
                raw = f"(تم إرفاق PDF من الصفحة {src.pdf_page_start} إلى {src.pdf_page_end})"

        user_prompt = f"""
اسم المشروع: {ctx.project_name}
الجمهور المستهدف: {ctx.audience}
مدة الفيديو المطلوبة بالدقائق: {ctx.duration_minutes}

المادة الخام:
\"\"\"{raw}\"\"\"
"""
        response = call_llm(
            ctx, provider, self.name, SYSTEM_PROMPT, user_prompt, allow_web_search=False
        )
        if not response.ok:
            return StepResult(ok=False, error=response.error)

        try:
            cleaned = response.text.strip().strip("```json").strip("```").strip()
            data = json.loads(cleaned)
        except Exception:
            data = {"raw_response": response.text}
            ctx.warnings.append("فهم الموضوع: تعذر تحليل الناتج كـ JSON منظم.")

        ctx.topic_understanding = data
        return StepResult(ok=True, output=data)
