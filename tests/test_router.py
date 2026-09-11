from core.orchestrator import plan
def test_build_route(): assert 'script' in plan('build_video').stages
def test_pdf_range_parser():
 from engines.input_engine import analyze
 x=analyze('اشرح من صفحة ١ إلى صفحة ٢٠',True); assert x.page_start==1 and x.page_end==20
