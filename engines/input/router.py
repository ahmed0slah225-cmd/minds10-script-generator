from core.context import PipelineContext


def input_router(ctx: PipelineContext, llm=None):
    text = ctx.state.input_text.strip()
    kind = "text"
    if text.lower().endswith(".pdf"):
        kind = "pdf_reference"
    elif text.startswith(("http://", "https://")):
        kind = "url"
    elif len(text) < 160:
        kind = "idea_or_title"
    elif "\n" in text:
        kind = "draft_or_notes"

    ctx.state.metadata["input_type"] = kind
    ctx.record("input_router", input_type=kind)


# Backward-compatible alias for any older internal imports.
route_input = input_router
