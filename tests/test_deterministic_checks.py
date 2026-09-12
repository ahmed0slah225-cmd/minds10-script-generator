from core.deterministic_checks import pass_local_checks

def test_good_text_passes():
    ok,errors=pass_local_checks('ده نص طبيعي فيه فكرة واضحة وجملة مفهومة. وبعدين نقطة تانية.')
    assert ok and not errors

def test_bad_opener_fails():
    ok,errors=pass_local_checks('أهلاً بكم في فيديو جديد. دلوقتي هنبدأ.')
    assert not ok
