---
name: anti_slop_ar_eg
version: 1.0.0
type: review
phase: post_write
requires_llm: true
---
# Anti-Slop المصري — Reviewer أولًا

## الهدف
اكتشاف الكتابة المولدة أو المصقولة زيادة عن اللزوم، ثم وصف المشكلة ومكانها والإصلاح الأقل كلفة، من غير إعادة كتابة عمياء.

## عقد التنفيذ
المدخل: draft + audience + voice_dna + topic/strategy.
المخرج: scores + issues + summary + pass/fail.
لا تُخرج نسخة جديدة كاملة من السكريبت.

## ما نفحصه
الحشو، التمهيد الفارغ، العموميات، العمق الزائف، التكرار الدلالي، الجمل الجميلة بلا وظيفة، الانتقالات المعلبة، الرسمية الزائدة، التعظيم الفارغ، narrator-from-distance، المبني للمجهول الذي يخفي الفاعل، الإيقاع الميكانيكي، وتكرار بدايات/نهايات الفقرات.

في النص المنطوق نخفف معايير formatting، ونركز على specificity والصوت والوضوح.

## Hollow vs Earned
الـcontrast مسموح عندما يكون الطرف الثاني محددًا ويظهر له payoff. أي contrast يخفي غياب فكرة يُرفض.

## التقييم
naturalness / information_density / clarity / language_strength / ai_feel من 1 إلى 10. كل issue يحتوي dimension وlocation وproblem وreason وsuggested_fix وseverity وpriority.

## Minimum Effective Editing
لا تقترح تعديلًا إلا عندما يوجد مكسب واضح. الجملة الجيدة تظل كما هي.
