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

# These collection fields are consumed as objects by downstream code.
# Non-object members are dropped instead of causing a secondary AttributeError.
OBJECT_LIST_FIELDS = {
    'items', 'hooks', 'issues', 'outline', 'sources', 'findings',
}

# Common envelope keys sometimes added by structured-output models.
ENVELOPE_KEYS = ('data', 'output', 'result')

# Safe semantic aliases for fields whose names commonly vary between
# natural-language instructions and the domain models.
FIELD_ALIASES = {
    'knowledge': {
        'items': {
            'type': 'kind',
            'content': 'text',
            'text_content': 'text',
        },
    },
    'hook': {
        'hooks': {
            'text_content': 'text',
            'hook': 'text',
        },
    },
    'anti_slop_review': {
        'issues': {
            'category': 'dimension',
            'dimension_name': 'dimension',
            'description': 'problem',
            'why': 'reason',
            'fix': 'suggested_fix',
        },
    },
}

# Small, safe defaults for domain fields that are often omitted by models.
ITEM_DEFAULTS = {
    'knowledge': {
        'items': {
            'kind': 'claim',
            'text': '',
            'provenance': 'model_inference',
            'source_ids': [],
            'confidence': 0.0,
            'verified': False,
        },
    },
    'anti_slop_review': {
        'issues': {
            'dimension': 'general',
            'problem': '',
            'reason': '',
            'suggested_fix': '',
            'priority': 3,
        },
    },
}

PROVENANCE_ALIASES = {
    'user_material': 'user_provided',
    'user_source': 'user_provided',
    'user_file': 'user_file',
    'web_source': 'web_research',
    'web': 'web_research',
    'research': 'web_research',
    'model': 'model_inference',
    'inference': 'model_inference',
    'unknown': 'unverified',
}


def _normalize_collection_items(engine_name: str, field_name: str, items: list[Any]) -> list[Any]:
    aliases = FIELD_ALIASES.get(engine_name, {}).get(field_name, {})
    defaults = ITEM_DEFAULTS.get(engine_name, {}).get(field_name, {})
    normalized_items: list[Any] = []

    for item in items:
        if not isinstance(item, dict):
            if field_name in OBJECT_LIST_FIELDS:
                continue
            normalized_items.append(item)
            continue

        obj = dict(item)
        for source_key, target_key in aliases.items():
            if target_key not in obj and source_key in obj:
                obj[target_key] = obj[source_key]

        for key, value in defaults.items():
            obj.setdefault(key, value.copy() if isinstance(value, list) else value)

        if engine_name == 'knowledge' and field_name == 'items':
            provenance = obj.get('provenance')
            if isinstance(provenance, str):
                obj['provenance'] = PROVENANCE_ALIASES.get(provenance.strip().lower(), provenance)

        normalized_items.append(obj)

    return normalized_items


def normalize_structured_output(engine_name: str, data: Any) -> dict[str, Any]:
    """Normalize Gemini structured JSON into the object shape expected by an engine."""
    if isinstance(data, dict):
        normalized = dict(data)

        # Unwrap a pure envelope such as {"data": {...}} only when it is
        # the sole top-level key, so meaningful sibling fields are preserved.
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
            return {wrapper: _normalize_collection_items(engine_name, wrapper, data)}
        raise StructuredOutputError(
            f"{engine_name}: Gemini رجّع JSON Array، لكن المرحلة تحتاج JSON Object. "
            f"المتوقع كائن JSON وليس قائمة. راجع صيغة خرج هذه المرحلة."
        )

    raise StructuredOutputError(
        f"{engine_name}: Gemini رجّع نوع JSON غير مدعوم ({type(data).__name__}). "
        f"المتوقع JSON Object."
    )
