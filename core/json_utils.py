from __future__ import annotations
import json
import re
from typing import Any


def extract_json(text: str) -> Any:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.S | re.I)
    if match:
        return json.loads(match.group(1))
    for start, end in [("{", "}"), ("[", "]")]:
        i, j = text.find(start), text.rfind(end)
        if i >= 0 and j > i:
            return json.loads(text[i:j+1])
    raise ValueError("لم أستطع استخراج JSON صالح من استجابة النموذج")
