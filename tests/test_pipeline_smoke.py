"""
tests/test_pipeline_smoke.py
--------------------------------
اختبار دخان (Smoke Test): بيشغّل الـ pipeline كامل مع Gemini مُموّه
(mocked) عشان نتأكد إن الأسلاك (wiring) بين كل المراحل والـ Skills
شغالة صح، من غير ما نحتاج اتصال إنترنت فعلي أو مفتاح API حقيقي.
"""

import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("GEMINI_API_KEY", "test-key")
os.environ.setdefault("LOCAL_SQLITE_PATH", "/tmp/minds10_test.db")

from engine.models import Project  # noqa: E402
from engine import pipeline  # noqa: E402


def fake_generate(prompt, system_instruction=None, deep=False, temperature=0.8, max_retries=3):
    return "نص تجريبي تم توليده أثناء الاختبار — " + prompt[:30].replace("\n", " ")


def fake_generate_json(prompt, system_instruction=None, deep=False, temperature=0.4):
    if "hooks" in prompt:
        return {"hooks": [{"text": "هوك تجريبي 1", "type": "موقف يومي", "why_it_works": "..."}]}
    if "items" in prompt:
        return {"items": [{"claim": "فكرة تجريبية", "evidence": "دليل", "source_ref": "مصدر تجريبي",
                            "confidence": "موثق", "usable_in_script": True}]}
    if "scores" in prompt:
        return {"scores": {"naturalness": 8, "information_density": 7, "clarity": 8,
                            "language_strength": 7, "originality_low_ai_feel": 8},
                "total_out_of_50": 38, "needs_revision": False, "issues": []}
    if "open_questions_without_payoff" in prompt:
        return {"open_questions_without_payoff": [], "false_suspense_lines": [],
                "weak_transitions": [], "suggested_rehook_points": [], "overall_retention_note": "تمام"}
    if "lazy_repetitions" in prompt:
        return {"lazy_repetitions": [], "useful_repetitions_kept": []}
    if "consistent" in prompt:
        return {"consistent": True, "drift_points": []}
    if "overall_verdict" in prompt:
        return {"did_i_understand": "أيوه", "was_i_interested": "أيوه", "did_it_feel_about_me": "أيوه",
                "where_would_i_leave": "محدش مكان واضح", "was_the_ending_worth_it": "أيوه",
                "was_the_opening_promise_fulfilled": True, "overall_verdict": "جاهز للتسجيل"}
    return {}


@patch("engine.gemini_client.generate", side_effect=fake_generate)
@patch("engine.gemini_client.generate_json", side_effect=fake_generate_json)
def test_full_pipeline_runs_end_to_end(mock_json, mock_gen):
    project = Project(
        title="اختبار الـ Pipeline",
        original_request="عايز فيديو عن التسويف",
        audience="جمهور عام مهتم بتطوير الذات",
        duration_minutes=8,
    )

    project = pipeline.run_input_understanding(project)
    assert project.topic_understanding

    project = pipeline.run_research(project, sources_text="", web_search_allowed=False)
    assert project.research_notes

    project = pipeline.run_knowledge(project)
    assert isinstance(project.knowledge_base, list) and len(project.knowledge_base) >= 1

    project = pipeline.run_audience(project)
    assert project.audience_insight

    project = pipeline.run_strategy(project)
    assert project.strategy

    project = pipeline.run_story(project)
    assert project.story_architecture

    project = pipeline.run_hook(project)
    assert project.hook_options and project.chosen_hook

    project = pipeline.run_script_writing(project)
    assert project.draft_script

    project = pipeline.run_humanization(project)
    assert project.humanized_script

    project = pipeline.run_anti_slop_review(project)
    assert "needs_revision" in project.anti_slop_report

    project = pipeline.run_retention_review(project)
    assert "overall_retention_note" in project.retention_report

    project = pipeline.run_repetition_review(project)
    assert "lazy_repetitions" in project.repetition_report

    project = pipeline.run_egyptian_arabic_editing(project)
    assert project.egyptian_edited_script

    project = pipeline.run_voice_dna_consistency_check(project)
    assert project.voice_consistency_report["consistent"] is True

    project = pipeline.run_final_human_review(project)
    assert project.final_review_notes

    project = pipeline.run_final_script(project)
    assert project.final_script
    assert project.status == "completed"
    assert len(project.stage_log) == len(pipeline.FULL_ORDER)

    print("✅ Pipeline full run OK — stages executed:", [s["stage"] for s in project.stage_log])
