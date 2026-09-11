"""
سجل الموديلات المركزي — لا تكتب أسماء الموديلات في أي مكان آخر.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


DEFAULT_MODEL_ID = "gemini-3.6-flash"


@dataclass
class ModelCapabilities:
    supports_pdf: bool = True
    supports_search: bool = False
    supports_structured_output: bool = True
    supports_tools: bool = False
    supports_thinking: bool = False
    supports_caching: bool = True


@dataclass
class ModelInfo:
    id: str
    display_name: str
    provider: str
    context_limit: int
    input_limit: int
    output_limit: int
    capabilities: ModelCapabilities = field(default_factory=ModelCapabilities)
    enabled: bool = True
    notes: str = ""


class ModelRegistry:
    def __init__(self) -> None:
        self._models: Dict[str, ModelInfo] = {}

    def register(self, model: ModelInfo) -> None:
        self._models[model.id] = model

    def get(self, model_id: str) -> Optional[ModelInfo]:
        return self._models.get(model_id)

    def list_enabled(self) -> List[ModelInfo]:
        return [m for m in self._models.values() if m.enabled]

    def list_all(self) -> List[ModelInfo]:
        return list(self._models.values())

    def get_default(self) -> str:
        # الافتراضي = gemini-3.6-flash لو متاح، وإلا أول موديل enabled
        if DEFAULT_MODEL_ID in self._models and self._models[DEFAULT_MODEL_ID].enabled:
            return DEFAULT_MODEL_ID
        for m in self._models.values():
            if m.enabled:
                return m.id
        raise RuntimeError("لا يوجد أي موديل متاح في السجل.")


model_registry = ModelRegistry()

# -----------------------------------------------------------------
# الموديلات — IDs قابلة للتغيير حسب Google API الحقيقي
# -----------------------------------------------------------------
model_registry.register(ModelInfo(
    id="gemini-3.6-flash",
    display_name="Gemini 3.6 Flash",
    provider="google",
    context_limit=1_000_000,
    input_limit=1_000_000,
    output_limit=8192,
    capabilities=ModelCapabilities(
        supports_pdf=True,
        supports_search=True,
        supports_structured_output=True,
        supports_tools=True,
        supports_thinking=False,
        supports_caching=True,
    ),
    enabled=True,
    notes="الموديل الافتراضي للمشروع.",
))

model_registry.register(ModelInfo(
    id="gemini-3.7-flash",
    display_name="Gemini 3.7 Flash",
    provider="google",
    context_limit=1_000_000,
    input_limit=1_000_000,
    output_limit=8192,
    capabilities=ModelCapabilities(
        supports_pdf=True,
        supports_search=True,
        supports_structured_output=True,
        supports_tools=True,
        supports_thinking=True,
        supports_caching=True,
    ),
    enabled=True,
    notes="موديل أحدث، يدعم thinking.",
))