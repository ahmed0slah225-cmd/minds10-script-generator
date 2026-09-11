from core.model_registry import model_registry
from providers.base import LLMProvider
from providers.gemini import GeminiProvider

_PROVIDERS = {
    "google": GeminiProvider,
}


def get_provider_for(model_id: str, **kwargs) -> LLMProvider:
    model = model_registry.get(model_id)
    if not model:
        raise ValueError(f"موديل غير معروف: {model_id}")
    cls = _PROVIDERS.get(model.provider)
    if not cls:
        raise ValueError(f"لا يوجد Provider للمزود: {model.provider}")
    return cls(**kwargs)