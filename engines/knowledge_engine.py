from core.context import PipelineContext, KnowledgeItem
from engines.base import BaseEngine
from engines.topic_engine import _extract_json
from providers.base import LLMProvider
from prompts.templates import KNOWLEDGE_PROMPT, SYSTEM_ANALYST


class KnowledgeEngine(BaseEngine):
    name = "knowledge"

    def run(self, ctx: PipelineContext, provider: LLMProvider) -> PipelineContext:
        research_str = ""
        if ctx.research_results:
            research_str = "\n".join(
                f"- {r.get('text','')} (source: {r.get('source','')}, kind: {r.get('kind','')}, conf: {r.get('confidence','')})"
                for r in ctx.research_results
            )

        prompt = KNOWLEDGE_PROMPT.format(
            raw_input=ctx.raw_input[:20000],
            research=research_str[:10000] or "(لا يوجد)",
        )
        raw = self.call_llm(
            ctx, provider, prompt,
            system_instruction=SYSTEM_ANALYST,
            temperature=0.3,
            response_mime_type="application/json",
        )
        data = _extract_json(raw)
        items = []
        for it in data.get("items", []):
            try:
                items.append(KnowledgeItem(
                    text=str(it.get("text", "")),
                    kind=str(it.get("kind", "fact")),
                    source=str(it.get("source", "")),
                    source_type=str(it.get("source_type", "model_inference")),
                    confidence=str(it.get("confidence", "medium")),
                ))
            except Exception:
                continue
        ctx.knowledge_base = items
        return ctx