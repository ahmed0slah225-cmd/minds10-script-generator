"""أدوات مشتركة لكل repositories."""

from __future__ import annotations

from typing import Any


class BaseRepository:
    def __init__(self, db):
        self.db = db

    @staticmethod
    def row_to_dict(row: Any) -> dict[str, Any]:
        if row is None:
            return {}
        try:
            keys = row.keys()
            return {key: row[key] for key in keys}
        except Exception:
            try:
                return dict(row)
            except Exception:
                return {}
