from services.gemini.generation import generate_json
from skills.registry import load
class ReviewEngine:
 def __init__(self,client): self.client=client
 def review(self,script,knowledge):
  prompt=f"""راجع السكريبت بصرامة. رجّع JSON: retention_score, naturalness_score, factual_risk_score, style_score, issues[], unsupported_claims[], repeated_patterns[], best_fixes[]. لا تعيد كتابة السكريبت.
السكريبت:{script}
المعرفة:{knowledge}"""
  return generate_json(self.client.client if hasattr(self.client,'client') else self.client,prompt,system=load(['stop_slop','addictive','general_writing']),max_tokens=7000)
