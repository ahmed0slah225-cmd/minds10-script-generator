import os
from core.storage import ProjectStore


def get_store(secrets=None):
    secrets = secrets or {}
    url = secrets.get('TURSO_DATABASE_URL', os.getenv('TURSO_DATABASE_URL', '')).strip()
    token = secrets.get('TURSO_AUTH_TOKEN', os.getenv('TURSO_AUTH_TOKEN', '')).strip()

    # No Turso credentials means local SQLite is the intentional fallback.
    if not url and not token:
        return ProjectStore()

    if not url or not token:
        raise RuntimeError('TURSO_DATABASE_URL و TURSO_AUTH_TOKEN لازم يكونوا موجودين مع بعض.')

    try:
        from .turso import TursoStore
        return TursoStore(url, token)
    except Exception as exc:
        raise RuntimeError(f'فشل تهيئة Turso. راجع بيانات Secrets والاتصال بـTurso: {exc}') from exc
