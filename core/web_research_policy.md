# Web Research Policy

البحث على الويب قرار صريح من المستخدم، وليس صلاحية تلقائية للمحركات.

## OFF — الافتراضي
عندما تكون `web_search=false`:
- لا يتم إنشاء Google Search tool.
- لا يقوم أي Engine ببحث خارجي.
- لا يتم تغيير هذا القرار بسبب موضوع "يحتاج بحثًا".
- مصادر المستخدم وقاعدة المعرفة والسياق الحالي هي المدخلات المسموح بها.

## ON
عندما تكون `web_search=true`:
- يسمح للـResearch Engine باستخدام أداة البحث التي يدعمها الموديل.
- يتم حفظ المصادر والروابط وتاريخ الجمع عند توفرها.
- لا تتحول نتيجة بحث غير موثوقة تلقائيًا إلى حقيقة.

## فصل مصادر الحقيقة
كل Knowledge item يجب أن يحمل source_type واحدًا على الأقل:
- user_provided
- user_file
- web_research
- model_inference
- unverified

المصدر الذي قدمه المستخدم لا يُستبدل بصمت بمصدر خارجي.

## Research Depth
واجهة المشروع تدعم لاحقًا:
- basic: أقل قدر لازم من البحث.
- standard: بحث كافٍ للتحقق وبناء الحجة.
- deep: توسع أكبر في المصادر والتناقضات والتحقق.

Deep ليس افتراضيًا.

## Capability Gate
قبل التشغيل:
model capabilities → web_search requested? → supported? → run / clear error.
لا يوجد fallback سري يبدل الموديل.
