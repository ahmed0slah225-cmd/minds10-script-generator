"""اختبارات سجل الموديلات — القسم 80."""
import pytest

from core.model_registry import (
    DEFAULT_MODEL_ID,
    ModelCapabilityError,
    ModelNotFoundError,
    get_model,
    list_available_models,
    require_capability,
)


def test_default_model_is_gemini_3_6_flash():
    assert DEFAULT_MODEL_ID == "gemini-3-6-flash"


def test_both_flash_models_registered_and_available():
    ids = {m.model_id for m in list_available_models()}
    assert "gemini-3-6-flash" in ids
    assert "gemini-3-7-flash" in ids


def test_unknown_model_raises_clear_error():
    with pytest.raises(ModelNotFoundError):
        get_model("gemini-999-ultra")


def test_capability_check_fails_loudly_not_silently():
    # 3.6 Flash في هذا السجل لا يدعم tools — يجب أن يفشل بوضوح
    with pytest.raises(ModelCapabilityError):
        require_capability("gemini-3-6-flash", "supports_tools")


def test_capability_check_passes_when_supported():
    # كلا الموديلين يدعمان البحث في هذا السجل
    require_capability("gemini-3-6-flash", "supports_search")
    require_capability("gemini-3-7-flash", "supports_search")
