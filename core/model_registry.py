from dataclasses import dataclass

@dataclass(frozen=True)
class ModelSpec:
    label: str
    model_id: str
    provider: str = 'google'
    context_limit: int | None = None
    output_limit: int | None = None
    support_pdf: bool = True
    support_search: bool = True
    support_structured_output: bool = True
    support_tools: bool = True
    support_thinking: bool = True
    support_caching: bool = True

AVAILABLE_MODELS={
    'Gemini 3.8 Flash': ModelSpec('Gemini 3.8 Flash','gemini-3.8-flash'),
    'Gemini 3.7 Flash': ModelSpec('Gemini 3.7 Flash','gemini-3.7-flash'),
    'Gemini 3.6 Flash': ModelSpec('Gemini 3.6 Flash','gemini-3.6-flash'),
    'Gemini 3.5 Flash': ModelSpec('Gemini 3.5 Flash','gemini-3.5-flash'),
}
DEFAULT_MODEL='Gemini 3.8 Flash'

# Ordered from strongest/most preferred to safer alternatives when a model is unavailable.
FALLBACK_MODEL_LABELS=('Gemini 3.8 Flash','Gemini 3.7 Flash','Gemini 3.6 Flash','Gemini 3.5 Flash')

def get_model(label:str)->ModelSpec:
    if label not in AVAILABLE_MODELS: raise ValueError(f'Unknown model: {label}')
    return AVAILABLE_MODELS[label]

def validate_capabilities(label:str,web_search:bool)->None:
    spec=get_model(label)
    if web_search and not spec.support_search: raise ValueError(f'{label} لا يدعم البحث المطلوب.')
