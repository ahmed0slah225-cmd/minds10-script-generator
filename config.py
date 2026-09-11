"""
config.py
==========
ملف الإعدادات المركزي الوحيد للمشروع.

القاعدة الذهبية: أي ثابت (Constant) يُستخدم في أكتر من ملف لازم يتعرّف
هنا مرة واحدة بس، وميتكررش تعريفه في مكان تاني. ده بالظبط اللي بيمنع
مشكلة زي:

    ImportError: cannot import name 'MAX_DURATION_MINUTES' from 'config'

لأن أي اسم هتستورده في app.py أو أي صفحة، لازم يكون معرّف هنا بالظبط
بنفس الاسم. لو ضفت متغير جديد في أي مكان في المشروع وبتستورده من config،
تأكد إنك ضفته هنا الأول.
"""

from __future__ import annotations

import os

# ---------------------------------------------------------------------------
# هوية التطبيق
# ---------------------------------------------------------------------------
APP_TITLE = "Minds10"
APP_TAGLINE = "من أي فكرة أو مصدر... لسكريبت يوتيوب احترافي بالمصري"
APP_ICON = "🎬"

# ---------------------------------------------------------------------------
# مدة الفيديو (بالدقائق) — المستخدم يختار من ضمن النطاق ده
# ---------------------------------------------------------------------------
MIN_DURATION_MINUTES = 3
MAX_DURATION_MINUTES = 45
DEFAULT_DURATION_MINUTES = 10

DURATION_PRESETS = [5, 10, 15, 20, 30, 45]

# ---------------------------------------------------------------------------
# حدود الـPDF (نصي فقط، بدون OCR في هذه النسخة)
# ---------------------------------------------------------------------------
MAX_PDF_SIZE_MB = 50
MAX_PDF_PAGES_PER_REQUEST = 40  # أقصى عدد صفحات تُستخرج في نطاق واحد

# ---------------------------------------------------------------------------
# نموذج Gemini
# ---------------------------------------------------------------------------
# ملحوظة مهمة (سبتمبر 2026): Gemini 2.0 Flash اتقفل نهائيًا في يونيو 2026،
# وGemini 2.5 Pro هيتقفل في أكتوبر 2026. النماذج بتتغيّر بسرعة، فاتأكد
# دايمًا من القائمة الحالية على:
# https://ai.google.dev/gemini-api/docs/models
# قبل ما تعتمد على الاسم ده، وغيّره وقتها بمتغير بيئة GEMINI_MODEL_NAME
# من غير ما تلمس الكود.
GEMINI_MODEL_NAME = os.environ.get("GEMINI_MODEL_NAME", "gemini-3.6-flash")
GEMINI_TEMPERATURE_DEFAULT = 0.5

# ---------------------------------------------------------------------------
# البحث على الويب
# ---------------------------------------------------------------------------
WEB_RESEARCH_ENABLED_DEFAULT = False  # المستخدم يفعّلها يدويًا من الإعدادات
MAX_WEB_SOURCES_PER_RESEARCH_RUN = 6

# ---------------------------------------------------------------------------
# قاعدة البيانات (Turso / SQLite محليًا)
# ---------------------------------------------------------------------------
# لو TURSO_DATABASE_URL موجود -> يشتغل على Turso الحقيقي.
# لو مش موجود -> يشتغل تلقائيًا على SQLite محلي (local.db) للتطوير والاختبار
# من غير ما تحتاج حساب Turso فعلي وانت لسه بتبني.
TURSO_DATABASE_URL = os.environ.get("TURSO_DATABASE_URL", "")
TURSO_AUTH_TOKEN = os.environ.get("TURSO_AUTH_TOKEN", "")
LOCAL_SQLITE_PATH = os.environ.get("LOCAL_SQLITE_PATH", "local.db")

# ---------------------------------------------------------------------------
# مراحل الـWorkflow (بالترتيب الرسمي المعتمد للمشروع)
# ---------------------------------------------------------------------------
WORKFLOW_STAGES = [
    "input_intelligence",
    "topic_understanding",
    "research",
    "knowledge",
    "audience",
    "strategy",
    "story_architecture",
    "retention_planning",
    "hook",
    "script_writing",
    "humanization",
    "anti_slop_review",
    "retention_review",
    "repetition_review",
    "egyptian_arabic_editing",
    "voice_dna_consistency_check",
    "final_human_review",
    "final_script",
]

STAGE_LABELS_AR = {
    "input_intelligence": "فهم المدخل",
    "topic_understanding": "فهم الموضوع",
    "research": "البحث",
    "knowledge": "بناء المعرفة",
    "audience": "ليه المشاهد يهتم",
    "strategy": "الاستراتيجية",
    "story_architecture": "بناء الحكاية",
    "retention_planning": "تخطيط الاحتفاظ بالمشاهد",
    "hook": "الهوك",
    "script_writing": "كتابة السكريبت",
    "humanization": "الأنسنة",
    "anti_slop_review": "مراجعة الحشو والـAI Slop",
    "retention_review": "مراجعة الاحتفاظ بالمشاهد",
    "repetition_review": "مراجعة التكرار",
    "egyptian_arabic_editing": "التحرير المصري النهائي",
    "voice_dna_consistency_check": "فحص اتساق بصمة الكاتب",
    "final_human_review": "المراجعة النهائية كمشاهد",
    "final_script": "السكريبت النهائي",
}
