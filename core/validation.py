from .models import ProjectState

def final_gate(state:ProjectState)->tuple[bool,list[str]]:
    errors=[]
    if not state.final_script.strip(): errors.append('لا توجد نسخة نهائية.')
    if not state.metadata.get('selected_hook') and not state.hook_set: errors.append('لا يوجد Hook معتمد.')
    if not state.strategy: errors.append('لا توجد استراتيجية.')
    truth=state.metadata.get('truth_check',{})
    for claim in truth.get('claims',[]):
        if claim.get('status')=='unverified' and claim.get('presented_as_fact',True): errors.append('يوجد claim غير متحقق منه بصياغة جازمة.')
    return (not errors,errors)
