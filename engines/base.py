"""
engines/base.py
=================
كل Engine في المشروع (Topic Understanding, Research, Strategy...) بيرث من
BaseEngine. الهدف: كل Engine له اسم، ودور (persona) بيتبعت كـ system
instruction لـ Gemini، وواجهة موحدة run(context) -> context.

كل Engine:
- يقرأ من الـ ProjectContext اللي محتاجه بس.
- يكتب نتيجته في الحقل المخصص له فقط.
- ما يلمسش حقول Engines تانية.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.context import ProjectContext
from llm.gemini_client import generate, generate_json


class BaseEngine(ABC):
    name: str = "base_engine"
    persona: str = "أنت مساعد ذكاء اصطناعي عام."

    def call(self, user_prompt: str, *, json_mode: bool = False, temperature: float = 0.8):
        if json_mode:
            return generate_json(self.persona, user_prompt, temperature=temperature)
        return generate(self.persona, user_prompt, temperature=temperature)

    @abstractmethod
    def run(self, ctx: ProjectContext) -> ProjectContext:
        ...

    def run_and_mark(self, ctx: ProjectContext) -> ProjectContext:
        ctx.current_stage = self.name
        ctx = self.run(ctx)
        ctx.mark_stage_done(self.name)
        return ctx
