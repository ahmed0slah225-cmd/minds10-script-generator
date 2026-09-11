import json
import re
from core.context import PipelineContext
from engines.base import BaseEngine
from providers.base import LLMProvider
from prompts.templates import TOPIC_PROMPT, SYSTEM_ANALYST


def _extract_json(text: str) -> dict:
    text = text.strip()
    # شيل أسوار الكود
    text = re.sub(r"^```(json)?", "", text, flags=re.MULTILINE).strip()
    text = re.sub(r"```$", "", text).strip()
    # دور على أول { وآخر }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start:end + 1]
    return json.loads(text)


class TopicEngine(BaseEngine):
    name = "topic"

    def run(self, ctx: PipelineContext, provider: LLMProvider) -> PipelineContext:
        prompt = TOPIC_PROMPT.format(raw_input=ctx.raw_input[:20000])
        raw = self.call_llm(
            ctx, provider, prompt,
            system_instruction=SYSTEM_ANALYST,
            temperature=0.4,
            response_mime_type="application/json",
        )
        ctx.topic_analysis = _extract_json(raw)
        return ctx