---
name: truth_check_ar_eg
version: 1.0.0
type: validation
phase: pre_final
requires_llm: true
---
# Truth Check

صنّف كل claim مهم إلى supported / uncertain / unverified. افصل user_provided وuser_file عن web_research، ولا تجعل model_inference evidence.

سجل source_id وlocation وpresented_as_fact والتعارضات. عند غياب الدليل استخدم «غير مؤكد» أو «يحتاج تحقق». ممنوع اختراع رقم أو اقتباس أو دراسة أو مصدر.