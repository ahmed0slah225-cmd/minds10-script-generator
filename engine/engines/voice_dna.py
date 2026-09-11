"""
engine/engines/voice_dna.py
-------------------------------
استخراج بصمة الكاتب من عينات كتابة سابقة، باستخدام مهارة voice_dna_ar_eg.
المخرج كائن VoiceProfile منظم يُستخدم لاحقًا في باقي محركات الكتابة.
"""

from typing import List
from engine import gemini_client
from engine.skills.loader import load_skill
from engine.models import VoiceProfile

SYSTEM = (
    "إنت محرك استخراج البصمة الصوتية (Voice DNA) داخل نظام Minds10. "
    "حلل عينات الكتابة المرفقة واستخرج الأنماط الأسلوبية فقط، بدون "
    "أحكام قيمية، وبدون اقتباس جمل كاملة من العينات في الملخص."
)


def extract_voice_profile(name: str, samples: List[str]) -> VoiceProfile:
    skill = load_skill("voice_dna")
    joined_samples = "\n\n---عينة جديدة---\n\n".join(samples)
    prompt = f"""
عينات الكتابة السابقة للمستخدم:
\"\"\"{joined_samples}\"\"\"

--- مهارة استخراج البصمة الصوتية (اتبعها بدقة) ---
{skill}
---

أخرج JSON بالحقول التالية بالضبط:
{{
  "avg_sentence_length": "",
  "pacing": "",
  "question_usage": "",
  "vocabulary_notes": "",
  "slang_level": "",
  "emotion_level": "",
  "explanation_style": "",
  "example_style": "",
  "transition_style": "",
  "curiosity_style": "",
  "ending_style": "",
  "metaphor_usage": "",
  "formality_level": "",
  "direct_address_style": "",
  "raw_traits_summary": "فقرة حرة من 5-8 أسطر تلخص شخصية الكاتب الكتابية"
}}
"""
    data = gemini_client.generate_json(prompt, system_instruction=SYSTEM, temperature=0.4)
    profile = VoiceProfile(name=name, sample_snippets=samples[:5])
    for key in [
        "avg_sentence_length", "pacing", "question_usage", "vocabulary_notes",
        "slang_level", "emotion_level", "explanation_style", "example_style",
        "transition_style", "curiosity_style", "ending_style", "metaphor_usage",
        "formality_level", "direct_address_style", "raw_traits_summary",
    ]:
        if key in data and isinstance(data[key], str):
            setattr(profile, key, data[key])
    return profile
