"""
engine/engines/editor.py
----------------------------
الغرفة كلها بتتجمع هنا. الـ Editor لا يخترع أفكار جديدة — بياخد النص
بعد الإنسنة، وتقارير anti_slop / retention / repetition / voice
consistency، ويطبّق التعديلات المطلوبة فعليًا في نسخة واحدة نهائية.
لو الجمهور مبتدئ تمامًا، يطبّق مهارة dumbify كخطوة إضافية اختيارية.
"""

from typing import Optional
from engine import gemini_client
from engine.skills.loader import load_skill

EDITOR_SYSTEM = (
    "إنت المحرر النهائي داخل نظام Minds10. مهمتك دمج نتائج المراجعات "
    "المختلفة في نسخة واحدة نهائية بالعامية المصرية، جاهزة للتسجيل. "
    "لا تضيف أفكار أو معلومات جديدة — فقط طبّق التعديلات المطلوبة من "
    "التقارير. حافظ على الحقائق والمصادر والفكرة الأساسية كما هي."
)


def apply_editorial_pass(
    humanized_script: str,
    anti_slop_report: dict,
    retention_report: dict,
    repetition_report: dict,
    voice_consistency_report: dict,
    simplify_for_beginners: bool = False,
) -> str:
    dumbify_section = ""
    if simplify_for_beginners:
        dumbify_skill = load_skill("dumbify")
        dumbify_section = f"""
--- مهارة التبسيط للمبتدئين (طبّقها بعد التعديلات الأساسية) ---
{dumbify_skill}
---
"""
    prompt = f"""
النص بعد الإنسنة:
\"\"\"{humanized_script}\"\"\"

تقرير كشف الـ AI Slop:
{anti_slop_report}

تقرير مراجعة الاحتفاظ بالمشاهد:
{retention_report}

تقرير مراجعة التكرار:
{repetition_report}

تقرير اتساق البصمة الصوتية:
{voice_consistency_report}

{dumbify_section}

المطلوب: طبّق التعديلات المطلوبة من التقارير أعلاه (لو needs_revision=true
في تقرير الـ Slop، أو فيه lazy_repetitions، أو drift_points في البصمة
الصوتية)، وأخرج النسخة النهائية الكاملة للسكريبت بالعامية المصرية، جاهزة
للتسجيل مباشرة قدام الكاميرا. لا تخرج أي تعليق أو شرح، فقط نص السكريبت
النهائي.
"""
    return gemini_client.generate(prompt, system_instruction=EDITOR_SYSTEM, temperature=0.4)
