# Minds Platform Layer

The repository is now split into core context/contracts/provider/model logic, engines for each production stage, reusable Arabic/Egyptian skills, storage adapters, and regression tests.

The current UI keeps Web Research OFF by default, exposes Gemini 3.6 Flash as the default model, supports Gemini 3.7 Flash, accepts scoped PDF input, supports Voice DNA extraction, and persists projects through a store adapter.