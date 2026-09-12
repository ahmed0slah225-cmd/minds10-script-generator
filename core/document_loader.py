from __future__ import annotations

def extract_uploaded_file(uploaded, page_start=None, page_end=None)->str:
    if uploaded is None: return ''
    name=uploaded.name.lower(); data=uploaded.getvalue()
    if name.endswith('.pdf'):
        try:
            import io
            from pypdf import PdfReader
            reader=PdfReader(io.BytesIO(data)); start=max(1,page_start or 1); end=min(len(reader.pages),page_end or len(reader.pages))
            return ''.join(f'\n[صفحة {i+1}]\n{reader.pages[i].extract_text() or ""}' for i in range(start-1,end))
        except Exception as exc: raise RuntimeError(f'فشل استخراج PDF: {exc}') from exc
    return data.decode('utf-8',errors='replace')
