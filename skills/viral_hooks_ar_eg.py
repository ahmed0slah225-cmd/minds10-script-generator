from core.contracts import SkillManifest

MANIFEST = SkillManifest(
    name="viral_hooks_ar_eg",
    version="1.0.0",
    skill_type="generation",
    stage="pre_write",
    engine="hook",
    description="توليد Hooks بدون Clickbait كاذب.",
    depends_on=["topic", "audience"],
    requires_llm=True,
    input_schema={"topic": "str", "angle": "str", "promise": "str"},
    output_schema={"hooks": "list", "selected": "str"},
)