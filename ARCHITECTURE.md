# Minds10 Architecture

المشروع لا يعتمد على Prompt واحد ضخم ولا على سلسلة Agents متصلبة. التصميم المقصود:

`Input → Understanding → Knowledge → Audience → Strategy → Story → Retention → Hook → Draft → Humanize → Anti-Slop → Egyptian Edit → Truth Check → Final`

## Engine vs Skill
- Engine = عملية كبيرة وتنسيق السياق.
- Skill = قدرة متخصصة يمكن أن تدخل أكثر من Engine.
- Reviewer لا يعمل ككاتب.
- Voice DNA ليست Humanizer.
- Anti-Slop يشخّص أولًا ثم يرسل الإصلاحات للمحرر.
- Retention ليست Hook Generator.

## Web boundary
قرار البحث يعيش في project context. إذا كان OFF فلا يتم إنشاء أداة البحث أصلًا. لا Skill تستطيع تجاوزه.

## Model boundary
الـEngines تستدعي Provider Adapter. أسماء الموديلات موجودة في `core/model_registry.py` فقط. هذا يسمح بإضافة مزودين لاحقًا دون إعادة كتابة الـworkflow.

## Source truth
كل معلومة يجب أن تحمل provenance في طبقة Knowledge مستقبلًا:
`user_provided | user_file | web_research | model_inference | unverified`

## Review loop
Reviewer → issues → priorities → suggested fixes → editor → recheck.
ليس Reviewer → rewrite whole script.

## Current first release
النسخة الأولى تركز على:
1. Streamlit UI.
2. Gemini provider.
3. Gemini 3.6 Flash كافتراضي.
4. Gemini 3.7 Flash كخيار.
5. Web Search OFF افتراضيًا ويمكن تشغيله من checkbox.
6. Research depth control.
7. Skill registry.
8. Deep skill specifications.

المراحل القادمة يمكن أن تفصل Engines إلى وحدات مستقلة، تضيف Knowledge Base وVoice DNA persistence وfile ingestion وstructured review artifacts دون تغيير واجهة اختيار الموديل أو سياسة البحث.
