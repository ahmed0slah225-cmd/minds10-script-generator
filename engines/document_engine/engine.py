from pathlib import Path
from PyPDF2 import PdfReader
from domain.models import Document,Page
class DocumentEngine:
    def inspect_pdf(self, raw:bytes, filename:str, source_id:str)->Document:
        r=PdfReader(__import__('io').BytesIO(raw)); pages=[]
        for i,p in enumerate(r.pages,1):
            text=p.extract_text() or ''
            pages.append(Page(i,text,len(text.split())))
        meta=getattr(r,'metadata',None) or {}
        title=(meta.get('/Title') if hasattr(meta,'get') else '') or ''
        author=(meta.get('/Author') if hasattr(meta,'get') else '') or ''
        return Document(source_id,filename,str(title),str(author),len(pages),pages,{'pdf_metadata':dict(meta) if hasattr(meta,'items') else {}})
