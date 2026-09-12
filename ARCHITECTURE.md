# Minds Content Intelligence Platform

Minds is a production-oriented YouTube content system, not a text generator.

## Runtime graph
`Input Router → Topic Understanding → Source Analysis → Research(optional) → Knowledge → Audience → Strategy → Story → Retention → Hook → Script → Humanize → Anti-Slop Review → Repetition Review → Egyptian Editor → Voice Check → Truth Check → Final Editor`

## Non-negotiable boundaries
- Web Research is OFF by default and is a hard user-controlled gate.
- Engines never call Gemini directly; they call `LLMProvider`.
- Model choice comes from `model_registry`; no scattered model IDs.
- User sources and web research remain separate provenance classes.
- Reviewers diagnose; editors apply targeted fixes.
- Humanize never invents facts, personal experiences, sources or evidence.
- Truth wins over style, retention or voice.

## Engine vs Skill
Engine owns process, context, I/O, persistence boundary, validation and failure handling. Skill owns reusable method, rules, constraints and quality criteria.

## Quality loop
Draft → reviews → prioritized issues → smallest effective fixes → re-review → final gate.

## Persistence
`ProjectStore` is the adapter boundary. Local SQLite is available; `TursoStore` uses Turso's Python libSQL client when credentials are supplied.

## PDF
PDF input is scoped by page range and becomes a user-file source. The pipeline never assumes the whole document should be processed.
