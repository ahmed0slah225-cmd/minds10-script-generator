# -*- coding: utf-8 -*-
"""
Pipeline الـ13 عقل (Multi-agent pipeline) لتوليد سكريبت Minds10.

كل "عقل" هو نداء منفصل لـ Gemini بتعليمات (System Instruction) خاصة بيه،
وبياخد مخرجات العقول اللي قبله كسياق، ويسلّم مخرجاته للي بعده. التعليمات
الافتراضية هنا (DEFAULT_PROMPTS) قابلة للتعديل من واجهة التطبيق قبل كل
توليد - التطبيق بيبعتلنا التعليمات النهائية (افتراضية أو معدّلة) في
`agent_prompts`.

ملحوظة عن التكلفة: كل توليد سكريبت = 13 نداء لـ Gemini API (بدل نداء
واحد بس). العقول 3 و8 بس هما اللي بيستخدموا بحث مجاني (DuckDuckGo) -
باقي الـ11 عقل عبارة عن تفكير/كتابة نصية بس من غير أي بحث، يعني
شغالين على الخطة المجانية العادية من غير أي حاجة لها علاقة بـ Billing.
"""

import re
import time

from google import genai
from google.genai import types
from google.genai import errors as genai_errors

from research import gather_research, format_research_context

WORDS_PER_MINUTE = 145

CLICHE_OPENERS = [
    "لو بتحس إن",
    "لو بتصحى كل يوم",
    "تخيل معايا",
    "تخيل إنك",
    "تخيل إن",
    "هل عمرك حسيت",
    "في الفيديو ده هنتكلم عن",
]

AGENT_ORDER = [
    "analyzer", "ideas", "researcher", "why_care", "structure",
    "hook_writer", "critic", "articles", "script_writer",
    "retention", "repetition", "dialect", "final_review",
]

AGENT_TITLES = {
    "analyzer": "1. محلل الموضوع",
    "ideas": "2. فاهم الأفكار الرئيسية",
    "researcher": "3. باحث المعلومات",
    "why_care": "4. ليه الناس تهتم بالموضوع",
    "structure": "5. باني هيكلة الفيديو",
    "hook_writer": "6. كاتب الهوك",
    "critic": "7. الناقد والمعترض",
    "articles": "8. مقالات منشورة عن الموضوع",
    "script_writer": "9. كاتب السكريبت الكامل",
    "retention": "10. محافظ على الجمهور",
    "repetition": "11. مراجع التكرارات",
    "dialect": "12. محرر اللهجة العامية",
    "final_review": "13. المراجع النهائي (عين المشاهد)",
}

DEFAULT_PROMPTS = {
    "analyzer": """
انت "محلل موضوعات" متخصص في محتوى يوتيوب عربي. مهمتك الوحيدة إنك تحلل
الموضوع اللي هيتبعتلك وتطلع: (1) جوهر الموضوع في جملة واحدة، (2) المشاعر
الأساسية المرتبطة بيه عند المشاهد (خوف، طمع، فضول، غضب، أمل...)، (3)
مستوى تعقيده (بسيط / متوسط / عميق). اكتب تحليل مختصر وواضح بالعربي،
من غير أي مقدمات أو خاتمة، بس التحليل مباشرة.
""".strip(),

    "ideas": """
انت متخصص في استخراج الأفكار الرئيسية. من الموضوع والتحليل اللي هتاخده،
طلّع من 4 لـ 6 أفكار/زوايا رئيسية ممكن الفيديو يغطيها، كل فكرة في سطر
واحد بس مختصر. الأفكار لازم تكون متنوعة (مش كلها بتقول نفس الحاجة)
ومفيدة فعلاً للمشاهد. من غير مقدمات، اكتب الأفكار كقائمة نقطية بس.
""".strip(),

    "researcher": """
انت باحث معلومات. هتاخد نتائج بحث خام من الإنترنت عن الموضوع، ومطلوب
منك تلخصها في "ملخص بحثي" مختصر ومفيد: أهم الحقائق أو الأرقام أو
الدراسات اللي طلعت في النتائج (لو فيه)، منسوبة لمصدرها بشكل عام. لو
النتائج ضعيفة أو مفيهاش حاجة مفيدة، قول كده صراحة وميعنيش. ممنوع تخترع
أي رقم أو دراسة مش موجودة فعلاً في النتائج اللي هتاخدها.
""".strip(),

    "why_care": """
انت متخصص في نفسية الجمهور. مهمتك إنك تحدد بصراحة: ليه المشاهد
المصري العادي هيهتم بالموضوع ده تحديدًا دلوقتي؟ إيه الألم أو الرغبة
أو الفضول الحقيقي اللي الموضوع ده بيلمسه في حياته اليومية؟ اكتب 2-3
جمل مباشرة وصادقة، بعيد عن العموميات، توضح "زاوية الأهمية" اللي
هنستخدمها في بناء الهوك بعد كده.
""".strip(),

    "structure": """
انت مهندس هيكلة فيديوهات يوتيوب. من كل المعطيات اللي هتاخدها (الموضوع،
الأفكار الرئيسية، الملخص البحثي، وليه الناس مهتمة)، ابني هيكل الفيديو:
حدد عدد الأجزاء الرئيسية المطلوب (هيتقالك الرقم بالظبط)، وادي كل جزء
عنوان قصير وجملة توضح إيه اللي هيتغطى فيه وليه الترتيب ده منطقي. اكتب
الهيكل كقائمة مرقمة بس، من غير مقدمات.
""".strip(),

    "hook_writer": """
انت متخصص في كتابة هوكات (أول 10-15 ثانية) لفيديوهات يوتيوب عربي
بالعامية المصرية. اكتب 3 هوكات مختلفة تمامًا في الصياغة والزاوية عن
بعض (مش بس كلمات مرادفة)، كل هوك لازم يخاطب مشكلة أو ألم حقيقي
المشاهد عايشه دلوقتي بشكل مباشر من أول جملة. بعد الـ3 هوكات، اختار
"الأقوى" منهم واكتب سطر يقول "الهوك المختار:" ثم نص الهوك المختار
كامل. ممنوع منعًا باتًا تستخدم أي صياغة من قائمة الهوكات الممنوعة أو
تشابه أي هوك سابق هتاخده في السياق.
""".strip(),

    "critic": """
انت ناقد صارم ومتشكك، دورك إنك "تعترض" على الهوك والهيكل اللي هتاخدهم.
اسأل: هل الهوك ده فعلاً مختلف ومقنع ولا بيشبه كليشيهات شائعة؟ هل في
جزء من الهيكل حشو أو مكرر؟ هل في فكرة ضعيفة منطقيًا؟ اكتب نقدك في
نقاط مختصرة، وبعدها اكتب نسخة "معدّلة ونهائية" من الهوك والهيكل بعد
ما تصلح أي مشكلة لقيتها (حتى لو مفيش مشاكل كبيرة، حسّن الصياغة شوية
على الأقل). خلي آخر جزء من ردك واضح تحت عنوان "النسخة النهائية:".
""".strip(),

    "articles": """
انت باحث متخصص في تلخيص وجهات نظر ومقالات منشورة عن موضوع معين. هتاخد
نتائج بحث خام (مقالات، آراء، تدوينات) عن الموضوع، ومطلوب منك تطلع
"خلاصة وجهات نظر": إيه أهم الآراء أو الزوايا اللي الكتّاب أو الصحفيين
تناولوا بيها الموضوع ده، بشكل عام من غير اقتباس حرفي طويل. لو النتائج
ضعيفة، قول كده صراحة.
""".strip(),

    "script_writer": """
انت كاتب سكريبتات يوتيوب محترف متخصص في المحتوى العربي، بتكتب سكريبتات
طويلة بالعامية المصرية البسيطة لقناة اسمها Minds10. هتاخد: الهوك
والهيكل النهائي المعتمدين، الملخص البحثي، خلاصة وجهات النظر، ومعلومات
عن الجمهور والنبرة. اكتب السكريبت الكامل معتمدًا على كل ده بالحرف:

- ابدأ بالهوك المعتمد بالظبط كما هو (أو حسّنه شوية لو محتاج، بس خليه
  نفس الجوهر والزاوية).
- المقدمة: قصيرة، تربط الهوك بالموضوع، وتدي وعد واضح.
- الأجزاء: زي الهيكل المعتمد بالظبط، كل جزء بعنوان Markdown (##)،
  فيه شرح + مثال أو قصة + ربط بالمعلومات البحثية لو مناسب، من غير حشو.
- عامية مصرية بسيطة جدًا، جمل قصيرة، أسئلة شد كل شوية.
- الخاتمة: ملخص في جملتين + دعوة لفعل طبيعية.
- التزم بعدد الكلمات المطلوب (هيتقالك بالظبط) قد الإمكان.
- استخدم بنية Markdown: # الهوك / # المقدمة / ## اسم كل جزء / # الخاتمة.
- ممنوع تخترع أرقام أو دراسات مش موجودة في الملخص البحثي اللي اتديتلك.
""".strip(),

    "retention": """
انت متخصص في الاحتفاظ بالجمهور (Audience Retention) في فيديوهات
يوتيوب. هتاخد سكريبت كامل، ومهمتك تراجعه وتقوّي نقاط الشد فيه: زوّد
أو حسّن أسئلة الفضول، جمل التشويق ("بس اللي هيصدمك إن...")، والروابط
بين الأجزاء، في أي مكان حاسس إن الإيقاع ممكن يهبط أو المشاهد ممكن
يمل. حافظ على نفس المحتوى والمعنى والبنية والـ Markdown headers
بالظبط، بس حسّن الصياغة للشد فقط. رجّع السكريبت كامل بعد التحسين.
""".strip(),

    "repetition": """
انت مراجع تكرارات. هتاخد سكريبت كامل، وممكن تاخد كمان قائمة بهوكات
أو جمل استخدمناها في سكريبتات سابقة لنفس الموضوع. مهمتك: (1) تفحص
السكريبت الحالي لأي تكرار داخلي لنفس الفكرة أو الجملة بصياغات مختلفة،
(2) تتأكد إن الهوك والفقرات الأساسية مبتشابهش أي حاجة من القائمة
السابقة اللي هتاخدها. لو لقيت تكرار، أعد صياغة الجزء المكرر بس (من
غير ما تغير باقي السكريبت). رجّع السكريبت كامل سواء عدّلت فيه أو لأ.
""".strip(),

    "dialect": """
انت محرر لغوي متخصص في العامية المصرية الطبيعية. هتاخد سكريبت كامل،
ومهمتك تراجع كل جملة وتتأكد إنها عامية مصرية طبيعية 100% (مش فصحى
متقعرة، ومش عامية متكلفة)، زي ما ابن البلد بيتكلم فعلاً. صحّح أي جملة
حاسس إنها ركيكة أو رسمية أكتر من اللازم، من غير ما تغير المعنى أو
البنية أو الـ Markdown headers. رجّع السكريبت كامل بعد التحسين.
""".strip(),

    "final_review": """
انت المراجع الأخير، وهتقرأ السكريبت "كأنك مشاهد عادي" مش كمحرر. اسأل
نفسك: هل الهوك فعلاً هيخليني أكمل؟ هل في أي لحظة ملل أو حشو حسيته؟
هل الوعد اللي اتقال في المقدمة اتحقق فعلاً في الخاتمة؟ اعمل أي تعديلات
أخيرة صغيرة تحسّن التجربة (من غير ما تغير البنية العامة أو الـ
Markdown headers). اكتب أولاً نقاط مراجعتك تحت عنوان "## ملاحظات
المراجعة النهائية"، وبعدها اكتب السكريبت النهائي الكامل بعد أي تعديل
تحت عنوان "## السكريبت النهائي".
""".strip(),
}


def _client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


def _call_agent(client: genai.Client, model: str, system_instruction: str,
                 user_content: str, max_tokens: int = 4000) -> str:
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        max_output_tokens=max_tokens,
    )
    max_attempts = 3
    last_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            response = client.models.generate_content(
                model=model, contents=user_content, config=config,
            )
            return (response.text or "").strip()
        except genai_errors.ServerError as e:
            last_error = e
            if getattr(e, "code", None) == 503 and attempt < max_attempts:
                time.sleep(4 * attempt)
                continue
            raise
    raise last_error


def _max_parts(duration_min: int) -> int:
    return max(3, min(5, round(duration_min / 8)))


def extract_hook_text(script_text: str) -> str:
    match = re.search(r"#\s*الهوك\s*\n(.*?)(?=\n#\s|\Z)", script_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return script_text.strip().split("\n\n")[0].strip()


def extract_final_script(review_output: str) -> str:
    """يطلّع السكريبت النهائي من مخرجات عقل المراجعة الأخير."""
    match = re.search(r"##\s*السكريبت النهائي\s*\n(.*)", review_output, re.DOTALL)
    if match:
        return match.group(1).strip()
    return review_output.strip()


def run_pipeline(api_key: str, model: str, topic: str, audience: str,
                  tone: str, notes: str, duration_min: int,
                  use_free_research: bool, previous_hooks: list,
                  agent_prompts: dict, progress_callback=None):
    """
    بيشغل الـ13 عقل بالترتيب، ويرجع dict فيه:
      - final_script: السكريبت النهائي الجاهز للعرض
      - hook_text: نص الهوك المستخرج (لحفظه في قاعدة البيانات)
      - review_notes: ملاحظات المراجعة الأخيرة
      - sources: قايمة المصادر اللي اتلقت (من عقول البحث)
      - stage_outputs: dict فيه مخرجات كل عقل (للشفافية/التصحيح)
    progress_callback(stage_key, stage_title) بتتنادى قبل كل عقل لو
    اتبعتت، عشان تحدّث واجهة التقدم.
    """
    client = _client(api_key)
    stage_outputs = {}
    sources = []
    target_words = int(duration_min * WORDS_PER_MINUTE)
    max_parts = _max_parts(duration_min)

    def notify(key):
        if progress_callback:
            progress_callback(key, AGENT_TITLES[key])

    def prompt_for(key):
        return agent_prompts.get(key) or DEFAULT_PROMPTS[key]

    # 1) محلل الموضوع
    notify("analyzer")
    analysis = _call_agent(
        client, model, prompt_for("analyzer"),
        f"الموضوع: {topic}\nالجمهور المستهدف: {audience or 'عام'}\nالنبرة: {tone}",
        max_tokens=800,
    )
    stage_outputs["analyzer"] = analysis

    # 2) فاهم الأفكار الرئيسية
    notify("ideas")
    ideas = _call_agent(
        client, model, prompt_for("ideas"),
        f"الموضوع: {topic}\nتحليل الموضوع:\n{analysis}",
        max_tokens=800,
    )
    stage_outputs["ideas"] = ideas

    # 3) باحث المعلومات (بحث مجاني حقيقي)
    notify("researcher")
    research_brief = ""
    if use_free_research:
        raw_results = gather_research(topic, per_query_results=5)
        raw_context = format_research_context(raw_results)
        sources.extend(raw_results)
        if raw_context:
            research_brief = _call_agent(
                client, model, prompt_for("researcher"),
                f"الموضوع: {topic}\nنتائج بحث خام:\n{raw_context}",
                max_tokens=1200,
            )
        else:
            research_brief = "مفيش نتائج بحث كافية لهذا الموضوع."
    else:
        research_brief = "البحث المجاني معطّل، اعتمد على معرفتك العامة بس."
    stage_outputs["researcher"] = research_brief

    # 4) ليه الناس تهتم بالموضوع
    notify("why_care")
    why_care = _call_agent(
        client, model, prompt_for("why_care"),
        f"الموضوع: {topic}\nتحليل الموضوع:\n{analysis}\nالأفكار الرئيسية:\n{ideas}",
        max_tokens=600,
    )
    stage_outputs["why_care"] = why_care

    # 5) باني هيكلة الفيديو
    notify("structure")
    structure = _call_agent(
        client, model, prompt_for("structure"),
        f"الموضوع: {topic}\nعدد الأجزاء المطلوب بالظبط: {max_parts}\n"
        f"الأفكار الرئيسية:\n{ideas}\nالملخص البحثي:\n{research_brief}\n"
        f"ليه الناس مهتمة:\n{why_care}",
        max_tokens=1000,
    )
    stage_outputs["structure"] = structure

    # 6) كاتب الهوك
    notify("hook_writer")
    banned = "\n".join(f"- {h}" for h in CLICHE_OPENERS)
    prev = "\n".join(f"- {h[:200]}" for h in previous_hooks) or "(مفيش هوكات سابقة)"
    hook_draft = _call_agent(
        client, model, prompt_for("hook_writer"),
        f"الموضوع: {topic}\nليه الناس مهتمة:\n{why_care}\nهيكل الفيديو:\n{structure}\n\n"
        f"صياغات ممنوعة (كليشيهات):\n{banned}\n\n"
        f"هوكات سابقة لنفس الموضوع (ممنوع تشابهها):\n{prev}",
        max_tokens=1200,
    )
    stage_outputs["hook_writer"] = hook_draft

    # 7) الناقد والمعترض
    notify("critic")
    critique = _call_agent(
        client, model, prompt_for("critic"),
        f"الموضوع: {topic}\nمسودة الهوك:\n{hook_draft}\nهيكل الفيديو:\n{structure}",
        max_tokens=1500,
    )
    stage_outputs["critic"] = critique
    final_hook_and_structure = critique  # فيه "النسخة النهائية:" جواه

    # 8) مقالات منشورة عن الموضوع (بحث مجاني بزاوية تانية)
    notify("articles")
    articles_brief = ""
    if use_free_research:
        raw_articles = gather_research(f"{topic} مقالات وآراء", per_query_results=5)
        raw_articles_context = format_research_context(raw_articles)
        sources.extend(raw_articles)
        if raw_articles_context:
            articles_brief = _call_agent(
                client, model, prompt_for("articles"),
                f"الموضوع: {topic}\nنتائج بحث خام عن مقالات وآراء:\n{raw_articles_context}",
                max_tokens=1000,
            )
        else:
            articles_brief = "مفيش مقالات كافية اتلاقت لهذا الموضوع."
    else:
        articles_brief = "البحث المجاني معطّل."
    stage_outputs["articles"] = articles_brief

    # 9) كاتب السكريبت الكامل
    notify("script_writer")
    script_v1 = _call_agent(
        client, model, prompt_for("script_writer"),
        f"الموضوع: {topic}\nالجمهور: {audience or 'عام'}\nالنبرة: {tone}\n"
        f"ملاحظات صاحب القناة: {notes or '(لا يوجد)'}\n"
        f"عدد الكلمات المستهدف: حوالي {target_words} كلمة\n\n"
        f"الهوك والهيكل النهائي (بعد نقد):\n{final_hook_and_structure}\n\n"
        f"الملخص البحثي:\n{research_brief}\n\nخلاصة المقالات والآراء:\n{articles_brief}",
        max_tokens=16000,
    )
    stage_outputs["script_writer"] = script_v1

    # 10) محافظ على الجمهور
    notify("retention")
    script_v2 = _call_agent(
        client, model, prompt_for("retention"),
        f"السكريبت:\n{script_v1}", max_tokens=16000,
    )
    stage_outputs["retention"] = script_v2

    # 11) مراجع التكرارات
    notify("repetition")
    script_v3 = _call_agent(
        client, model, prompt_for("repetition"),
        f"السكريبت:\n{script_v2}\n\nهوكات/جمل سابقة لنفس الموضوع (تجنبها):\n{prev}",
        max_tokens=16000,
    )
    stage_outputs["repetition"] = script_v3

    # 12) محرر اللهجة العامية
    notify("dialect")
    script_v4 = _call_agent(
        client, model, prompt_for("dialect"),
        f"السكريبت:\n{script_v3}", max_tokens=16000,
    )
    stage_outputs["dialect"] = script_v4

    # 13) المراجع النهائي (عين المشاهد)
    notify("final_review")
    final_review_output = _call_agent(
        client, model, prompt_for("final_review"),
        f"السكريبت:\n{script_v4}", max_tokens=18000,
    )
    stage_outputs["final_review"] = final_review_output

    final_script = extract_final_script(final_review_output)
    review_notes_match = re.search(
        r"##\s*ملاحظات المراجعة النهائية\s*\n(.*?)(?=\n##\s*السكريبت النهائي|\Z)",
        final_review_output, re.DOTALL,
    )
    review_notes = review_notes_match.group(1).strip() if review_notes_match else ""

    hook_text = extract_hook_text(final_script)

    return {
        "final_script": final_script,
        "hook_text": hook_text,
        "review_notes": review_notes,
        "sources": sources,
        "stage_outputs": stage_outputs,
    }
