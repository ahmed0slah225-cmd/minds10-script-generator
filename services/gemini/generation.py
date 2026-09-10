from __future__ import annotations
import json, re, time
from google.genai import types
from config.settings import get_settings

def _text(resp):
    try:
        t=resp.text
        if t: return t
    except Exception: pass
    try:
        return ''.join((getattr(p,'text','') or '') for p in (getattr(resp.candidates[0].content,'parts',[]) or []))
    except Exception: return ''

def generate(client, prompt, *, system='', model=None, temperature=0.7, max_tokens=None, tools=None, json_mode=False, retries=3):
    s=get_settings(); model=model or s.gemini_model; max_tokens=max_tokens or s.max_tokens
    kwargs={'system_instruction':system,'temperature':temperature,'max_output_tokens':max_tokens}
    if tools: kwargs['tools']=tools
    if json_mode: kwargs['response_mime_type']='application/json'
    last=None
    for i in range(retries):
        try:
            r=client.models.generate_content(model=model, contents=prompt, config=types.GenerateContentConfig(**kwargs))
            return r
        except Exception as e:
            last=e; 
            if i<retries-1: time.sleep(2*(i+1))
    raise RuntimeError(f'Gemini request failed: {last}')

def generate_text(*args, **kwargs): return _text(generate(*args, **kwargs))
def generate_json(*args, **kwargs):
    raw=generate_text(*args, json_mode=True, **kwargs)
    raw=re.sub(r'^```json\s*|\s*```$','',raw.strip(),flags=re.I)
    a=min([i for i in [raw.find('{'),raw.find('[')] if i>=0] or [0]); b=max(raw.rfind('}'),raw.rfind(']'))
    return json.loads(raw[a:b+1])
