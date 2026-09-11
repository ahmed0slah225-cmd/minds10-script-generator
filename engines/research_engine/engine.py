from google.genai import types
from services.gemini.generation import generate_text
from config.settings import get_settings

class ResearchEngine:
    def __init__(self, client):
        self.client = client

    def run(self, query: str, urls=(), purpose: str = "research"):
        s = get_settings()
        tools = []
        if s.allow_web_research:
            tools.append(types.Tool(google_search=types.GoogleSearch()))
        if s.allow_url_context and urls:
            try:
                tools.append(types.Tool(url_context=types.UrlContext()))
            except Exception:
                pass
        prompt = (
            f"ابحث في الموضوع التالي لخدمة مهمة: {purpose}.\n"
            f"السؤال: {query}\n"
            "روابط المستخدم:\n" + "\n".join(urls)
        )
        system = (
            "أنت باحث معلومات لمنصة محتوى. ميّز بين الحقيقة والدليل والاستنتاج. "
            "لا تخترع مصادر أو أرقامًا. فضّل المصدر الأولي. "
            "اكتب بالعربية المصرية البسيطة كإجابة داخلية، وليس سكريبتًا."
        )
        text = generate_text(
            self.client,
            prompt,
            system=system,
            temperature=0.2,
            max_tokens=9000,
            tools=tools or None,
        )
        return {"answer": text, "query": query, "urls": list(urls), "grounded": bool(tools)}
