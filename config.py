"""
config.py
---------
نقطة تجميع كل الثوابت والإعدادات العامة للمشروع.
أي ثابت يُستخدم في app.py أو في أي صفحة داخل pages/ لازم يتعرّف هنا
عشان نتجنب أخطاء ImportError زي اللي كانت بتحصل قبل كده.
"""

import os
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# هوية التطبيق
# ---------------------------------------------------------------------------
APP_TITLE = "Minds10 — Script Intelligence Platform"
APP_TAGLINE = "من الفكرة الخام إلى سكريبت يوتيوب احترافي جاهز للتسجيل"
APP_ICON = "🎬"

# ---------------------------------------------------------------------------
# مفاتيح الاتصال (تُقرأ من Environment Variables أو من st.secrets)
# لا تضع أي مفتاح هنا مباشرة. استخدم .env محليًا أو Secrets على Streamlit Cloud.
# ---------------------------------------------------------------------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_MODEL_DEEP = os.environ.get("GEMINI_MODEL_DEEP", "gemini-2.5-pro")

TURSO_DATABASE_URL = os.environ.get("TURSO_DATABASE_URL", "")
TURSO_AUTH_TOKEN = os.environ.get("TURSO_AUTH_TOKEN", "")
# لو مفيش Turso متظبط، النظام يرجع تلقائيًا لملف SQLite محلي، عشان المشروع
# يفضل شغال حتى وانت لسه مركبش قاعدة البيانات السحابية.
LOCAL_SQLITE_FALLBACK = os.environ.get("LOCAL_SQLITE_PATH", "minds10_local.db")

WEB_SEARCH_ENABLED = os.environ.get("WEB_SEARCH_ENABLED", "false").lower() == "true"
SEARCH_API_KEY = os.environ.get("SEARCH_API_KEY", "")  # اختياري (Serper / Tavily / ...الخ)

# ---------------------------------------------------------------------------
# مدة الفيديو
# ---------------------------------------------------------------------------
MIN_DURATION_MINUTES = 3
MAX_DURATION_MINUTES = 60
DEFAULT_DURATION_MINUTES = 10

# تقريب: كلمة لكل ~0.45 ثانية كلام مصري طبيعي (~135 كلمة/دقيقة تقريبًا)
WORDS_PER_MINUTE_EGYPTIAN_SPEECH = 135


def target_word_count(duration_minutes: int) -> int:
    """تحويل تقريبي من الدقائق المطلوبة إلى عدد كلمات مستهدف للسكريبت."""
    return int(duration_minutes * WORDS_PER_MINUTE_EGYPTIAN_SPEECH)


# ---------------------------------------------------------------------------
# خيارات الجمهور المستهدف (تُستخدم في واجهة اختيار الجمهور)
# ---------------------------------------------------------------------------
AUDIENCE_PRESETS = [
    "جمهور عام مهتم بتطوير الذات",
    "شباب 18-25 سنة",
    "رجال وسيدات 30-45 سنة",
    "مهتمين بالاقتصاد والمال الشخصي",
    "مبتدئين تمامًا في الموضوع",
    "متخصصين / مهتمين بعمق أكبر",
    "مخصص (اكتب وصف الجمهور بنفسك)",
]

# ---------------------------------------------------------------------------
# مراحل الـ Workflow — الترتيب ده هو مصدر الحقيقة الوحيد لترتيب الـ Pipeline.
# أي تعديل في الترتيب لازم يتم من هنا فقط، مش من جوه pipeline.py.
# ---------------------------------------------------------------------------
WORKFLOW_STAGES = [
    "input_understanding",     # فهم المدخل الخام
    "document_intelligence",   # تحليل PDF / المصادر (لو موجودة)
    "research",                # البحث
    "knowledge",                # بناء قاعدة المعرفة
    "audience",                 # لماذا يهتم المشاهد
    "strategy",                  # الزاوية والاستراتيجية (+ Retention Planning)
    "story_architecture",        # هيكل الحكاية (+ Storytelling skill)
    "hook",                       # الهوك (+ Viral Hooks skill)
    "script_writing",             # كتابة المسودة (+ Voice DNA)
    "humanization",                # Humanize skill
    "anti_slop_review",             # Stop-Slop skill
    "retention_review",              # Addictive Writing skill (مراجعة)
    "repetition_review",              # مراجعة التكرار
    "egyptian_arabic_editing",         # تحرير اللهجة (+ Dumbify عند الحاجة)
    "voice_dna_consistency_check",      # التأكد من ثبات البصمة الصوتية
    "final_human_review",                # المراجعة النهائية كمشاهد
    "final_script",                       # الإخراج النهائي
]

# ---------------------------------------------------------------------------
# إعدادات عامة أخرى
# ---------------------------------------------------------------------------
MAX_PDF_PAGES_PER_REQUEST = 40  # حماية من إرسال كتاب كامل في Context واحد
MAX_SOURCES_PER_PROJECT = 15
APP_ENV = os.environ.get("APP_ENV", "development")  # development | production


@dataclass
class RuntimeFlags:
    """أعلام تشغيل يمكن التحكم فيها من صفحة Settings وقت التشغيل."""
    web_search_enabled: bool = WEB_SEARCH_ENABLED
    deep_model_enabled: bool = False
    max_review_passes: int = 2
    allow_humanization: bool = True
    allow_anti_slop: bool = True
    allow_retention_review: bool = True


DEFAULT_RUNTIME_FLAGS = RuntimeFlags()
