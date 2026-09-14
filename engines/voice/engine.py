"""
engines/voice/engine.py
==========================
voice_dna_check — تحقق حتمي (بدون LLM، القاعدة 38) من إن السكريبت
النهائي متوافق تقريبيًا مع سمات الحمض النووي الصوتي المُستخرجة، بدل
تفويت هذا الفحص أو دفع تكلفة موديل إضافية لمقارنة أسلوبية بسيطة.

هذا فحص "علامات تحذير"، مش حكم قاطع — لو voice_dna فاضي أصلاً (المستخدم
معملش استخراج سمات)، الفحص يُتخطى بصمت بدل ما يفشل.
"""

from __future__ import annotations

import re

from core.context import PipelineContext


def run(ctx: PipelineContext, *, model_id: str) -> None:
    voice = ctx.voice_dna
    text = ctx.humanized_script or ctx.draft_script or ""

    if not any([voice.slang_intensity, voice.viewer_address_style, voice.sentence_length_pattern]):
        # مفيش profile حقيقي اتبنى أصلاً — لا داعي لفحص وهمي
        ctx.log_run(engine="voice_dna_check", skill=None, model_id=None, status="skipped_no_profile")
        return

    warnings = []

    if voice.viewer_address_style and "أنت" not in text and "انت" not in text and "ك" not in text[:50]:
        warnings.append("سمة صوت الكاتب بتفضّل مخاطبة المشاهد مباشرة، لكن النص مبدئيًا مافيهوش خطاب مباشر واضح.")

    sentences = [s for s in re.split(r"[.!؟\n]", text) if s.strip()]
    lengths = [len(s.split()) for s in sentences]
    if lengths:
        variance = max(lengths) - min(lengths) if len(lengths) > 1 else 0
        if voice.sentence_length_pattern and "متنوع" in voice.sentence_length_pattern and variance < 3:
            warnings.append("سمة صوت الكاتب بتفضّل تنوّع في طول الجمل، لكن جمل النص طولها متقارب جدًا.")

    if warnings:
        ctx.review_notes.append({"type": "voice_dna_check_warning", "detail": warnings})

    ctx.log_run(engine="voice_dna_check", skill=None, model_id=None, status="passed",
                error=None if not warnings else f"{len(warnings)} تحذير توافق صوت")
