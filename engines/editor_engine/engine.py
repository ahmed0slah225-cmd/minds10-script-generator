from services.gemini.generation import generate_text
from skills.registry import load
class EditorEngine:
 def __init__(self,client): self.client=client
 def finalize(self,script,reviews,knowledge):
  prompt=f"""أنت المحرر النهائي. أعد السكريبت كاملًا بعد تطبيق الإصلاحات الضرورية فقط. لا تضف معلومة غير موجودة في السكريبت أو المعرفة. لو reviewer قال إن claim غير مدعوم، احذفه أو صغه كاحتمال/ادعاء غير مؤكد بدل اختراعه. حافظ على العامية المصرية والصوت. لا تضف شرحًا خارج النص.
REVIEWS:{reviews}
KNOWLEDGE:{knowledge}
SCRIPT:{script}"""
  return generate_text(self.client.client if hasattr(self.client,'client') else self.client,prompt,system=load(['humanize','stop_slop','general_writing','addictive']),temperature=0.72,max_tokens=max(12000,len(script.split())*7))
