# المرحلة الثانية — Core Foundation

هذه الطبقة لا تحتوي بعد على محركات المحتوى أو صفحات الواجهة.
هدفها تثبيت الحدود بين:

- `config/`: الإعدادات والثوابت والنماذج التشغيلية.
- `domain/`: كيانات المجال.
- `core/`: orchestration وcontext وstate.
- `services/`: تكاملات Gemini وTurso.
- `database/`: schema الدائم.
- `utils/`: أدوات صغيرة مشتركة.

قاعدة مهمة: الـUI لا يستدعي Gemini أو Turso مباشرة. الواجهة تستدعي services/cores، والـEngines القادمة تستخدم نفس الطبقات.
