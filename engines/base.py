from __future__ import annotations
from core.gemini_client import GeminiClient
from core.prompts import base_rules, compact_context
from core.skill_loader import load_skill

class Engine:
    stage = "base"
    skill_name = None
    def __init__(self, ai: GeminiClient):
        self.ai = ai

    def prompt(self, task: str, state) -> str:
        skill = load_skill(self.skill_name) if self.skill_name else ""
        return f"{base_rules()}\n\n[SKILL]\n{skill}\n\n{compact_context(state)}\n\nمهمتك الآن:\n{task}"

    def run_json(self, task: str, state, *, web: bool = False):
        return self.ai.generate_json(self.prompt(task, state), use_web=web)

    def run_text(self, task: str, state, *, web: bool = False):
        return self.ai.generate_text(self.prompt(task, state), use_web=web)
