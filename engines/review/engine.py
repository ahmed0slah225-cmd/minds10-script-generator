from engines.base import LLMEngine
from core.models import ReviewResult,ReviewIssue

class ReviewEngine(LLMEngine):
    name='anti_slop_review'; skill='anti_slop_ar_eg'; temperature=.4

    def task(self,ctx):
        return '''راجع المسودة فقط ولا تعِد كتابتها. قيّم naturalness, information_density, clarity, language_strength, ai_feel من 1-10. اكتشف filler, genericity, fake depth, repetition, canned transitions, excess formality, mechanical phrasing, significance inflation. لكل issue: location, problem, reason, suggested_fix, severity, priority. مهم جدًا: priority يجب أن تكون رقمًا صحيحًا من 1 إلى 5، حيث 1 أعلى أولوية و5 أقل أولوية. لا تكتب high/medium/low داخل priority. Minimum Effective Editing.'''

    def apply(self,ctx,d):
        issues=[]
        priority_map={'critical':1,'high':1,'urgent':1,'medium':3,'normal':3,'low':5}
        for i,x in enumerate(d.get('issues',[])):
            item=dict(x)
            raw=item.get('priority',3)
            if isinstance(raw,str):
                value=priority_map.get(raw.strip().lower())
                if value is None:
                    try:
                        value=int(raw.strip())
                    except ValueError:
                        value=3
                item['priority']=max(1,min(5,value))
            else:
                try:
                    item['priority']=max(1,min(5,int(raw)))
                except (TypeError,ValueError):
                    item['priority']=3
            issues.append(ReviewIssue(id=f'issue-{i}',reviewer='anti_slop',**item))
        ctx.state.reviews.append(ReviewResult(reviewer='anti_slop',passed=bool(d.get('passed',False)),scores=d.get('scores',{}),issues=issues,summary=d.get('summary',''))); ctx.state.metadata['anti_slop']=d
