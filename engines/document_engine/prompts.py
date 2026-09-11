def identity_prompt(doc_excerpt):
 return f"""أنت محلل كتب. حلل النص التالي من بدايات PDF فقط. لا تخترع اسم الكتاب أو المؤلف.
استخرج JSON فيه: title, author, subject, language, confidence, clues.
النص:
{doc_excerpt}"""
