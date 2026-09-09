from services.gemini.generation import generate_json
from skills.registry import load
class StrategyEngine:
 def __init__(self,client): self.client=client
 def run(self,topic,knowledge,duration,audience):
  prompt=f"""ابنِ استراتيجية فيديو. اطلع: viewer_problem, promise, 3-4 core_ideas, angles[], outline[]. الـoutline لازم يحتوي هدف كل جزء وعدد كلمات تقريبي. لا تحشر 10 أفكار.
الموضوع: {topic}
المدة: {duration}
الجمهور: {audience}
المعرفة: {knowledge}"""
  return generate_json(self.client.client if hasattr(self.client,'client') else self.client,prompt,system=load(['addictive','dumbify','storytelling','general_writing']),max_tokens=7000)
