from __future__ import annotations
import re

BANNED_OPENERS=['أهلاً بكم','اهلا بكم','في فيديو النهاردة','في هذا الفيديو سنتحدث']

def text_checks(script:str)->dict:
    checks={'has_script':bool(script.strip()),'banned_openers':[],'length_chars':len(script),'short_fragment_ratio':0.0}
    first=script[:500]
    checks['banned_openers']=[x for x in BANNED_OPENERS if x in first]
    sentences=[s.strip() for s in re.split(r'[.!؟]+',script) if s.strip()]
    if sentences: checks['short_fragment_ratio']=round(sum(len(s)<18 for s in sentences)/len(sentences),3)
    return checks

def pass_local_checks(script:str)->tuple[bool,list[str]]:
    c=text_checks(script); errors=[]
    if not c['has_script']: errors.append('السكريبت فارغ.')
    if c['banned_openers']: errors.append('بداية تحتوي افتتاحيات ممنوعة: '+', '.join(c['banned_openers']))
    if c['short_fragment_ratio']>.55: errors.append('الإيقاع يبدو متقطعًا أكثر من اللازم في الفحص المحلي.')
    return not errors,errors
