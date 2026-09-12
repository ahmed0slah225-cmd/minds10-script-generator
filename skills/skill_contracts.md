# Skill Contract Standard

كل Skill في Minds لها: name, version, type, phase, inputs, outputs, invariants, dependencies, conflicts, execution policy, validation, tests, cost policy.

## أنواع التنفيذ
- deterministic: regex / statistics / schema / local rules.
- llm: reasoning or generation.
- hybrid: LLM proposal followed by deterministic validation.

## قواعد الصلاحيات
Reviewer لا يصبح Rewriter. Rewriter لا يملك صلاحية تغيير الحقيقة. Profile لا يُستخدم كقالب حرفي. Router لا يكتب. Search Engine وحده يملك صلاحية Web Search.
