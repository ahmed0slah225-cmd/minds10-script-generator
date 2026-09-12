from __future__ import annotations
from dataclasses import dataclass,asdict
from datetime import datetime,timezone

@dataclass
class RunLog:
    run_id:str; project_id:str; stage:str; engine:str; skill:str|None; model_id:str|None; started_at:str; elapsed_ms:int; status:str; error:str=''; input_chars:int=0; output_chars:int=0
    def as_dict(self): return asdict(self)

def now_iso(): return datetime.now(timezone.utc).isoformat()
