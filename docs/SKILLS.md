# الـ 4 Skills المدموجة

كل Skill لها ملف مستقل جوه `skills/`، وعقد كامل موثّق كـ docstring في أول
الملف (اسم، وظيفة، Input/Output contract، قواعد تشغيل، متى تعمل، ما
الممنوع، وطريقة الاستدعاء). ملخص سريع:

| Skill | الملف | المصدر الملهم | مُستدعاة من |
|-------|-------|----------------|--------------|
| `humanization` | `skills/humanization.py` | harshaneel/humanize | مرحلة `humanization` بعد `script_writing` |
| `retention` | `skills/retention.py` | MarcoWorms/addictive-writing | `strategy`, `story` (تخطيط) + مرحلة `retention_review` |
| `anti_slop_review` | `skills/anti_slop.py` | hardikpandya/stop-slop + msimchowitz/writing-skills | مرحلتي `anti_slop_review` و `repetition_review` |
| `voice_dna` | `skills/voice_dna.py` | artemnovitckii/content-skills (مفهوم Voice DNA) | `strategy`, `story`, `hook`, `script_writing` (guidance) + مرحلة `voice_dna_consistency_check` |

## القواعد المشتركة (مطبّقة فعليًا في الكود)

1. `humanization` لا تضيف معلومات جديدة → مكتوبة صراحة في الـ persona
   ومكررة في تعليمات الـ prompt نفسه.
2. `anti_slop_review` لا تحذف فكرة مهمة لمجرد أنها معقدة → مكتوبة في
   `forbidden` وفي الـ persona.
3. `retention` لا تستخدم Clickbait، ولا تفتح سؤال بلا Payoff → منطق
   `plan()` يفرض `payoff_at` لكل `open_loop`.
4. `voice_dna` لا تقلد شخصًا آخر ولا تنسخ نصًا سابقًا → موثّق في
   `forbidden`، والاستخراج مبني فقط على عينات المستخدم نفسه.
5. الأولوية دائمًا: المعنى → الوضوح → الإنسانية → الإيقاع، وهي نفس
   الأولوية المستخدمة في prompt مرحلة `egyptian_arabic_editing`.
6. الحقائق والمصادر تُحفظ كما هي عبر كل مراحل التحرير - كل Skill
   بتحسّن/تحرّر، وما ينفعش أي منها يضيف معلومة أو دليل جديد.

## إضافة Skill جديدة لاحقًا
1. أنشئ ملف جديد في `skills/` يرث من `skills.base.BaseSkill`.
2. وثّق العقد كامل في الـ docstring (نفس نمط الملفات الأربعة الحالية).
3. أضف دالة `_stage_xxx` في `core/workflow.py` لو هتشتغل كمرحلة مستقلة،
   أو استدعِها مباشرة من داخل الـ Engine المناسب لو هتشتغل أثناء التخطيط
   أو الكتابة.
4. أضف اسم المرحلة لقائمة `STAGES` بالترتيب الصحيح و`STAGE_LABELS_AR`.

هذا يسمح بتطوير كل Skill بشكل مستقل دون إعادة بناء المشروع بالكامل -
تمامًا كما هو مطلوب.
