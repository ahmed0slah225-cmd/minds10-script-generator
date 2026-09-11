"""
engine/knowledge_engine.py
=============================
مرحلة "Knowledge". بياخد research_notes الخام ويحوّلها لـKnowledgeItems
منظمة، مع الحفاظ على مبدأ "إيه اللي نعرفه فعلًا وإيه اللي لسه غير مؤكد".

منطق تحويل الـconfidence هنا مباشر (مش محتاج نداء Gemini إضافي) لأن
DeepResearchSkill في مرحلة البحث أصلًا بيرجّع confidence لكل نتيجة —
الـEngine هنا بس بينظّمها في KnowledgeItem رسمية وبيربطها بالمصادر.
"""

from __future__ import annotations

from engine.models import ProjectContext, KnowledgeItem, new_id

_CONFIDENCE_MAP = {
    "confirmed": "confirmed",
    "needs_verification": "unconfirmed",
}


class KnowledgeEngine:
    def run(self, ctx: ProjectContext) -> ProjectContext:
        for note in ctx.research_notes:
            for finding in note.get("findings", []):
                confidence = _CONFIDENCE_MAP.get(finding.get("confidence"), "unconfirmed")
                kind = "evidence" if finding.get("origin") == "web_search" else "idea"
                ctx.knowledge_base.append(
                    KnowledgeItem(
                        id=new_id("know"),
                        content=finding.get("content", ""),
                        kind=kind,
                        confidence=confidence,
                    )
                )
        ctx.touch("knowledge")
        return ctx
