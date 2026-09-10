# البنية المعمارية

## المبدأ الحاكم
المشروع لا يبدأ بالكتابة. المشروع يبدأ بالفهم.
`Thinking System → Writing System`، وليس `Writing System` فقط.

## الـ Workflow الكامل (بالترتيب الفعلي في `core/workflow.py`)

| # | المرحلة | النوع | الملف | تستخدم Skill؟ |
|---|---------|-------|-------|----------------|
| 1 | فهم المدخلات | Engine | `engines/input_intelligence.py` | - |
| 2 | فهم الموضوع | Engine | `engines/topic_understanding.py` | - |
| 3 | البحث | Engine | `engines/research.py` | - |
| 4 | بناء المعرفة | Engine | `engines/knowledge.py` | - |
| 5 | فهم الجمهور | Engine | `engines/audience.py` | - |
| 6 | الاستراتيجية | Engine | `engines/strategy.py` | `retention.plan()` |
| 7 | بناء الحكاية | Engine | `engines/story.py` | `retention.plan()` (إعادة ضبط) |
| 8 | صناعة الهوك | Engine | `engines/hook.py` | `voice_dna` (guidance) |
| 9 | كتابة السكريبت | Engine | `engines/script_writing.py` | `voice_dna` (guidance) |
| 10 | الإنسنة | **Skill** | `skills/humanization.py` | - |
| 11 | مراجعة الكتابة الرديئة | **Skill** | `skills/anti_slop.py` (`review`) | - |
| 12 | مراجعة الاحتفاظ | **Skill** | `skills/retention.py` (`review`) | - |
| 13 | مراجعة التكرار | **Skill** | `skills/anti_slop.py` (`repetition_check`) | - |
| 14 | تحرير اللهجة المصرية | Engine | `engines/egyptian_arabic_editing.py` | يطبّق نتائج 11+12+13 دفعة واحدة |
| 15 | فحص اتساق البصمة الصوتية | **Skill** | `skills/voice_dna.py` (`consistency_check`) | - |
| 16 | المراجعة النهائية كمشاهد | Engine | `engines/final_review.py` | - |
| 17 | التحرير النهائي | Engine | `engines/editor.py` → `final_script` | - |

## Context Flow
كل مرحلة بتاخد وترجع كائن واحد: `core.context.ProjectContext`. كل مرحلة
تكتب في حقلها فقط ولا تلمس حقول غيرها. الكائن بالكامل بيتحفظ في قاعدة
البيانات (Turso/SQLite) بعد كل مرحلة عبر `db/project_store.py`، وده اللي
بيخلي المشروع "قابل للاستكمال" (`ctx.completed_stages`).

## كفاءة الاستدعاءات
- كل مراجعة (Anti-Slop / Retention / Repetition) بتتنفذ **مرة واحدة فقط**.
- تعديلات المراجعات التلاتة بتتجمع وتتطبق **دفعة واحدة** في مرحلة
  `egyptian_arabic_editing`، بدل إعادة كتابة السكريبت 3 مرات منفصلة.
- `Editor Engine` (المرحلة الأخيرة) بيعمل استدعاء إضافي **فقط لو** المراجعة
  النهائية أو فحص البصمة الصوتية طلعوا نقاط لازم تتعالج - مش بشكل ثابت.
