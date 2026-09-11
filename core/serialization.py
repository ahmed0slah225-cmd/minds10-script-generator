from __future__ import annotations
from dataclasses import asdict
from core.models import Project, PipelineState

def state_payload(state: PipelineState) -> dict:
    return asdict(state)

def project_from_row(row) -> Project:
    return Project(id=row[0], title=row[1], request=row[2], duration_minutes=int(row[3]), audience=row[4], language=row[5], current_stage=row[6])
