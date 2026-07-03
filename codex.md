# codex.md

<!-- TOC START -->

- No sections found
<!-- TOC END -->

OpenAI Codex instructions for this repository are pointer-only. Policy lives in `AGENTS.md`.

- Read `AGENTS.md` §0 first.
- `qlty` first. One offender only. Stale offender -> rerun `qlty` immediately.
- Generated / auto-generated files are invalid smell lanes unless the generator itself is the target.
- Reuse origin methods before creating helpers. Single-caller private helper -> inline delete.
- Parameter-count smell does not justify widened kwargs or a new carrier model. Reuse the owner model, enum, or `match/case` first.
- True option bags use `model_validate(kwargs)` once. Fixed-shape APIs stay explicit and use one packed `model_validate({...})`.
- Manual kwargs key/type normalization is invalid when Pydantic can own payload.
- Gate the first edit with `ruff` then `pyrefly`.
- Use `.agents/skills/` for path-scoped, evidence-backed guidance.
- For broad simplification, deduplication, or contract-centralization work, load `.github/prompts/flext-aggressive-scale-refactor.prompt.md` after `AGENTS.md` and the path-scoped skills.
- Follow the canonical tool-routing rules for Scope, Serena, `ast-grep`, and MCP from `AGENTS.md` and `.agents/INSTRUCTION_SURFACE.md`.
- No raw gate output means the refactor lane is not done.
- Never use fallback instruction paths.
- Do not duplicate rules here; update `AGENTS.md` as the source of truth.
