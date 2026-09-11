from google import genai
from config.settings import get_settings
class GeminiClient:
    def __init__(self, api_key=None):
        self.settings=get_settings(); key=api_key or self.settings.gemini_api_key
        if not key: raise RuntimeError('مفتاح GEMINI_API_KEY غير موجود.')
        self.client=genai.Client(api_key=key)
    def raw(self): return self.client
