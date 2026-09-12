"""
engines/knowledge_engine.py
============================
البحث والمصدر لا يدخلان مباشرة للكاتب (بند 20). هذا المحرك يبني Knowledge
Base منظمة، ويحافظ دائمًا على تمييز أصل كل معلومة:
user_provided | source_backed | web_research | model_inference | unverified
"""

from __future__ import annotations

from core.contracts import Engine, StepResult
from core.context import PipelineContext, KnowledgeItem


class KnowledgeEngine(Engine):
    name = "knowledge_engine"
    stage = "knowledge"
    requires_llm = False  # عملية تنظيم حتمية، لا تحتاج LLM (بند 38/55)

    def run(self, ctx: PipelineContext, provider) -> StepResult:
        items = list(ctx.knowledge_base)

        # المادة الخام دائمًا مصدر أساسي محفوظ (بند 24)
        if ctx.source and ctx.source.raw_text:
            items.append(
                KnowledgeItem(
                    content=ctx.source.raw_text[:4000],
                    origin="user_provided",
                    source_ref="مادة المستخدم الأصلية",
                    confidence="مصدر أساسي",
                )
            )
        if ctx.source and ctx.source.kind == "pdf":
            items.append(
                KnowledgeItem(
                    content=f"صفحات {ctx.source.pdf_page_start}-{ctx.source.pdf_page_end} من ملف PDF مرفق",
                    origin="source_backed",
                    source_ref=ctx.source.pdf_path or "PDF",
                    confidence="مصدر أساسي",
                )
            )

        ctx.knowledge_base = items
        return StepResult(ok=True, output=items, metrics={"items_count": len(items)})
