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
