from core.contracts import SkillManifest

MANIFEST = SkillManifest(
    name="dumpify_ar_eg",
    version="1.0.0",
    skill_type="rewrite",
    stage="post_write",
    engine="humanize",
    description="تبسيط بدون تسطيح.",
    depends_on=[],
    requires_llm=True,
    input_schema={"text": "str"},
    output_schema={"simplified": "str"},
)