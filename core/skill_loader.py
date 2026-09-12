from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SKILLS_ROOT=ROOT/'skills'

def load_skill(name:str)->str:
    path=SKILLS_ROOT/name/'SKILL.md'
    if not path.exists(): raise FileNotFoundError(f'Skill not found: {name}')
    return path.read_text(encoding='utf-8')

def load_references(name:str)->dict[str,str]:
    return {p.name:p.read_text(encoding='utf-8') for p in (SKILLS_ROOT/name/'references').glob('*.md')}
