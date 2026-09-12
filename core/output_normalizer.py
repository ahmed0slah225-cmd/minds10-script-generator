from __future__ import annotations

from typing import Any


class StructuredOutputError(RuntimeError):
    """Raised when an LLM structured response cannot be normalized safely."""


# Only engines where a top-level array has one unambiguous meaning are listed.
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

# Safe semantic aliases for fields whose names commonly vary between
# natural-language instructions and the Pydantic/domain model.
# Keep these explicit by engine so we do not silently change unrelated data.
FIELD_ALIASES = {
    'knowledge': {
        'items': {
            'type': 'kind',
            'content': 'text',
            'text_content': 'text',
            'source_ids': 'source_ids',
        },
    },
    'hook': {
        'hooks': {
            'text_content': 'text',
            'hook': 'text',
        },
    },
}


def _normalize_collection_items(engine_name: str, field_name: str, items: list[Any]) -> list[Any]:
    """Normalize object keys inside a known collection without guessing broadly."""
    aliases = FIELD_ALIASES.get(engine_name, {}).get(field_name, {})
    if not aliases:
        return items

    normalized_items: list[Any] = []
    for item in items:
        if not isinstance(item, dict):
            normalized_items.append(item)
            continue

        obj = dict(item)
        for source_key, target_key in aliases.items():
            if target_key not in obj and source_key in obj:
                obj[target_key] = obj[source_key]
        normalized_items.append(obj)

    return normalized_items


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
                value = [value]
            elif value is None:
                value = []
            if isinstance(value, list):
                normalized[field] = _normalize_collection_items(engine_name, field, value)

        return normalized

    if isinstance(data, list):
        wrapper = TOP_LEVEL_LIST_WRAPPERS.get(engine_name)
        if wrapper:
            return {
                wrapper: _normalize_collection_items(engine_name, wrapper, data)
            }
        raise StructuredOutputError(
            f"{engine_name}: Gemini رجّع JSON Array، لكن المرحلة تحتاج JSON Object. "
            f"المتوقع كائن JSON وليس قائمة. راجع صيغة خرج هذه المرحلة."
        )

    raise StructuredOutputError(
        f"{engine_name}: Gemini رجّع نوع JSON غير مدعوم ({type(data).__name__}). "
        f"المتوقع JSON Object."
    )
