import time
from typing import Optional
from core.context import PipelineContext
from providers.base import GenerationRequest, LLMProvider


class BaseEngine:
    name: str = "base"

    def call_llm(
        self,
        ctx: PipelineContext,
        provider: LLMProvider,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        enable_search: bool = False,
        response_mime_type: Optional[str] = None,
    ) -> str:
        model_id = ctx.model_config.model_for(self.name)

        # البحث ما يتفعّلش إلا لو المستخدم فعّله في الـConfig
        effective_search = enable_search and ctx.research_config.enabled

        req = GenerationRequest(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=temperature,
            enable_search=effective_search,
            response_mime_type=response_mime_type,
        )

        # فحص Capacity
        ok, err = provider.validate(model_id, req)
        if not ok:
            raise RuntimeError(err)

        t0 = time.time()
        resp = provider.generate(model_id, req)
        dt = time.time() - t0

        ctx.run_log.append({
            "engine": self.name,
            "model": model_id,
            "duration": round(dt, 2),
            "input_tokens": resp.input_tokens,
            "output_tokens": resp.output_tokens,
            "status": "ok",
        })
        return resp.text

    def run(self, ctx: PipelineContext, provider: LLMProvider) -> PipelineContext:
        raise NotImplementedError