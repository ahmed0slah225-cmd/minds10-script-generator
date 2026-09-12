"""
core/pipeline.py
=================
المنسق (Orchestrator). يشغّل المراحل بالترتيب الموصوف في المواصفات (بند 42):
فهم → بحث → معرفة → جمهور → استراتيجية → قصة → هوك → سكريبت → أنسنة →
مكافحة انزلاق + احتفاظ → تحرير نهائي → النص النهائي.

بوابة جودة بسيطة (بند 57): إذا فشلت مرحلة أساسية (فهم/سكريبت)، نتوقف فورًا
بدل الاستمرار بمعطيات ناقصة. المراحل غير الحرجة (بحث، احتفاظ) تسجّل تحذيرًا
وتكمل.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any

from core.context import PipelineContext
from providers.base import LLMProvider

from engines.understanding_engine import UnderstandingEngine
from engines.research_engine import ResearchEngine
from engines.knowledge_engine import KnowledgeEngine
from engines.audience_engine import AudienceEngine
from engines.strategy_engine import StrategyEngine
from engines.story_engine import StoryEngine
from engines.hook_engine import HookEngine
from engines.script_engine import ScriptEngine
from engines.editor_engine import EditorEngine

from skills.voice_dna_ar_eg import VoiceDNASkill
from skills.humanize_ar_eg import HumanizeSkill
from skills.anti_slop_ar_eg import AntiSlopSkill
from skills.retention_ar_eg import RetentionSkill


@dataclass
class StageOutcome:
    stage_name: str
    ok: bool
    critical: bool
    warnings: List[str] = field(default_factory=list)
    error: str = ""


class ScriptPipeline:
    CRITICAL_STAGES = {"understanding_engine", "script_engine"}

    def __init__(self):
        self.understanding = UnderstandingEngine()
        self.voice_dna = VoiceDNASkill()
        self.research = ResearchEngine()
        self.knowledge = KnowledgeEngine()
        self.audience = AudienceEngine()
        self.strategy = StrategyEngine()
        self.story = StoryEngine()
        self.hook = HookEngine()
        self.script = ScriptEngine()
        self.humanize = HumanizeSkill()
        self.anti_slop = AntiSlopSkill()
        self.retention = RetentionSkill()
        self.editor = EditorEngine()

    def run(self, ctx: PipelineContext, provider: LLMProvider, progress_cb=None) -> List[StageOutcome]:
        outcomes: List[StageOutcome] = []

        def step(label_ar: str, engine_name: str, fn, critical: bool):
            if progress_cb:
                progress_cb(label_ar)
            result = fn()
            outcome = StageOutcome(
                stage_name=engine_name,
                ok=result.ok,
                critical=critical,
                warnings=result.warnings,
                error=result.error or "",
            )
            outcomes.append(outcome)
            return outcome

        o = step("فهم الموضوع...", "understanding_engine", lambda: self.understanding.run(ctx, provider), True)
        if not o.ok:
            return outcomes  # بوابة جودة: لا نكمل بدون فهم صحيح

        step("استخراج الحمض النووي الصوتي...", "voice_dna_ar_eg", lambda: self.voice_dna.run(ctx, provider), False)
        step("البحث (إن كان مفعّلاً)...", "research_engine", lambda: self._merge_research(ctx, provider), False)
        step("بناء قاعدة المعرفة...", "knowledge_engine", lambda: self.knowledge.run(ctx, provider), False)
        step("تحليل الجمهور...", "audience_engine", lambda: self.audience.run(ctx, provider), False)
        step("بناء الاستراتيجية...", "strategy_engine", lambda: self.strategy.run(ctx, provider), False)
        step("بناء القصة...", "story_engine", lambda: self.story.run(ctx, provider), False)
        step("توليد الخطافات...", "hook_engine", lambda: self.hook.run(ctx, provider), False)

        o = step("كتابة المسودة...", "script_engine", lambda: self.script.run(ctx, provider), True)
        if not o.ok:
            return outcomes

        step("الأنسنة...", "humanize_ar_eg", lambda: self.humanize.run(ctx, provider), False)
        step("مراجعة مكافحة الانزلاق...", "anti_slop_ar_eg", lambda: self.anti_slop.run(ctx, provider), False)
        step("مراجعة الاحتفاظ...", "retention_ar_eg", lambda: self.retention.run(ctx, provider), False)
        step("التحرير النهائي...", "editor_engine", lambda: self.editor.run(ctx, provider), False)

        if not ctx.final_script:
            ctx.final_script = ctx.humanized_script or ctx.draft_script

        return outcomes

    def _merge_research(self, ctx: PipelineContext, provider):
        result = self.research.run(ctx, provider)
        if result.ok and result.output:
            ctx.knowledge_base.extend(result.output)
        return result
