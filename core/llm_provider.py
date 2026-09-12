from typing import Optional
from google import genai
from google.genai import types


class GeminiProvider:
    """Provider adapter: engines depend on this interface, not directly on Gemini."""

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def generate(self, model_id: str, prompt: str, system_instruction: str = "", web_search: bool = False):
        kwargs = {}
        if system_instruction:
            kwargs["system_instruction"] = system_instruction
        if web_search:
            kwargs["tools"] = [types.Tool(google_search=types.GoogleSearch())]
        return self.client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=types.GenerateContentConfig(**kwargs),
        )
