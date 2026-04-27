# codex.md

<!-- TOC START -->

- No sections found
<!-- TOC END -->

OpenAI Codex instructions for this repository are defined in `AGENTS.md`.

- Read `AGENTS.md` §0 first.
- For simplify/refactor loops: run `qlty smells --all --sarif --include-tests > /tmp/qlty_smells-tests.json`, select one offender, reuse origin methods before creating helpers, use `model_validate(kwargs)` only for true option bags, keep fixed-shape APIs explicit with one packed validation, and gate the first edit with `ruff` then `pyrefly`.
- Use `.agents/skills/` for path-scoped, evidence-backed guidance.
- For broad simplification, deduplication, or contract-centralization work, load `.github/prompts/flext-aggressive-scale-refactor.prompt.md` after `AGENTS.md` and the path-scoped skills.
- Follow the canonical tool-routing rules for Scope, Serena, `ast-grep`, and MCP from `AGENTS.md` and `.agents/INSTRUCTION_SURFACE.md`.
- No raw gate output means the refactor lane is not done.
- Never use fallback instruction paths.
- Do not duplicate rules here; update `AGENTS.md` as the source of truth.
