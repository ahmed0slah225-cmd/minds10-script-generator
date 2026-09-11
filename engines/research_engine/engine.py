from google.genai import types
from services.gemini.generation import generate_text
from config.settings import get_settings

class ResearchEngine:
    """Research only from explicitly allowed sources.

    Google Search is opt-in. When it is off, the engine may use only URLs
    supplied by the user (via URL Context). With no user URLs, it performs
    no web research call at all.
    """
    def __init__(self, client):
        self.client = client

    def run(self, query: str, urls=(), purpose: str = "research", use_google_search: bool | None = None):
        s = get_settings()
        use_google_search = False if use_google_search is None else bool(use_google_search)
        clean_urls = [u.strip() for u in (urls or []) if u and u.strip()]

        # Explicit rule: with Google Search OFF and no user-provided URLs,
        # do not perform a research request using the model's own knowledge.
        if not use_google_search and not clean_urls:
            return {
                "answer": "",
                "query": query,
                "urls": [],
                "grounded": False,
                "source_mode": "none",
            }

        tools = []
        if use_google_search:
            tools.append(types.Tool(google_search=types.GoogleSearch()))
        # URL Context is NOT a web search. It only reads URLs explicitly
        # supplied by the user. This remains available when Google Search is off.
        if clean_urls and s.allow_url_context:
            try:
                tools.append(types.Tool(url_context=types.UrlContext()))
            except Exception:
                pass

        source_mode = "google_search" if use_google_search else "user_urls_only"
        prompt = (
            f"نفّذ مهمة بحث لخدمة: {purpose}.\n"
            f"السؤال/الموضوع: {query}\n"
            "المصادر التي قدمها المستخدم (استخدمها فقط إذا كان البحث العام مغلقًا):\n"
            + "\n".join(clean_urls)
        )
        if use_google_search:
            prompt += "\nالبحث العام في الإنترنت مسموح لأن المستخدم فعّله. استخدم Google Search عند الحاجة."
        else:
            prompt += (
                "\nالبحث العام في الإنترنت ممنوع في هذه المهمة. لا تستخدم Google Search "
                "ولا تعتمد على نتائج بحث عامة. اعتمد فقط على الروابط التي قدمها المستخدم. "
                "إذا تعذر الوصول إلى الروابط، صرّح بذلك ولا تستبدلها بمعرفة عامة."
            )

        system = (
            "أنت باحث معلومات لمنصة محتوى. ميّز بين الحقيقة والدليل والاستنتاج. "
            "لا تخترع مصادر أو أرقامًا. فضّل المصدر الأولي. "
            "أنت لا تكتب سكريبتًا؛ تنتج مادة بحث داخلية موثوقة. "
            "عندما تكون المصادر محصورة في روابط المستخدم، التزم بها حصريًا."
        )
        text = generate_text(
            self.client,
            prompt,
            system=system,
            temperature=0.2,
            max_tokens=9000,
            tools=tools or None,
        )
        return {
            "answer": text,
            "query": query,
            "urls": clean_urls,
            "grounded": bool(tools),
            "source_mode": source_mode,
        }
