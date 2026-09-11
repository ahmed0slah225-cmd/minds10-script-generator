from core.contracts import SkillManifest

MANIFEST = SkillManifest(
    name="anti_slop_ar_eg",
    version="1.0.0",
    skill_type="review",
    stage="review",
    engine="anti_slop",
    description="كشف الانزلاق (AI Slop) بمعايير منظمة.",
    depends_on=["humanize_ar_eg"],
    requires_llm=True,
    input_schema={"text": "str"},
    output_schema={
        "scores": {
            "naturalness": "int",
            "information_density": "int",
            "clarity": "int",
            "language_strength": "int",
            "ai_feel": "int",
        },
        "issues": "list",
    },
)