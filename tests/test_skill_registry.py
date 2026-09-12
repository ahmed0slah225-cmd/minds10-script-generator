from core.skill_registry import get_skill,validate_dependencies

def test_core_skills_registered():
    for name in ['viral_hooks_ar_eg','retention_ar_eg','humanize_ar_eg','anti_slop_ar_eg','truth_check_ar_eg','final_editor_ar_eg']:
        assert get_skill(name).name==name

def test_dependency_graph():
    assert validate_dependencies(['humanize_ar_eg','voice_dna_ar_eg'])==[]
