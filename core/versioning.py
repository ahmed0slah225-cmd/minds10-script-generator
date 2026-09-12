from __future__ import annotations
from datetime import datetime,timezone
from .models import ProjectState

def snapshot_label(stage:str,version:int)->str:
    return f'{stage}_v{version}'

def mark_snapshot(state:ProjectState,stage:str):
    state.metadata.setdefault('snapshots',[]).append({'label':snapshot_label(stage,state.version),'stage':stage,'timestamp':datetime.now(timezone.utc).isoformat()})
