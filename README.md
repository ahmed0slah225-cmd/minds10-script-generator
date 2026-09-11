# minds10-script-generator

Content Intelligence Platform لتحويل أي مادة خام إلى سكريبت YouTube احترافي باللهجة المصرية، مع فصل واضح بين الـEngines والـSkills، حفظ المشاريع، مصادر/صفحات PDF، وبحث اختياري عبر Google Search داخل Gemini.

## التشغيل المحلي

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

ضع `GEMINI_API_KEY` في `.streamlit/secrets.toml` أو متغير بيئة.

## Turso

اضبط:

- `TURSO_DATABASE_URL`
- `TURSO_AUTH_TOKEN`

وعند غيابهما يستخدم التطبيق SQLite محليًا للتطوير.

## Streamlit Community Cloud

Entry point: `app.py`

Secrets المطلوبة حسب الاستخدام. لا تضع الأسرار داخل GitHub.

## المعمارية

`Input -> Understanding -> Research -> Knowledge -> Strategy -> Story -> Retention -> Hook -> Script -> Humanize -> Reviews -> Egyptian Edit -> Voice DNA Check -> Final Edit`

كل Skill داخل `skills/` لها ملف `SKILL.md` و`rules.py` ويمكن اختبارها أو تطويرها مستقلة عن بقية النظام.

## Gemini resilience

The app now treats Gemini 429/408/5xx responses as transient, adds bounded exponential backoff with jitter, and falls back from `GEMINI_MODEL` to `GEMINI_FALLBACK_MODEL`. The default fallback is the stable `gemini-3.6-flash-lite`.

Streamlit Secrets:

```toml
GEMINI_API_KEY = "..."
GEMINI_MODEL = "gemini-3.6-flash"
GEMINI_FALLBACK_MODEL = "gemini-3.6-flash-lite"
GEMINI_MAX_ATTEMPTS = "3"
```

When a stage fails, successful prior stages remain persisted. Use **استكمال من آخر مرحلة** to continue from the first stage that was not saved.
