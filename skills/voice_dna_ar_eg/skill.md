# voice_dna_ar_eg

**الأصل:** دليل بناء Voice DNA من `artemnovitckii/content-skills`، معاد بناؤه كطبقة مشتركة عبر كل الـEngines.

**النوع:** Extract (مرة واحدة لكل كاتب) + Review (Consistency Check نهائي).

## متى تعمل

| الدالة | التوقيت | التكرار |
|---|---|---|
| `extract()` | أول مرة يضيف فيها الكاتب عيّناته أو يحدّثها | مرة لكل كاتب، تُخزَّن في `voice_profiles` |
| `to_prompt_fragment()` | تُحقن جوه أي Prompt في Story/Hook/Script/Humanize/Editor | بدون نداء Gemini إضافي |
| `consistency_check()` | آخر الـWorkflow، بعد `Egyptian Arabic Editing` | مرة لكل مشروع |

## ما لا يجوز فعلها

- لا تُستخرج البصمة من عيّنة واحدة (الحد الأدنى عيّنتين، والأفضل 5+).
- لا تُستخدم لنسخ جمل حرفية من عيّنات سابقة.
- لا تفترض تقليد كاتب مشهور بعينه.
- `consistency_check()` تحليل فقط، لا تعدّل السكريبت.
