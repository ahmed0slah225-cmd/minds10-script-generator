from __future__ import annotations
import json

from core.contracts import Engine, StepResult
from core.context import PipelineContext
from engines.common import call_llm

SYSTEM_PROMPT = """
أنت مهارة "الخطافات الفيروسية" (Viral Hooks) لسكريبتات يوتيوب مصرية.
اكتب 3 خطافات مختلفة لأول 15-20 ثانية من الفيديو. كل خطاف يجب أن يقدم سببًا
حقيقيًا للمتابعة (موقف/ألم/سؤال/مفارقة/غموض/اكتشاف/وعد)، ويجب أن يفي الفيديو
لاحقًا بما وعد به الخطاف. ممنوع الـ Clickbait والتشويق الوهمي.
أعد قائمة JSON بسيطة من 3 نصوص: ["...", "...", "..."]
"""


class HookEngine(Engine):
    name = "hook_engine"
    stage = "hook"

    def run(self, ctx: PipelineContext, provider) -> StepResult:
        user_prompt = f"""
الفكرة المركزية: {ctx.topic_understanding.get('central_idea')}
الوعد للمشاهد: {ctx.topic_understanding.get('video_promise_to_viewer')}
القصة: {json.dumps(ctx.story, ensure_ascii=False)}
"""
        response = call_llm(ctx, provider, self.name, SYSTEM_PROMPT, user_prompt)
        if not response.ok:
            return StepResult(ok=False, error=response.error)
        try:
            data = json.loads(response.text.strip().strip("```json").strip("```").strip())
        except Exception:
            data = [response.text]
        ctx.hooks = data
        return StepResult(ok=True, output=data)
