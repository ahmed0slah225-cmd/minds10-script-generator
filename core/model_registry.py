"""
core/model_registry.py
=======================
سجل مركزي لكل الموديلات المدعومة + قدراتها (Capability Matrix — القسم 33/71).

القاعدة 70: أسماء الموديلات لا يجب أن تكون Hard-coded منتشرة في الملفات.
كل مكان في المشروع يحتاج موديلًا يسأل هذا الملف، لا يكتب الاسم مباشرة.

لاحقًا يمكن استبدال القاموس الثابت هنا باستدعاء فعلي لـ Models API الخاص
بكل مزوّد (Gemini/OpenAI/...) عند الإقلاع، دون تغيير أي كود يستهلك هذا الملف.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class ModelCapabilities:
    supports_pdf: bool = False
    supports_search: bool = False
    supports_structured_output: bool = False
    supports_tools: bool = False
    supports_thinking: bool = False
    context_limit_tokens: int = 0
    max_output_tokens: int = 0


@dataclass(frozen=True)
class ModelInfo:
    model_id: str            # المعرّف الفعلي المُرسل للـ API
    display_name: str        # ما يظهر للمستخدم في الواجهة
    provider: str            # "google" | "openai" | "anthropic" | ...
    available: bool = True
    capabilities: ModelCapabilities = field(default_factory=ModelCapabilities)


# ---------------------------------------------------------------------------
# القائمة المركزية — عدّل هنا فقط عند إضافة/تحديث موديل.
# ملاحظة: القيم الرقمية للسياق تقريبية على أساس توثيق Google وقت الكتابة —
# يجب مراجعتها دوريًا (أو استبدالها بقراءة حيّة من Models API).
# ---------------------------------------------------------------------------
AVAILABLE_MODELS: dict[str, ModelInfo] = {
    "gemini-3-7-flash": ModelInfo(
        model_id="gemini-3-7-flash",
        display_name="Gemini 3.7 Flash",
        provider="google",
        available=True,
        capabilities=ModelCapabilities(
            supports_pdf=True,
            supports_search=True,
            supports_structured_output=True,
            supports_tools=True,
            supports_thinking=True,
            context_limit_tokens=1_000_000,
            max_output_tokens=65_536,
        ),
    ),
    "gemini-3-6-flash": ModelInfo(
        model_id="gemini-3-6-flash",
        display_name="Gemini 3.6 Flash",
        provider="google",
        available=True,
        capabilities=ModelCapabilities(
            supports_pdf=True,
            supports_search=True,
            supports_structured_output=True,
            supports_tools=False,
            supports_thinking=False,
            context_limit_tokens=1_000_000,
            max_output_tokens=32_768,
        ),
    ),
}

DEFAULT_MODEL_ID = "gemini-3-6-flash"


class ModelNotFoundError(Exception):
    pass


class ModelCapabilityError(Exception):
    """تُرفع عندما يُطلب من موديل ميزة لا يدعمها — القاعدة 33/72:
    لا يحدث تشغيل خاطئ صامت، ولا استبدال سري للموديل."""


def get_model(model_id: str) -> ModelInfo:
    info = AVAILABLE_MODELS.get(model_id)
    if info is None:
        raise ModelNotFoundError(f"موديل غير معروف في السجل: {model_id}")
    return info


def list_available_models() -> list[ModelInfo]:
    """يُستخدم لملء Dropdown الواجهة — لا يُعرض أي موديل available=False."""
    return [m for m in AVAILABLE_MODELS.values() if m.available]


def require_capability(model_id: str, capability: str) -> None:
    """يستدعيها أي Engine قبل استخدام ميزة (بحث، PDF، أدوات...).
    لو الموديل لا يدعمها: يرفع خطأ واضح بدل تجاهل الميزة أو تبديل الموديل سرًا."""
    info = get_model(model_id)
    if not getattr(info.capabilities, capability, False):
        raise ModelCapabilityError(
            f"الموديل '{info.display_name}' لا يدعم '{capability}'. "
            f"يرجى اختيار موديل متوافق، أو تفعيل 'السماح بالرجوع التلقائي' "
            f"صراحة في الإعدادات المتقدمة."
        )


def register_model(info: ModelInfo, *, overwrite: bool = False) -> None:
    """نقطة التوسّع الوحيدة لإضافة موديل جديد دون تعديل بقية المشروع
    (القسم 30/70: الموديل لا يحدد Architecture)."""
    if info.model_id in AVAILABLE_MODELS and not overwrite:
        raise ValueError(f"الموديل '{info.model_id}' مسجّل بالفعل. استخدم overwrite=True للتحديث.")
    AVAILABLE_MODELS[info.model_id] = info
