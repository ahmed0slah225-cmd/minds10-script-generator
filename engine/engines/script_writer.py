"""
engine/engines/script_writer.py
-----------------------------------
هنا فقط تبدأ الكتابة الفعلية — بعد ما الموضوع والبحث والمعرفة
والاستراتيجية والحكاية والهوك كلهم جاهزين. الكاتب هنا لا "يفكر" من
الصفر، هو يستلم كل حاجة ويكتب.

بعد المسودة، بيتم تطبيق مهارة humanize_ar_eg كتحسين لاحق، مش كتابة من
جديد.
"""

from typing import Optional
from engine import gemini_client
from engine.skills.loader import load_skill
from engine.models import VoiceProfile
from config import target_word_count

SYSTEM = (
    "إنت كاتب سكريبتات يوتيوب بالعامية المصرية داخل نظام Minds10. "
    "بتكتب سكريبت جاهز للتسجيل قدام الكاميرا، مش مقال. الجمل لازم تكون "
    "قابلة للنطق بصوت طبيعي. لا تخترع معلومات أو مصادر أو أرقام غير "
    "موجودة في قاعدة المعرفة المزودة لك."
)


def _voice_context(voice_profile: Optional[VoiceProfile]) -> str:
    if not voice_profile:
        return "لا توجد بصمة صوتية محفوظة — استخدم عامية مصرية طبيعية، جمل متنوعة الطول، بدون رسمية زايدة."
    return voice_profile.raw_traits_summary or "بصمة محفوظة بدون ملخص نصي متاح."


def write_draft(
    chosen_hook: str,
    story_architecture: str,
    strategy: str,
    knowledge_summary: str,
    duration_minutes: int,
    audience: str,
    voice_profile: Optional[VoiceProfile] = None,
) -> str:
    words_target = target_word_count(duration_minutes)
    prompt = f"""
الهوك المختار (ابدأ الفيديو بيه بالظبط أو بتصرف بسيط جدًا):
\"\"\"{chosen_hook}\"\"\"

الهيكل الحكائي المطلوب اتباعه:
\"\"\"{story_architecture}\"\"\"

الاستراتيجية العامة:
\"\"\"{strategy}\"\"\"

قاعدة المعرفة المتاحة (استخدمها فقط، لا تخترع غيرها):
\"\"\"{knowledge_summary}\"\"\"

الجمهور: {audience}
مدة الفيديو: {duration_minutes} دقيقة (استهدف حوالي {words_target} كلمة تقريبًا)

بصمة الكاتب الصوتية المطلوب اتباعها:
\"\"\"{_voice_context(voice_profile)}\"\"\"

اكتب السكريبت كاملًا بالعامية المصرية، بصيغة كلام منطوق (مش مقال)،
باتباع الهيكل الحكائي بالترتيب، مع الحفاظ على الوعد اللي الهوك فتحه
وتقفيله قبل النهاية.
"""
    return gemini_client.generate(prompt, system_instruction=SYSTEM, temperature=0.85)


def humanize_draft(draft_script: str, voice_profile: Optional[VoiceProfile] = None) -> str:
    humanize_skill = load_skill("humanize")
    prompt = f"""
النص المطلوب تحسينه إنسانيًا (لا تكتب من جديد، حسّن الموجود فقط):
\"\"\"{draft_script}\"\"\"

بصمة الكاتب الصوتية (لو موجودة، التزم بيها):
\"\"\"{_voice_context(voice_profile)}\"\"\"

--- مهارة الإنسانية (اتبعها بدقة) ---
{humanize_skill}
---

أخرج النص المحسّن كاملًا، ثم بعده اكتب سطر "---تغييرات---" وتحته 2-4 نقاط
مختصرة بأهم التعديلات اللي اتعملت.
"""
    return gemini_client.generate(prompt, system_instruction=SYSTEM, temperature=0.6)
