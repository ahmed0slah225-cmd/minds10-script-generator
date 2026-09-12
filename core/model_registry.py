from dataclasses import dataclass


@dataclass(frozen=True)
class ModelSpec:
    model_id: str
    provider: str = "google"
    supports_search: bool = True
    supports_tools: bool = True
    supports_structured_output: bool = True


AVAILABLE_MODELS = {
    "Gemini 3.6 Flash": ModelSpec("gemini-3.6-flash"),
    "Gemini 3.7 Flash": ModelSpec("gemini-3.7-flash"),
}

DEFAULT_MODEL = "Gemini 3.6 Flash"


def get_model(label: str) -> ModelSpec:
    if label not in AVAILABLE_MODELS:
        raise ValueError(f"Unknown model: {label}")
    return AVAILABLE_MODELS[label]


def validate_capabilities(label: str, web_search: bool) -> None:
    spec = get_model(label)
    if web_search and not spec.supports_search:
        raise ValueError(f"{label} لا يدعم البحث المطلوب. لم يتم تبديل الموديل تلقائيًا.")
