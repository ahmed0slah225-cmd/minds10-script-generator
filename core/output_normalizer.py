from __future__ import annotations

from typing import Any


class StructuredOutputError(RuntimeError):
    """Raised when an LLM structured response cannot be normalized safely."""


# Only engines where a top-level array has an unambiguous meaning are listed.
TOP_LEVEL_LIST_WRAPPERS = {
    'knowledge': 'items',
    'hook': 'hooks',
    'anti_slop_review': 'issues',
    'outline': 'outline',
}

# Collection fields that sometimes arrive as one object instead of a list.
LIST_FIELDS = {
    'items', 'hooks', 'issues', 'outline', 'sources', 'findings',
    'research_questions', 'claims', 'examples', 'stories',
    'numbers', 'quotes', 'contradictions', 'uncertainty',
}

# Common envelope keys sometimes added by structured-output models.
ENVELOPE_KEYS = ('data', 'output', 'result')


def normalize_structured_output(engine_name: str, data: Any) -> dict[str, Any]:
    """Normalize Gemini structured JSON into the object shape expected by an engine."""
    if isinstance(data, dict):
        normalized = dict(data)

        # Unwrap a pure envelope such as {"data": {...}} without guessing
        # when the object contains any other meaningful sibling fields.
        if len(normalized) == 1:
            envelope_key = next((k for k in ENVELOPE_KEYS if k in normalized), None)
            if envelope_key and isinstance(normalized[envelope_key], dict):
                normalized = dict(normalized[envelope_key])

        for field in LIST_FIELDS:
            value = normalized.get(field)
            if isinstance(value, dict):
                normalized[field] = [value]
            elif value is None:
                normalized[field] = []

        return normalized

    if isinstance(data, list):
        wrapper = TOP_LEVEL_LIST_WRAPPERS.get(engine_name)
        if wrapper:
            return {wrapper: data}
        raise StructuredOutputError(
            f"{engine_name}: Gemini رجّع JSON Array، لكن المرحلة تحتاج JSON Object. "
            f"المتوقع كائن JSON وليس قائمة. راجع صيغة خرج هذه المرحلة."
        )

    raise StructuredOutputError(
        f"{engine_name}: Gemini رجّع نوع JSON غير مدعوم ({type(data).__name__}). "
        f"المتوقع JSON Object."
    )
