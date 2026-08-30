# 🎬 Minds10 Script Generator

تطبيق Streamlit بيولّد سكريبتات فيديوهات يوتيوب طويلة (حوالي 30 دقيقة)
بالعامية المصرية، لصالح قناة **Minds10**. بيستخدم **Gemini API** من
Google، ومعاه خاصية **البحث التلقائي من الإنترنت (Grounding)** عشان
يجيب أدلة وأرقام ودراسات حقيقية أثناء الكتابة من غير ما تحتاج تدوّر
عليها بنفسك.

## 📁 هيكلة المشروع

```
minds10-script-generator/
├── app.py                          # واجهة Streamlit فقط
├── engine/
│   ├── __init__.py
│   ├── prompts.py                  # كل التعليمات (System Instruction) وبناء الـ Prompt
│   └── style_guide.md              # دليل الأسلوب بشكل مقروء - عدّل هنا الأول لو عايز تغيّر الأسلوب
├── examples/
│   └── sample_script.md            # مثال مرجعي (Few-shot) للأسلوب واللغة
├── .streamlit/
│   └── secrets_template.toml       # نموذج لشكل ملف الـ secrets (مش الملف الحقيقي)
├── requirements.txt
├── .gitignore
└── README.md
```

الفكرة إن كل حاجة خاصة بـ"طريقة الكتابة والأسلوب" بقت في `engine/`
منفصلة عن كود الواجهة، عشان تقدر تجرب وتعدّل الأسلوب من غير ما تلمس
كود Streamlit خالص.

## 🔎 البحث التلقائي (Grounding) - مجاني إزاي بالظبط؟

خاصية البحث **مدمجة جوه Gemini API نفسه** ومش محتاجة مفتاح API تاني
منفصل ولا اشتراك في محرك بحث خارجي. بس فيه تفصيلة مهمة:

> لتشتغل الخاصية دي بثبات (من غير ما تقابل خطأ 429 - تجاوز الحصة)،
> لازم تكون مفعّل **Billing** على مشروعك في [Google AI Studio](https://aistudio.google.com/)
> - حتى لو استهلاكك الفعلي فضل في حدود الاستخدام المجاني.

لو مش عايز تفعّل Billing دلوقتي، سيب خيار "فعّل البحث التلقائي" في
التطبيق مطفي - السكريبت هيتكتب برضه وبجودة كويسة، بس من غير بحث حي.

## 🚀 التشغيل محليًا

```bash
git clone https://github.com/<اسم_حسابك>/minds10-script-generator.git
cd minds10-script-generator
pip install -r requirements.txt

# حط مفتاحك:
cp .streamlit/secrets_template.toml .streamlit/secrets.toml
# وبعدين افتح .streamlit/secrets.toml وحط مفتاح Gemini API الحقيقي بتاعك

streamlit run app.py
```

## ☁️ النشر على Streamlit Community Cloud

1. ادخل على [share.streamlit.io](https://share.streamlit.io/) وسجّل دخول بحساب GitHub بتاعك.
2. اضغط **New app**.
3. اختار الـ repo: `minds10-script-generator`، والـ branch: `main`، وملف التشغيل: `app.py`.
4. اضغط **Deploy**.
5. بعد ما التطبيق يتعمله Deploy، ادخل على **Settings → Secrets** من داخل التطبيق على Streamlit Cloud، وضيف:
   ```toml
   GEMINI_API_KEY = "مفتاحك_الحقيقي_هنا"
   ```
6. احفظ - التطبيق هيعيد تشغيل نفسه تلقائيًا وهيقرأ المفتاح من هناك.

بعد كده، أي تعديل بترفعه بـ `git push` على فرع `main` هيتنشر تلقائيًا
على نفس الرابط من غير ما تعمل أي حاجة إضافية.

## 🔑 إزاي تجيب مفتاح Gemini API

1. ادخل [Google AI Studio](https://aistudio.google.com/).
2. اضغط **Get API key** → **Create API key**.
3. انسخ المفتاح واستخدمه في `secrets.toml` محليًا أو في Secrets على Streamlit Cloud.

## 🔄 Git - أوامر الرفع الأساسية

```bash
git add .
git commit -m "وصف التعديل اللي عملته"
git push
```

Streamlit Community Cloud بيتابع فرع `main` تلقائيًا، فبمجرد ما الـ
push ينجح، التطبيق هيتحدّث لوحده خلال دقيقة أو اتنين.

## ✏️ إزاي تعدّل أسلوب الكتابة

1. افتح `engine/style_guide.md` واقرا/عدّل القاعدة اللي عايزها بشكل مقروء.
2. انقل نفس التعديل لنص القواعد جوه `engine/prompts.py` (دالة `build_system_instruction`).
3. لو عندك سكريبت جديد عايز يبقى مرجع أسلوب أقوى، حدّث `examples/sample_script.md`
   والمقطع المُنتقى `VOICE_SAMPLE_EXCERPT` في `engine/prompts.py`.
4. اعمل commit و push زي ما فوق.

## ⚠️ ملاحظات مهمة

- **متحطش مفتاح الـ API مباشرة في الكود أبدًا** - استخدم Secrets دايمًا.
- ملف `.streamlit/secrets.toml` الحقيقي متضاف في `.gitignore` عشان
  محدش يقدر يرفعه بالغلط على GitHub.
- أسامي الموديلات المتاحة في التطبيق (`gemini-3.7-flash`,
  `gemini-3.6-flash`, `gemini-3.5-flash`, `gemini-2.5-flash`) بتتغيّر
  من وقت للتاني حسب إصدارات Google - لو قابلت خطأ 404 يعني الموديل
  اتشال، راجع [صفحة الموديلات](https://ai.google.dev/gemini-api/docs/models) واختار موديل بديل من القائمة.
