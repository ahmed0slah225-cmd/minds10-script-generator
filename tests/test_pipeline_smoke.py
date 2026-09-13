import tempfile
import unittest
from pathlib import Path

from core.context import PipelineContext
from core.llm_provider import LLMResult, RetryableLLMError
from core.models import ProjectSettings
from core.orchestrator import Orchestrator
from core.pipeline import new_project
from core.storage import ProjectStore


class FakeLLM:
    """Deterministic fake provider for end-to-end pipeline tests."""

    def __init__(self):
        self.calls = 0
        self.outputs = [
            {  # topic
                "topic": "موضوع تجريبي",
                "human_problem": "مشكلة بشرية واضحة",
                "central_question": "ليه ده بيحصل؟",
                "central_idea": "فكرة مركزية",
                "angle": "زاوية مفهومة",
                "promise": "وعد واضح",
                "known": [],
                "needs_verification": [],
                "sensitive_claims": [],
                "objections": [],
            },
            {  # source analysis
                "claims": [],
                "quotes": [],
                "stories": [],
                "examples": [],
            },
            [  # knowledge: deliberately return a top-level array + alias keys
                {
                    "type": "fact",
                    "content": "حقيقة تجريبية",
                    "provenance": "web_source",
                    "source_ids": [],
                    "confidence": 0.9,
                    "verified": True,
                }
            ],
            {"knowledge_level": "general", "pain": "pain", "objections": [], "language": "ar-EG"},  # audience
            {"central_promise": "وعد", "central_question": "سؤال", "angle": "زاوية", "argument_spine": [], "discoveries": [], "evidence_placement": [], "story_placement": [], "objections": [], "ending": "خاتمة"},  # strategy
            {"situation": "موقف", "question": "سؤال", "tension": "توتر", "discovery": "اكتشاف", "explanation": "شرح", "complication": "تعقيد", "insight": "استبصار", "payoff": "مكافأة"},  # story
            {"promise": "وعد", "central_question": "سؤال", "section_order": [], "transitions": [], "re_hooks": [], "payoffs": [], "ending": "نهاية"},  # retention
            [  # hook: deliberately return a top-level array
                {"text": "تخيل إن المشكلة دي بتحصل معاك كل يوم.", "type": "question", "specificity": 9, "stakes": 8}
            ],
            {"script": "إنت ممكن تكون بتعمل ده كل يوم من غير ما تاخد بالك. ودي مسودة اختبارية طويلة بما يكفي للفحص."},  # script
            "إنت ممكن تكون بتعمل ده كل يوم من غير ما تاخد بالك. ودي نسخة أنعم في النطق.",  # humanize
            {  # anti-slop review: missing dimension on purpose
                "passed": True,
                "scores": {"naturalness": 8, "clarity": 8, "ai_feel": 8},
                "issues": [
                    {"category": "clarity", "location": "فقرة 1", "problem": "مشكلة اختبار", "reason": "سبب اختبار", "suggested_fix": "إصلاح اختبار", "priority": 2}
                ],
                "summary": "مراجعة اختبارية",
            },
            {"repeated": [], "summary": "لا يوجد تكرار مهم."},  # repetition
            "إنت ممكن تكون بتعمل ده كل يوم من غير ما تاخد بالك. ودي نسخة مصرية طبيعية.",  # egyptian
            {"scores": {"voice_match": 8}, "deviations": []},  # voice
            {"claims": []},  # truth
            "إنت ممكن تكون بتعمل ده كل يوم من غير ما تاخد بالك. ودي النسخة النهائية للاختبار.",  # final editor
        ]

    def generate(self, *args, **kwargs):
        if self.calls >= len(self.outputs):
            raise AssertionError("FakeLLM received more calls than expected")
        payload = self.outputs[self.calls]
        self.calls += 1
        if isinstance(payload, str):
            text = payload
        else:
            import json
            text = json.dumps(payload, ensure_ascii=False)
        return LLMResult(text=text, model_id="fake-model", run_id=f"fake-{self.calls}", elapsed_ms=0)


class RetryOnceFakeLLM(FakeLLM):
    """Fails once with a retryable error before allowing the first stage to succeed."""

    def __init__(self):
        super().__init__()
        self.failed_once = False

    def generate(self, *args, **kwargs):
        if not self.failed_once:
            self.failed_once = True
            raise RetryableLLMError("temporary service outage")
        return super().generate(*args, **kwargs)


class PipelineSmokeTests(unittest.TestCase):
    def test_full_pipeline_without_external_api(self):
        settings = ProjectSettings(
            name="smoke-test",
            duration_minutes=5,
            model_label="Gemini 3.8 Flash",
            web_research=False,
        )
        ctx = new_project("موضوع تجريبي", settings)
        fake = FakeLLM()
        ctx = Orchestrator(fake).run(ctx, retry_delay=0, max_auto_retries=0)

        self.assertEqual(fake.calls, 16)
        self.assertTrue(ctx.state.final_script.strip())
        self.assertTrue(ctx.state.strategy)
        self.assertTrue(ctx.state.hook_set)
        self.assertEqual(len(ctx.state.knowledge), 1)
        self.assertEqual(ctx.state.knowledge[0].kind, "fact")
        self.assertEqual(ctx.state.knowledge[0].text, "حقيقة تجريبية")
        self.assertEqual(ctx.state.knowledge[0].provenance, "web_research")
        self.assertEqual(ctx.state.reviews[0].issues[0].dimension, "clarity")
        self.assertTrue(ctx.state.metadata["final_gate"]["passed"])
        self.assertEqual(ctx.state.metadata["resume_stage_index"], 18)
        self.assertEqual(sum(1 for x in ctx.trace if x.get("status") == "ok"), 18)

    def test_transient_error_retries_same_stage(self):
        settings = ProjectSettings(name="retry-test", duration_minutes=5, model_label="Gemini 3.6 Flash")
        ctx = new_project("موضوع تجريبي", settings)
        fake = RetryOnceFakeLLM()

        ctx = Orchestrator(fake).run(ctx, retry_delay=0, max_auto_retries=1)

        self.assertEqual(fake.calls, 16)
        self.assertEqual(ctx.state.metadata["resume_stage_index"], 18)
        topic_attempts = [x for x in ctx.trace if x.get("stage") == "topic_understanding"]
        self.assertTrue(any(x.get("status") == "error" and x.get("retryable") is True for x in topic_attempts))
        self.assertTrue(any(x.get("status") == "ok" and x.get("attempt") == 2 for x in topic_attempts))

    def test_local_store_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "minds.db"
            store = ProjectStore(str(db_path))
            settings = ProjectSettings(name="storage-test", model_label="Gemini 3.8 Flash")
            ctx = new_project("storage test", settings)
            ctx.state.final_script = "script"
            ctx.state.metadata["resume_stage_index"] = 12
            ctx.state.metadata["trace"] = [{"stage": "topic_understanding", "status": "ok"}]
            store.save_project(ctx.state)
            loaded = store.load_project(ctx.state.project_id)
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded.project_id, ctx.state.project_id)
            self.assertEqual(loaded.final_script, "script")
            restored_ctx = PipelineContext(loaded)
            self.assertEqual(restored_ctx.trace[0]["stage"], "topic_understanding")
            self.assertEqual(loaded.metadata["resume_stage_index"], 12)

    def test_stage_graph_matches_architecture(self):
        names = []
        for stage in Orchestrator(FakeLLM()).stages:
            names.append(getattr(stage, "name", getattr(stage, "__name__", "stage")))
        expected = [
            "input_router", "topic_understanding", "source_analysis", "research",
            "knowledge", "audience", "strategy", "story", "retention", "hook",
            "script", "humanize", "anti_slop_review", "repetition_review",
            "egyptian_editor", "voice_check", "truth_check", "final_editor",
        ]
        self.assertEqual(names, expected)


if __name__ == "__main__":
    unittest.main()
