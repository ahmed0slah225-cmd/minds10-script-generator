from core.contracts import SkillManifest

MANIFEST = SkillManifest(
    name="retention_ar_eg",
    version="1.0.0",
    skill_type="review",
    stage="review",
    engine="retention_review",
    description="منظومة الاحتفاظ الكاملة: loops، transitions، drop-risk.",
    depends_on=["storytelling_ar_eg", "viral_hooks_ar_eg"],
    requires_llm=True,
    input_schema={"text": "str"},
    output_schema={
        "open_loops": "list",
        "drop_risk_points": "list",
        "overall_retention_score": "int",
    },
)