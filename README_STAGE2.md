# Minds10 Script Generator — Stage 2 Foundation

هذه حزمة الـFoundation للنسخة 2.0.0.

## البيئة

Python 3.11+

## المتغيرات

انسخ `.env.example` إلى `.env` للتطوير المحلي أو ضع القيم داخل Streamlit Secrets عند النشر.

## Gemini

استخدمنا `google-genai` والـ`genai.Client` كطبقة واحدة مركزية. لا تضع مفتاح API داخل Git.

## Turso

النسخة السحابية تستخدم `libsql` للاتصال المباشر بقاعدة Turso عبر URL + Auth Token.

شغّل `database/schema.sql` مرة واحدة لإنشاء الجداول.

## ملاحظة

الـEngines والواجهة الكاملة ستُبنى فوق هذه الطبقة في المراحل التالية.
