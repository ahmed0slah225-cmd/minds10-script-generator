import os
from typing import Optional, Tuple
try:
    import google.generativeai as genai  # type: ignore
except ImportError:  # pragma: no cover
    genai = None

from core.model_registry import model_registry
from providers.base import GenerationRequest, GenerationResponse, LLMProvider


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if genai and self.api_key:
            genai.configure(api_key=self.api_key)

    def validate(self, model_id: str, request: GenerationRequest) -> Tuple[bool, Optional[str]]:
        model = model_registry.get(model_id)
        if not model:
            return False, f"موديل غير معروف: {model_id}"
        if not model.enabled:
            return False, f"الموديل {model.display_name} معطّل."
        if request.enable_search and not model.capabilities.supports_search:
            return False, (
                f"الموديل {model.display_name} لا يدعم البحث على الويب. "
                f"اختر موديل يدعمه أو أوقف البحث."
            )
        if request.files and not model.capabilities.supports_pdf:
            return False, f"الموديل {model.display_name} لا يدعم الملفات."
        return True, None

    def generate(self, model_id: str, request: GenerationRequest) -> GenerationResponse:
        ok, err = self.validate(model_id, request)
        if not ok:
            raise ValueError(err)
        if genai is None:
            raise RuntimeError("مكتبة google-generativeai غير مثبتة.")
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY غير مضبوط في البيئة.")

        # نضبط System Instruction لو موجود
        kwargs = {}
        if request.system_instruction:
            kwargs["system_instruction"] = request.system_instruction
        model = genai.GenerativeModel(model_id, **kwargs)

        gen_cfg = {"temperature": request.temperature}
        if request.max_output_tokens:
            gen_cfg["max_output_tokens"] = request.max_output_tokens
        if request.response_mime_type:
            gen_cfg["response_mime_type"] = request.response_mime_type

        call_kwargs = {"generation_config": gen_cfg}
        tools = []
        if request.enable_search:
            tools.append({"google_search_retrieval": {}})
        if tools:
            call_kwargs["tools"] = tools

        content = request.prompt
        if request.files:
            content = list(request.files) + [request.prompt]

        resp = model.generate_content(content, **call_kwargs)

        text = getattr(resp, "text", "") or ""
        usage = getattr(resp, "usage_metadata", None)
        in_tok = getattr(usage, "prompt_token_count", 0) if usage else 0
        out_tok = getattr(usage, "candidates_token_count", 0) if usage else 0

        return GenerationResponse(
            text=text,
            model_id=model_id,
            input_tokens=in_tok,
            output_tokens=out_tok,
        )