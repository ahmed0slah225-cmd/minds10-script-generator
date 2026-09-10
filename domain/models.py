from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

def now(): return datetime.now(timezone.utc).isoformat()
@dataclass
class Project:
    id:str; title:str; task_type:str; workspace_id:str='default'; input_text:str=''; duration_minutes:float|None=None; audience:str=''; status:str='draft'; current_stage:str='input'; metadata:dict[str,Any]=field(default_factory=dict); created_at:str=field(default_factory=now); updated_at:str=field(default_factory=now)
@dataclass
class Page:
    page_number:int; text:str; word_count:int
@dataclass
class Document:
    source_id:str; filename:str; title:str=''; author:str=''; page_count:int=0; pages:list[Page]=field(default_factory=list); metadata:dict[str,Any]=field(default_factory=dict)
@dataclass
class Evidence:
    claim:str; evidence:str; confidence:float; source_id:str=''; page_number:int|None=None; source_url:str=''; kind:str='fact'
@dataclass
class VoiceProfile:
    id:str; name:str; profile:dict[str,Any]; samples:list[str]=field(default_factory=list)
