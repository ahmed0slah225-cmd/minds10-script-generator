"""
engine/engines/hook.py
--------------------------
يكتب عدة مقترحات للبداية (أول 15-30 ثانية) باستخدام مهارة viral_hooks_ar_eg،
مبني على أول لحظة في الهيكل الحكائي. يرجع خيارات متعددة عشان المستخدم
يختار أو الـ Editor النهائي يقرر.
"""

from typing import List, Optional
from engine import gemini_client
from engine.skills.loader import load_skill
from engine.models import VoiceProfile

SYSTEM = (
    "إنت محرك كتابة الهوكات داخل نظام Minds10. اتبع مهارة viral_hooks "
    "المرفقة بدقة، وأخرج مقترحات بصيغة JSON فقط."
)


def _voice_context(voice_profile: Optional[VoiceProfile]) -> str:
    if not voice_profile:
        return "لا توجد بصمة صوتية محفوظة — استخدم أسلوب افتراضي: عامية مصرية طبيعية، جمل متوسطة، بدون رسمية."
    return voice_profile.raw_traits_summary or "بصمة محفوظة بدون ملخص نصي متاح."


def generate_hooks(
    story_architecture: str,
    audience_insight: str,
    voice_profile: Optional[VoiceProfile] = None,
) -> List[dict]:
    hooks_skill = load_skill("viral_hooks")
    prompt = f"""
الهيكل الحكائي (ركّز على أول لحظة/موقف فيه):
\"\"\"{story_architecture}\"\"\"

تحليل الجمهور:
\"\"\"{audience_insight}\"\"\"

بصمة الكاتب الصوتية:
\"\"\"{_voice_context(voice_profile)}\"\"\"

--- مهارة كتابة الهوكات (اتبعها بدقة) ---
{hooks_skill}
---

أخرج JSON بالشكل:
{{
  "hooks": [
    {{"text": "...", "type": "...", "why_it_works": "..."}}
  ]
}}
اكتب 4 مقترحات مختلفة بالعامية المصرية.
"""
    result = gemini_client.generate_json(prompt, system_instruction=SYSTEM, temperature=0.9)
    hooks = result.get("hooks", [])
    return hooks if isinstance(hooks, list) else []
