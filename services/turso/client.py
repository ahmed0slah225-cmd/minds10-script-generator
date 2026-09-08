"""اتصال Turso remote عبر libsql."""

from __future__ import annotations

from typing import Any

import libsql

from config.settings import Settings


class TursoClient:
    def __init__(self, settings: Settings):
        if not settings.turso_database_url or not settings.turso_auth_token:
            raise ValueError("TURSO_DATABASE_URL و TURSO_AUTH_TOKEN مطلوبان للاتصال بـTurso.")

        self.connection = libsql.connect(
            database=settings.turso_database_url,
            auth_token=settings.turso_auth_token,
        )

    def execute(self, sql: str, params: tuple | list = ()):
        return self.connection.execute(sql, params)

    def executemany(self, sql: str, seq_of_params):
        return self.connection.executemany(sql, seq_of_params)

    def commit(self) -> None:
        self.connection.commit()

    def rollback(self) -> None:
        try:
            self.connection.rollback()
        except Exception:
            pass

    def close(self) -> None:
        try:
            self.connection.close()
        except Exception:
            pass

    def healthcheck(self) -> bool:
        row = self.execute("SELECT 1 AS ok").fetchone()
        return bool(row and row[0] == 1)
