import json
from services.gemini.generation import generate_json
class KnowledgeEngine:
 def __init__(self,client): self.client=client
 def run(self,topic,pdf_text='',research_text='',urls_text=''):
  prompt=f"""حوّل المادة التالية إلى قاعدة معرفة منظمة. لا تخترع أي معلومة. افصل الدليل عن الاستنتاج. رجّع JSON فيه: main_idea, key_points[], claims[], stories[], terms[], contradictions[], gaps[]. لكل claim ضع evidence وsource_type وpage_or_url إن وُجد.
الموضوع: {topic}
PDF:
{pdf_text}
WEB:
{research_text}
URLS:
{urls_text}"""
  return generate_json(self.client.client if hasattr(self.client,'client') else self.client,prompt,system='أنت مهندس معرفة لمحتوى يوتيوب بالعامية المصرية. لا تضيف حقائق خارج المادة المعطاة.',max_tokens=10000)
