from __future__ import annotations

from typing import Any


class StructuredOutputError(RuntimeError):
    """Raised when an LLM structured response cannot be normalized safely."""


# Only engines where a top-level array has one unambiguous meaning are listed.
TOP_LEVEL_LIST_WRAPPERS = {
    'knowledge': 'items',
    'hook': 'hooks',
    'anti_slop_review': 'issues',
}

# Collection fields that sometimes arrive as one object instead of a list.
LIST_FIELDS = {
    'items', 'hooks', 'issues', 'sources', 'findings',
    'research_questions', 'claims', 'examples', 'stories',
    'numbers', 'quotes', 'contradictions', 'uncertainty',
}


def normalize_structured_output(engine_name: str, data: Any) -> dict[str, Any]:
    """Normalize Gemini structured JSON into a safe object shape."""
    if isinstance(data, dict):
        normalized = dict(data)
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
