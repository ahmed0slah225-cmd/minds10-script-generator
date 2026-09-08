"""تشغيل schema.sql بصورة idempotent."""

from __future__ import annotations

from pathlib import Path


def apply_schema(db) -> None:
    schema_path = Path(__file__).resolve().parents[3] / "database" / "schema.sql"
    sql = schema_path.read_text(encoding="utf-8")
    # schema بسيط ومكوّن من statements مفصولة بـ ;
    statements = [statement.strip() for statement in sql.split(";") if statement.strip()]
    try:
        for statement in statements:
            db.execute(statement)
        db.commit()
    except Exception:
        db.rollback()
        raise
