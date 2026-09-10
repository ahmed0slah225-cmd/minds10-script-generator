"""
config.py
==========
إعدادات عامة للمشروع. القيم الحساسة (مفاتيح API) تُقرأ من
.streamlit/secrets.toml أو متغيرات البيئة - وليس من هنا.
"""

APP_TITLE = "minds10-script-generator"
APP_TAGLINE = "من فكرة خام إلى سكريبت يوتيوب مصري احترافي"

DEFAULT_DURATION_MINUTES = 10
MIN_DURATION_MINUTES = 3
MAX_DURATION_MINUTES = 60

GEMINI_MODEL = "gemini-2.0-flash"

# حد أقصى تقريبي لعدد الأحرف المستخرجة من كل مصدر نصي/PDF قبل تمريرها
# للـ Engines، عشان ما نبعتش مستندات ضخمة في كل استدعاء.
MAX_SOURCE_CHARS = 20000
