"""
engine/pipeline.py
=====================
الأوركستريتور المركزي. بيشغّل كل الـEngines بالترتيب الرسمي المتفق عليه
(نفس ترتيب config.WORKFLOW_STAGES بالظبط)، وبيحفظ Snapshot في قاعدة
البيانات بعد كل مرحلة — عشان المشروع يبقى Resumable فعليًا: لو حصل أي
خطأ أو المستخدم قفل المتصفح، يقدر يرجع لآخر مرحلة اتحفظت بالظبط.

فيه طريقتين للتشغيل:
1) run_full_pipeline(): يشغّل كل المراحل ورا بعض من البداية للنهاية.
2) run_stage(): يشغّل مرحلة واحدة بس — ده اللي بتستخدمه واجهة Streamlit
   عشان تدي المستخدم تحكم مرحلة بمرحلة، ويقدر يوقف ويكمل بعدين.
"""

from __future__ import annotations

from typing import Callable, Optional

from config import WEB_RESEARCH_ENABLED_DEFAULT, WORKFLOW_STAGES
from engine.audience_engine import AudienceEngine
from engine.editor_engine import EditorEngine
from engine.final_review_engine import FinalReviewEngine
from engine.gemini_client import GeminiClient
from engine.hook_engine import HookEngine
from engine.humanization_engine import HumanizationEngine
from engine.knowledge_engine import KnowledgeEngine
from engine.models import ProjectContext
from engine.research_engine import ResearchEngine
from engine.retention_engine import RetentionEngine
from engine.review_engine import ReviewEngine
from engine.script_engine import ScriptEngine
from engine.story_engine import StoryEngine
from engine.strategy_engine import StrategyEngine
from engine.topic_engine import TopicEngine
from engine.voice_engine import VoiceEngine
from persistence.db import Database


class Pipeline:
    def __init__(
        self,
        db: Database,
        llm: Optional[GeminiClient] = None,
        web_search_fn: Optional[Callable[[str], list[dict]]] = None,
        web_research_enabled: bool = WEB_RESEARCH_ENABLED_DEFAULT,
    ):
        self.db = db
        llm = llm or GeminiClient()
        self.web_research_enabled = web_research_enabled

        self.voice_engine = VoiceEngine(db, llm)
        self.topic_engine = TopicEngine(llm)
        self.research_engine = ResearchEngine(llm, web_search_fn=web_search_fn)
        self.knowledge_engine = KnowledgeEngine()
        self.audience_engine = AudienceEngine(llm)
        self.strategy_engine = StrategyEngine(llm)
        self.story_engine = StoryEngine(llm)
        self.retention_engine = RetentionEngine(llm)
        self.hook_engine = HookEngine(llm)
        self.script_engine = ScriptEngine(llm)
        self.humanization_engine = HumanizationEngine(llm)
        self.review_engine = ReviewEngine(llm)
        self.editor_engine = EditorEngine(llm)
        self.final_review_engine = FinalReviewEngine(llm)

        # خريطة اسم المرحلة -> الدالة المسؤولة عنها، بنفس ترتيب
        # config.WORKFLOW_STAGES بالظبط.
        self._stage_runners: dict[str, Callable[[ProjectContext], ProjectContext]] = {
            "input_intelligence": self.voice_engine.load_or_extract,
            "topic_understanding": self.topic_engine.run,
            "research": lambda ctx: self.research_engine.run(ctx, self.web_research_enabled),
            "knowledge": self.knowledge_engine.run,
            "audience": self.audience_engine.run,
            "strategy": self.strategy_engine.run,
            "story_architecture": self.story_engine.run,
            "retention_planning": self.retention_engine.plan,
            "hook": self.hook_engine.run,
            "script_writing": self.script_engine.run,
            "humanization": self.humanization_engine.run,
            "anti_slop_review": self._run_anti_slop_and_repetition,
            "repetition_review": self._noop,  # اتنفذت بالفعل داخل anti_slop_review
            "retention_review": self._run_retention_review_and_edit,
            "egyptian_arabic_editing": self._noop,  # اتنفذت بالفعل داخل retention_review
            "voice_dna_consistency_check": self._run_voice_consistency,
            "final_human_review": self.final_review_engine.run,
            "final_script": self._noop,  # اتنفذت بالفعل داخل final_human_review
        }
        self._retention_review_cache: dict = {}

    # -- مراحل مركّبة (لتفادي نداء Gemini إضافي بلا داعي) -----------------
    def _run_anti_slop_and_repetition(self, ctx: ProjectContext) -> ProjectContext:
        return self.review_engine.run_all(ctx, ctx.humanized_script)

    def _run_retention_review_and_edit(self, ctx: ProjectContext) -> ProjectContext:
        retention_result = self.retention_engine.review(ctx, ctx.humanized_script)
        ctx = self.editor_engine.run(ctx, retention_result)
        ctx.touch("retention_review")
        return ctx

    def _run_voice_consistency(self, ctx: ProjectContext) -> ProjectContext:
        consistency = self.voice_engine.consistency_check(ctx, ctx.egyptian_final_script)
        ctx.voice_dna_consistency = consistency
        ctx.touch("voice_dna_consistency_check")
        return ctx

    @staticmethod
    def _noop(ctx: ProjectContext) -> ProjectContext:
        return ctx

    # -- تشغيل مرحلة واحدة (Resumable) -------------------------------------
    def run_stage(self, ctx: ProjectContext, stage: str) -> ProjectContext:
        if stage not in self._stage_runners:
            raise ValueError(f"مرحلة غير معروفة: {stage}")
        ctx = self._stage_runners[stage](ctx)
        self.db.save_project_snapshot(ctx)
        return ctx

    # -- تشغيل كل الـWorkflow ورا بعض ---------------------------------------
    def run_full_pipeline(self, ctx: ProjectContext, start_from: Optional[str] = None) -> ProjectContext:
        stages = WORKFLOW_STAGES
        if start_from:
            idx = stages.index(start_from)
            stages = stages[idx:]
        for stage in stages:
            ctx = self.run_stage(ctx, stage)
        return ctx
