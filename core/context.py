from __future__ import annotations
from .models import ProjectState, ProjectSettings

class PipelineContext:
    def __init__(self,state:ProjectState): self.state=state; self.trace=[]
    @property
    def settings(self)->ProjectSettings: return self.state.settings
    def record(self,stage:str,**data): self.trace.append({'stage':stage,**data})
    def set(self,field:str,value): setattr(self.state,field,value)
