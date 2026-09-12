import os
from core.storage import ProjectStore

def get_store(secrets=None):
    secrets=secrets or {}
    url=secrets.get('TURSO_DATABASE_URL',os.getenv('TURSO_DATABASE_URL',''))
    token=secrets.get('TURSO_AUTH_TOKEN',os.getenv('TURSO_AUTH_TOKEN',''))
    if url and token:
        try:
            from .turso import TursoStore
            return TursoStore(url,token)
        except Exception:
            pass
    return ProjectStore()
