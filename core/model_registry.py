"""
model_registry.py
==================
المصدر المركزي الوحيد لأسماء وقدرات الموديلات في المشروع كله.
ممنوع كتابة اسم موديل (مثل "gemini-3.6-flash") في أي مكان آخر غير هذا الملف.
أي Engine أو Skill يجب أن يطلب الموديل عن طريق:
    model_registry.get_default_model()
    model_registry.get_model(model_id)
    model_registry.list_available_models()

القاعدة: الموديل لا يحدد الـ Architecture. هذا الملف فقط هو ما يعرف تفاصيل
الموديلات، وأي طبقة أعلى (Engines/Skills) تتعامل مع "قدرات" وليس أسماء.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class ModelCapabilities:
    """مصفوفة القدرة لكل موديل (بند 71 في المواصفات)."""
    context_limit: int
    max_output_tokens: int
    supports_pdf: bool = True
    supports_web_search: bool = True          # Google Search grounding
    supports_structured_output: bool = True
    supports_tools: bool = True
    supports_thinking: bool = True
    thinking_levels: List[str] = field(default_factory=lambda: ["low", "medium", "high"])


@dataclass(frozen=True)
class ModelInfo:
    model_id: str            # المعرف الفعلي المستخدم في نداء الـ API (لا يُعدَّل)
    display_name_ar: str     # الاسم المعروض للمستخدم بالعربي
    provider: str            # "google"
    available: bool
    is_default: bool
    capabilities: ModelCapabilities
    notes_ar: str = ""


# ---------------------------------------------------------------------------
# السجل المركزي. لإضافة موديل جديد مستقبلاً: أضف سطرًا هنا فقط، ولا تلمس أي
# Engine أو Skill. هذا هو المكان الوحيد المسموح فيه بكتابة model_id حرفيًا.
# ---------------------------------------------------------------------------
_REGISTRY: Dict[str, ModelInfo] = {
    "gemini-3.6-flash": ModelInfo(
        model_id="gemini-3.6-flash",
        display_name_ar="جيميناي 3.6 فلاش (الافتراضي)",
        provider="google",
        available=True,
        is_default=True,
        capabilities=ModelCapabilities(
            context_limit=1_048_576,
            max_output_tokens=65_536,
            supports_pdf=True,
            supports_web_search=True,
            supports_structured_output=True,
            supports_tools=True,
            supports_thinking=True,
            thinking_levels=["minimal", "low", "medium", "high"],
        ),
        notes_ar="موديل سريع واقتصادي، مناسب كافتراضي لمعظم مراحل خط الإنتاج.",
    ),
    "gemini-3.7-flash": ModelInfo(
        model_id="gemini-3.7-flash",
        display_name_ar="جيميناي 3.7 فلاش (أعلى جودة)",
        provider="google",
        available=True,
        is_default=False,
        capabilities=ModelCapabilities(
            context_limit=1_048_576,
            max_output_tokens=65_536,
            supports_pdf=True,
            supports_web_search=True,
            supports_structured_output=True,
            supports_tools=True,
            supports_thinking=True,
            thinking_levels=["low", "medium", "high"],  # لا يدعم minimal
        ),
        notes_ar="أعلى جودة تفكير واستدلال متعدد الخطوات، تكلفة أعلى قليلاً.",
    ),
}

_DEFAULT_MODEL_ID = "gemini-3.6-flash"


def list_available_models() -> List[ModelInfo]:
    """يُستخدم في الواجهة لملء Dropdown اختيار الموديل. لا يعرض موديلات غير متاحة."""
    return [m for m in _REGISTRY.values() if m.available]


def get_model(model_id: str) -> ModelInfo:
    if model_id not in _REGISTRY:
        raise ValueError(f"موديل غير معروف في السجل: {model_id}")
    info = _REGISTRY[model_id]
    if not info.available:
        raise ValueError(f"الموديل '{model_id}' غير متاح حاليًا.")
    return info


def get_default_model() -> ModelInfo:
    return get_model(_DEFAULT_MODEL_ID)


def model_supports(model_id: str, capability: str) -> bool:
    """
    فحص قدرة قبل التشغيل (بند 33/71/72).
    capability من: pdf, web_search, structured_output, tools, thinking
    """
    info = get_model(model_id)
    mapping = {
        "pdf": info.capabilities.supports_pdf,
        "web_search": info.capabilities.supports_web_search,
        "structured_output": info.capabilities.supports_structured_output,
        "tools": info.capabilities.supports_tools,
        "thinking": info.capabilities.supports_thinking,
    }
    if capability not in mapping:
        raise ValueError(f"قدرة غير معروفة: {capability}")
    return mapping[capability]


def resolve_model_for_engine(
    project_default_model_id: str,
    engine_override_model_id: Optional[str] = None,
) -> ModelInfo:
    """
    تنفيذ منطق (الافتراضي ← تجاوز المحرك) الموصوف في البند 29.
    لا يغيّر الموديل سرًا؛ فقط يطبّق الأولوية: Override > مشروع > افتراضي عام.
    """
    chosen_id = engine_override_model_id or project_default_model_id or _DEFAULT_MODEL_ID
    return get_model(chosen_id)
