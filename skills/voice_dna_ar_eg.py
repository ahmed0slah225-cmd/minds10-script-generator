"""
skills/voice_dna_ar_eg.py
============================
الحمض النووي الصوتي (بند 9/10). يحلل عينات سابقة من كلام/كتابة المستخدم
ليستخرج ميزات أسلوبية (طول الجمل، الإيقاع، المفردات، مستوى العامية...) —
وليس نسخ النصوص القديمة نفسها.
"""

from __future__ import annotations
import json

from core.contracts import Skill, StepResult
from core.context import PipelineContext, VoiceDNA
from engines.common import call_llm

SYSTEM_PROMPT = """
أنت مهارة استخراج "الحمض النووي الصوتي" لكاتب/يوتيوبر مصري. حلل العينات
المُعطاة واستخرج الميزات الأسلوبية فقط (وليس نسخ الجمل نفسها):
طول الجمل، الإيقاع، مستوى العامية، الأسئلة الموجهة للمشاهد، العاطفة،
أسلوب الشرح والأمثلة، الانتقالات، بناء الفضول، طريقة إنهاء الفكرة.

أعد JSON فقط:
{
  "sentence_length_profile": "...",
  "slang_level": "منخفض|متوسط|عالي",
  "style_notes": "وصف نثري موجز (3-5 أسطر) لأسلوب هذا الكاتب يمكن اتباعه لاحقًا"
}
"""


class VoiceDNASkill(Skill):
    name = "voice_dna_ar_eg"
    skill_type = "profile"
    execution_stage = "planning"
    depends_on = []
    conflicts_with = []

    def run(self, ctx: PipelineContext, provider, **kwargs) -> StepResult:
        samples = ctx.voice_dna.sample_texts
        if not samples:
            return StepResult(ok=True, output=None, warnings=["لا توجد عينات صوتية؛ سيُستخدم أسلوب افتراضي."])

        joined = "\n---\n".join(samples[:5])
        user_prompt = f"عينات من كتابة/كلام المستخدم:\n{joined}"
        response = call_llm(ctx, provider, self.name, SYSTEM_PROMPT, user_prompt)
        if not response.ok:
            return StepResult(ok=False, error=response.error)

        try:
            data = json.loads(response.text.strip().strip("```json").strip("```").strip())
        except Exception:
            data = {"style_notes": response.text}

        ctx.voice_dna.sentence_length_profile = data.get("sentence_length_profile", ctx.voice_dna.sentence_length_profile)
        ctx.voice_dna.slang_level = data.get("slang_level", ctx.voice_dna.slang_level)
        ctx.voice_dna.notes = data.get("style_notes", ctx.voice_dna.notes)
        return StepResult(ok=True, output=data)
