from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class GenerationRequest:
    prompt: str
    system_instruction: Optional[str] = None
    temperature: float = 0.7
    max_output_tokens: Optional[int] = None
    enable_search: bool = False
    files: Optional[List[Any]] = None
    response_mime_type: Optional[str] = None  # "application/json" لو عايز JSON


@dataclass
class GenerationResponse:
    text: str
    model_id: str
    input_tokens: int = 0
    output_tokens: int = 0
    finish_reason: str = "stop"
    sources: Optional[List[Dict[str, Any]]] = None


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, model_id: str, request: GenerationRequest) -> GenerationResponse:
        ...

    @abstractmethod
    def validate(self, model_id: str, request: GenerationRequest) -> Tuple[bool, Optional[str]]:
        ...