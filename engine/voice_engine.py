"""
engine/voice_engine.py
=========================
الـEngine المسؤول عن Voice DNA بالكامل: تحميل البصمة المخزنة، استخراجها
لو مش موجودة، وفحص الاتساق النهائي. هو نقطة الوصل بين VoiceDNASkill
وقاعدة البيانات — الـSkill نفسه ملوش أي وصول مباشر للـDB.
"""

from __future__ import annotations

from typing import Optional

from engine.gemini_client import GeminiClient
from engine.models import ProjectContext, VoiceDNAProfile
from persistence.db import Database
from skills import VoiceDNASkill


class VoiceEngine:
    def __init__(self, db: Database, llm: Optional[GeminiClient] = None):
        self.db = db
        self.skill = VoiceDNASkill(llm)

    def load_or_extract(self, ctx: ProjectContext) -> ProjectContext:
        """
        بتتنادى أول حاجة في المشروع (بعد Input Intelligence). لو الكاتب
        عنده بصمة محفوظة بالفعل، بتتحمّل من الداتابيز من غير أي نداء
        Gemini. لو مفيش، وعنده عيّنات كتابة كافية، بتتستخرج مرة واحدة
        وتتحفظ عشان المشاريع الجاية لنفس الكاتب ما تكررش النداء.
        """
        existing = self.db.load_voice_profile(ctx.writer_id)
        if existing:
            ctx.voice_dna = existing
            ctx.touch()
            return ctx

        samples = self.db.list_voice_samples(ctx.writer_id)
        if len(samples) >= 2:
            result = self.skill.extract(samples, writer_id=ctx.writer_id)
            if result.ok:
                profile = VoiceDNAProfile(
                    writer_id=ctx.writer_id,
                    traits=result.data.get("traits", {}),
                    notes=result.data.get("notes", ""),
                )
                self.db.save_voice_profile(profile)
                ctx.voice_dna = profile
        ctx.touch()
        return ctx

    def add_sample_and_refresh(self, writer_id: str, sample_text: str) -> Optional[VoiceDNAProfile]:
        """يُستدعى من صفحة "Voice DNA" في الواجهة لما المستخدم يضيف عيّنة جديدة."""
        self.db.add_voice_sample(writer_id, sample_text)
        samples = self.db.list_voice_samples(writer_id)
        if len(samples) < 2:
            return None
        result = self.skill.extract(samples, writer_id=writer_id)
        if not result.ok:
            return None
        profile = VoiceDNAProfile(
            writer_id=writer_id, traits=result.data.get("traits", {}), notes=result.data.get("notes", "")
        )
        self.db.save_voice_profile(profile)
        return profile

    def consistency_check(self, ctx: ProjectContext, script_text: str) -> dict:
        """Review-only — بترجع dict، الـEditor هو اللي بيقرر إزاي يستخدمه."""
        if not ctx.voice_dna.traits:
            return {"consistency_score": None, "note": "لا توجد بصمة صوتية مسجلة لهذا الكاتب بعد."}
        result = self.skill.consistency_check(script_text, ctx.voice_dna)
        return result.data if result.ok else {"consistency_score": None, "error": result.error}
