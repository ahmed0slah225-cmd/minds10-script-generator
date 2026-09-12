from engines.base import LLMEngine
from core.models import ReviewResult,ReviewIssue
class ReviewEngine(LLMEngine):
    name='anti_slop_review'; skill='anti_slop_ar_eg'; temperature=.4
    def task(self,ctx): return 'راجع المسودة فقط ولا تعِد كتابتها. قيّم naturalness, information_density, clarity, language_strength, ai_feel من 1-10. اكتشف filler, genericity, fake depth, repetition, canned transitions, excess formality, mechanical phrasing, significance inflation. لكل issue: location, problem, reason, suggested_fix, severity, priority. Minimum Effective Editing.'
    def apply(self,ctx,d):
        issues=[ReviewIssue(id=f'issue-{i}',reviewer='anti_slop',**x) for i,x in enumerate(d.get('issues',[]))]
        ctx.state.reviews.append(ReviewResult(reviewer='anti_slop',passed=bool(d.get('passed',False)),scores=d.get('scores',{}),issues=issues,summary=d.get('summary',''))); ctx.state.metadata['anti_slop']=d
