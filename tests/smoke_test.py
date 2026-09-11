"""
tests/smoke_test.py
======================
اختبار شامل يشغّل الـpipeline كله من "input_intelligence" لحد
"final_script"، باستخدام FakeGeminiClient بيرجّع ردود JSON جاهزة حسب
محتوى كل System Prompt — من غير أي حاجة حقيقية من Gemini أو Turso.

الهدف: التأكد إن كل الأسلاك متوصلة صح (كل Engine بيقرأ من الـContext
الصح، وبيكتب في المكان الصح) قبل ما توصل المشروع بمفاتيح حقيقية.

تشغيل:
    python -m tests.smoke_test
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class FakeGeminiClient:
    """بيرجّع رد JSON مناسب حسب فحص محتوى الـsystem_prompt، بدون شبكة."""

    def generate(self, system_prompt: str, user_prompt: str, *, temperature: float = 0.4) -> str:
        def j(data: dict) -> str:
            return json.dumps(data, ensure_ascii=False)

        if "المشروع لا يبدأ بالكتابة" in system_prompt:
            return j({
                "surface_topic": "القرارات المالية اليومية",
                "possible_underlying_problems": ["تراكم قرارات صغيرة", "غياب وعي بالإنفاق"],
                "core_ideas": ["القرار الصغير المتكرر أقوى من القرار الكبير النادر"],
            })
        if "أنت باحث متخصص" in system_prompt:
            return j({
                "findings": [
                    {"content": "الادخار المنتظم بيقلل التوتر المالي على المدى الطويل",
                     "origin": "user_source", "relevance": "يدعم فكرة القرارات الصغيرة", "confidence": "confirmed"}
                ],
                "gaps": [],
            })
        if "أنت متخصص في فهم دوافع المشاهد" in system_prompt:
            return j({
                "pain_point": "بيشتغل بجد لكن آخر الشهر دايمًا في أزمة، ومش فاهم ليه",
                "everyday_symptom": "بيتفاجئ برصيده وهو حاسس إنه ماصرفش كتير",
            })
        if "أنت استراتيجي محتوى" in system_prompt:
            return j({
                "angle": "مستقبلك المالي بيتحدد بقرارات صغيرة متكررة مش قرار كبير واحد",
                "central_question": "ليه نفس الأزمة بترجع كل شهر؟",
                "promise_to_viewer": "هتفهم إيه القرارات الصغيرة اللي بتحدد مصيرك المالي",
                "viewer_shift": "من 'المشكلة في الدخل' لـ'المشكلة في تراكم قرارات صغيرة'",
            })
        if "أنت مهندس حكاية" in system_prompt:
            return j({
                "opening_situation": "آخر يوم في الشهر، بتفتح التطبيق وتتفاجئ إن الرصيد خلص تاني",
                "beats": [
                    {"beat": "سؤال", "content": "ليه ده بيحصل كل شهر تقريبًا؟"},
                    {"beat": "حيرة", "content": "أنا مش بصرف في حاجة كبيرة، فين المشكلة؟"},
                    {"beat": "اكتشاف", "content": "القرارات الصغيرة المتكررة هي السبب"},
                    {"beat": "تفسير", "content": "كل قرار صغير بيتراكم على مدار الشهر"},
                    {"beat": "تعقيد", "content": "مش كل قرار صغير سهل تلاحظه وانت بتاخده"},
                    {"beat": "مفاجأة", "content": "القرار الكبير النادر أقل تأثيرًا من المتكرر"},
                    {"beat": "فهم جديد", "content": "التركيز على القرارات المتكررة مش على القرار الكبير"},
                ],
            })
        if "أنت مخطط احتفاظ بالمشاهد" in system_prompt:
            return j({
                "open_loops": [{"question": "إيه هي القرارات الصغيرة دي بالظبط؟", "planned_payoff_section": "منتصف الفيديو"}],
                "re_hook_points": ["بعد الدقيقة الثالثة"],
            })
        if "أنت مراجع احتفاظ بالمشاهد" in system_prompt:
            return j({"retention_score": 8, "unresolved_loops": [], "false_suspense": [], "weak_transitions": []})
        if "أنت متخصص في هوكات" in system_prompt:
            return j({
                "hooks": [
                    {"text": "آخر يوم في الشهر، وبتتفاجئ إن الرصيد خلص... تاني. مش بتصرف في حاجة كبيرة، فين المشكلة بقى؟",
                     "why_it_works": "موقف محسوس + سؤال حقيقي", "risk": "none"}
                ],
                "recommended_index": 0,
            })
        if "أنت كاتب سكريبتات يوتيوب متخصص" in system_prompt:
            return j({"script_text": "آخر يوم في الشهر، وبتفتح التطبيق تتفاجئ إن الرصيد خلص تاني. من الجدير بالذكر أن القرارات الصغيرة بتتراكم بمرور الوقت وبتأثر في مسارك المالي."})
        if "أنسنة" in system_prompt:
            original = user_prompt.split("السكريبت المطلوب أنسنته:")[-1].split("\n\n---")[0].strip()
            return j({
                "humanized_text": original.replace("من الجدير بالذكر أن ", ""),
                "levers_applied": ["مخاطبة مباشرة", "تنويع إيقاع الجملة"],
                "change_log": [{"before": "من الجدير بالذكر أن", "after": "(حذف)", "why": "حشو رسمي"}],
            })
        if "AI Slop" in system_prompt:
            return j({
                "scores": {
                    "naturalness": {"score": 8, "reason": "طبيعي"},
                    "information_density": {"score": 7, "reason": "جيد"},
                    "clarity": {"score": 8, "reason": "واضح"},
                    "language_strength": {"score": 7, "reason": "قوي بما يكفي"},
                    "originality_low_ai_feel": {"score": 7, "reason": "مقبول"},
                },
                "issues": [],
            })
        if "أنت مراجع تكرار متخصص" in system_prompt:
            return j({"repeated_ideas": []})
        if "أنت المحرر النهائي" in system_prompt:
            script = user_prompt.split("السكريبت (بعد الأنسنة):")[-1].split("\n\n---")[0].strip()
            return j({"final_text": script, "applied_fixes_count": 0, "skipped_fixes": []})
        if "أنت محلل أسلوب كتابة" in system_prompt:
            return j({
                "traits": {"pacing": "سريع", "audience_address_style": "مباشر بصيغة إنت"},
                "notes": "بيفضّل المواقف اليومية",
            })
        if "أنت مراجع اتساق أسلوب" in system_prompt:
            return j({"consistency_score": 9, "matches": ["مخاطبة مباشرة"], "deviations": []})
        if "أنت مشاهد عادي" in system_prompt:
            return j({
                "would_keep_watching": True, "understood_from_start": True, "felt_personal": True,
                "drop_off_point": "", "promise_fulfilled": True,
                "overall_verdict": "فيديو واضح وحاسس إنه بيتكلم عني",
            })
        return "{}"


def main() -> None:
    os.environ["LOCAL_SQLITE_PATH"] = "/tmp/smoke_test.db"
    if os.path.exists("/tmp/smoke_test.db"):
        os.remove("/tmp/smoke_test.db")

    from persistence.db import Database
    from engine.models import ProjectContext, SourceItem
    from engine.pipeline import Pipeline  # استورد من engine.pipeline مباشرة، مش من engine

    db = Database()
    llm = FakeGeminiClient()
    pipeline = Pipeline(db, llm=llm)

    # المستخدم أضاف عيّنتين من كتابته القديمة قبل كده (خطوة onboarding منفصلة
    # في صفحة "Voice DNA")، عشان نختبر مسار استخراج البصمة أول مرة فعليًا.
    db.add_voice_sample("ahmed", "الناس بتفكر إن الموضوع معقد، بس هو أبسط بكتير من كده.")
    db.add_voice_sample("ahmed", "إنت مش محتاج تغيير جذري، إنت محتاج قرار صغير تكرره كل يوم.")

    ctx = ProjectContext(
        title="قرارك اليوم ممكن يغير مستقبلك المالي",
        audience="شاب في العشرينات بيشتغل ومش فاهم بيروح فين فلوسه",
        duration_minutes=8,
        writer_id="ahmed",
    )
    ctx.sources.append(SourceItem(
        id="src_1", kind="idea",
        raw_text="عايز فيديو يشرح إزاي القرارات اليومية بتأثر على المسار المالي، بطريقة بسيطة ومصرية.",
    ))

    ctx = pipeline.run_full_pipeline(ctx)

    print("== نتيجة الـpipeline ==")
    print("المرحلة الحالية:", ctx.current_stage)
    print("الهوك:", ctx.hook_text[:80])
    print("السكريبت المسودة:", ctx.draft_script[:80])
    print("السكريبت بعد الأنسنة:", ctx.humanized_script[:80])
    print("السكريبت المصري النهائي:", ctx.egyptian_final_script[:80])
    print("السكريبت النهائي:", ctx.final_script[:80])
    print("تقييم Anti-Slop:", ctx.reviews.get("anti_slop", {}).get("score"))
    print("اتساق Voice DNA:", ctx.voice_dna_consistency.get("consistency_score"))
    print("حكم المشاهد النهائي:", ctx.reviews.get("final_human", {}).get("overall_verdict"))

    assert ctx.current_stage == "final_script"
    assert ctx.final_script, "السكريبت النهائي فاضي!"
    assert "من الجدير بالذكر" not in ctx.humanized_script, "الأنسنة كان المفروض تشيل الحشو"
    assert ctx.hook_text, "الهوك فاضي!"
    assert ctx.voice_dna.traits, "Voice DNA ما اتستخرجتش رغم إنها أول مرة"

    # التأكد إن المشروع Resumable فعليًا من قاعدة البيانات
    reloaded = db.load_latest_project(ctx.project_id)
    assert reloaded.final_script == ctx.final_script
    assert reloaded.title == ctx.title
    print("\nOK: المشروع اتحفظ واترجع من قاعدة البيانات صح (Resumable) ✅")

    print("\n✅ كل مراحل الـpipeline الـ18 اشتغلت من الأول للآخر بنجاح.")


if __name__ == "__main__":
    main()
