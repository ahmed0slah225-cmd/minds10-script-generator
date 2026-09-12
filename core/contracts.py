from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field
from .models import KnowledgeItem, ProjectState

class StageResult(BaseModel):
    stage: str; ok: bool=True; payload: dict[str,Any]=Field(default_factory=dict); warnings:list[str]=Field(default_factory=list); errors:list[str]=Field(default_factory=list)

class StageContract:
    name='base'; required_fields:tuple[str,...]=()
    def validate(self,state:ProjectState)->list[str]: return [f'غياب الحقل: {f}' for f in self.required_fields if not getattr(state,f,None)]

def source_truth_order(item:KnowledgeItem)->int:
    return {'user_provided':0,'user_file':1,'web_research':2,'model_inference':3,'unverified':4}[item.provenance]

def has_unverified(text:str, knowledge:list[KnowledgeItem])->bool:
    return any(k.provenance=='unverified' and k.text and k.text in text for k in knowledge)
