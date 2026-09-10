"""
skills/voice_dna.py
=====================
المصدر الملهم: artemnovitckii/content-skills (مفهوم Voice DNA فقط، تمت
إعادة بنائه بالكامل ليخدم سكريبتات يوتيوب مصرية طويلة - وليس نسخًا حرفيًا).

الاسم: voice_dna
الوظيفة: استخراج بصمة الكاتب الأسلوبية من عينات كتابته السابقة، ثم تمرير
هذه البصمة كإرشاد نثري لأي Engine يحتاجها، وأخيرًا التحقق من اتساق
السكريبت النهائي معها.

Input contract:
    - extract(samples: list[str]) -> VoiceDNAProfile
        samples: نصوص سابقة كتبها المستخدم (سكريبتات قديمة، منشورات، ملاحظات...)
    - as_prompt_guidance(profile) -> str  (من core/context.py)
    - consistency_check(script: str, profile: VoiceDNAProfile) -> ReviewResult

Output contract:
    - VoiceDNAProfile: كائن منظم بالسمات الأسلوبية (core/context.py)
    - ReviewResult: {passed, scores, issues, summary}

قواعد التشغيل:
    - لا تُستخدم لنسخ نص سابق حرفيًا أو محاكاة أسلوب شخص آخر غير المستخدم نفسه.
    - الهدف استخراج السمات المتكررة فقط، وإعادة استخدامها لإنتاج نص جديد.
    - لو مفيش عينات، البصمة تبقى فارغة والنظام يعتمد على مصري طبيعي عام.

متى تعمل:
    A) أثناء التخطيط: كإرشاد يُمرَّر لـ Strategy/Story/Hook.
    B) أثناء الكتابة: يُمرَّر لـ Script Writing Engine.
    C) كمراجعة نهائية: Voice DNA Consistency Check بعد التحرير المصري.

ما لا يجوز لها فعله:
    - اختراع سمات أسلوبية غير مستخرجة فعليًا من العينات.
    - فرض أسلوب على مستخدم لم يقدم عينات (تُترك الكتابة طبيعية عامة).

طريقة الاستدعاء:
    from skills.voice_dna import VoiceDnaSkill
    skill = VoiceDnaSkill()
    profile = skill.extract(samples)
    guidance_text = profile.as_prompt_guidance()
    report = skill.consistency_check(final_script, profile)
"""

from __future__ import annotations

from core.context import VoiceDNAProfile, ReviewResult
from llm.gemini_client import generate_json
from skills.base import BaseSkill

_EXTRACT_PERSONA = (
    "أنت 'محلل البصمة الصوتية' (Voice DNA Analyst). مهمتك قراءة عينات كتابة "
    "سابقة لشخص واحد واستخراج السمات الأسلوبية المتكررة فيها فقط - وليس "
    "تلخيص محتواها. ممنوع اختراع سمات غير ظاهرة فعليًا في العينات."
)

_CONSISTENCY_PERSONA = (
    "أنت 'مراجع اتساق البصمة الصوتية'. تقارن سكريبت نهائي ببصمة أسلوبية "
    "محفوظة مسبقًا، وتحدد أماكن الانحراف الواضح عن الأسلوب المعتاد للكاتب. "
    "لا تطلب تغيير الأفكار أو الحقائق، فقط الأسلوب."
)


class VoiceDnaSkill(BaseSkill):
    name = "voice_dna"
    purpose = "استخراج بصمة الكاتب الأسلوبية وتمريرها كإرشاد لبقية المراحل، ثم التحقق من الاتساق."
    allowed_stages = (
        "strategy", "story", "hook", "script_writing",
        "humanization", "egyptian_arabic_editing", "voice_dna_consistency_check",
    )
    forbidden = (
        "نسخ نص سابق حرفيًا",
        "تقليد أسلوب شخص آخر غير صاحب العينات",
        "اختراع سمات غير مستخرجة من العينات الفعلية",
    )

    def extract(self, samples: list[str]) -> VoiceDNAProfile:
        if not samples:
            return VoiceDNAProfile()

        joined = "\n\n---\n\n".join(s[:4000] for s in samples[:8])
        prompt = f"""
عينات كتابة سابقة لنفس الشخص:
{joined}

استخرج JSON بالشكل التالي فقط بناءً على ما هو ظاهر فعليًا في النصوص:
{{
  "avg_sentence_length": رقم تقديري لمتوسط عدد الكلمات في الجملة,
  "rhythm_notes": "وصف مختصر لإيقاع الكلام",
  "question_usage": "وصف كيف يستخدم الكاتب الأسئلة",
  "vocabulary_level": "بسيط/متوسط/متقدم مع سبب",
  "slang_level": "درجة العامية المصرية المستخدمة",
  "emotion_level": "منخفضة/متوسطة/عالية",
  "transition_style": "وصف طريقة الانتقال بين الأفكار",
  "example_style": "وصف طريقة بناء الأمثلة",
  "closing_style": "وصف طريقة إنهاء الفكرة أو الفقرة",
  "raw_notes": "أي ملاحظة أسلوبية أخرى مهمة يصعب تصنيفها"
}}
"""
        data = generate_json(_EXTRACT_PERSONA, prompt, temperature=0.2)
        data["sample_count"] = len(samples)
        data.pop("_raw", None)
        data.pop("_parse_error", None)
        return VoiceDNAProfile(**{k: v for k, v in data.items() if k in VoiceDNAProfile.__dataclass_fields__})

    def consistency_check(self, script: str, profile: VoiceDNAProfile) -> ReviewResult:
        if profile.sample_count == 0:
            return ReviewResult(passed=True, summary="لا توجد بصمة صوتية محفوظة - تم تخطي هذا الفحص.")

        prompt = f"""
البصمة الصوتية المرجعية:
{profile.as_prompt_guidance()}

السكريبت النهائي المطلوب مراجعته:
{script}

المطلوب JSON:
{{
  "passed": true أو false,
  "scores": {{"الاتساق_مع_البصمة": رقم من 1 إلى 10}},
  "issues": [{{"location": "اقتباس قصير جدًا من مكان الانحراف", "problem": "وصف الانحراف عن البصمة", "suggestion": "تعديل مقترح"}}],
  "summary": "خلاصة قصيرة"
}}
"""
        data = generate_json(_CONSISTENCY_PERSONA, prompt, temperature=0.3)
        return ReviewResult(
            passed=data.get("passed", True),
            scores=data.get("scores", {}),
            issues=data.get("issues", []),
            summary=data.get("summary", ""),
        )
