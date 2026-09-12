from .deterministic_checks import pass_local_checks

def run_pre_final_checks(script:str):
    return pass_local_checks(script)
