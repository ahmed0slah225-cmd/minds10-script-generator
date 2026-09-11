from __future__ import annotations
from engines.input_intelligence import InputIntelligenceEngine
from engines.research import ResearchEngine
from engines.knowledge import KnowledgeEngine
from engines.audience_strategy import AudienceStrategyEngine
from engines.story import StoryEngine
from engines.retention import RetentionEngine
from engines.hook import HookEngine
from engines.script import ScriptEngine
from engines.humanization import HumanizationEngine
from engines.reviews import ReviewEngine
from engines.editor import EditorEngine
from engines.final_review import FinalHumanReviewEngine

class Pipeline:
    def __init__(self, ai):
        self.ai = ai
        self.steps = [
            InputIntelligenceEngine(ai), ResearchEngine(ai), KnowledgeEngine(ai),
            AudienceStrategyEngine(ai), StoryEngine(ai), RetentionEngine(ai),
            HookEngine(ai), ScriptEngine(ai), HumanizationEngine(ai), ReviewEngine(ai), FinalHumanReviewEngine(ai), EditorEngine(ai)
        ]

    def run(self, state, *, use_web=True, progress=None, on_stage=None, resume=True):
        completed = set(state.stage_outputs.keys()) if resume else set()
        for i, step in enumerate(self.steps):
            if step.stage in completed:
                if progress:
                    progress((i + 1) / len(self.steps), f"تجاوزنا {step.stage} لأنها محفوظة")
                continue
            if progress:
                progress(i / len(self.steps), step.stage)
            if step.stage == "research":
                step.run(state, use_web=use_web)
            else:
                step.run(state)
            state.project.current_stage = step.stage
            state.stage_outputs[step.stage] = self._snapshot(step, state)
            if on_stage:
                on_stage(state, step.stage)
            if progress:
                progress((i+1) / len(self.steps), step.stage)
        return state

    @staticmethod
    def _snapshot(step, state):
        name = step.stage
        if name == "input_understanding": return state.topic
        if name == "research": return state.research
        if name == "knowledge": return state.knowledge
        if name == "strategy": return state.strategy
        if name == "story": return state.story
        if name == "retention": return state.retention
        if name == "hook": return state.hook
        if name == "script": return state.script
        if name == "humanization": return state.humanized_script
        if name == "reviews": return state.anti_slop
        if name == "final_review": return state.final_review
        if name == "final_edit": return state.final_script
        return None
