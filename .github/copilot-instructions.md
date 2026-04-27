# GitHub Copilot Instructions

Canonical source: [`AGENTS.md`](../AGENTS.md).

Use this file as an entrypoint only.

- Read [`AGENTS.md`](../AGENTS.md) §0 first, not just the file generally.
- Start every refactor lane with one offender, `qlty smells --all --sarif --include-tests > /tmp/qlty_smells-tests.json`, origin search before helper, and `ruff` -> `pyrefly` immediately after the first edit.
- Let Pydantic own payloads: true option bags use `model_validate(kwargs)`, fixed-shape APIs keep explicit typed params plus one packed validation, and `model_copy(update=...)` / cached `TypeAdapter` / declarative validators beat manual normalization.
- Load [`flext-context-routing`](../.agents/skills/flext-context-routing/SKILL.md) to auto-select tools/MCP/skills by context.
- Load scoped rules from `.agents/skills/` for the files being changed.
- For broad simplification, deduplication, pyrefly/ruff reduction, or contract-centralization requests, load [`.github/prompts/flext-aggressive-scale-refactor.prompt.md`](./prompts/flext-aggressive-scale-refactor.prompt.md) after `AGENTS.md` and the path-scoped skills.
- Never use fallback instruction paths.
- Do not duplicate governance here; update `AGENTS.md` for normative policy changes.
- Keep this file concise and pointer-only.
