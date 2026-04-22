# GitHub Copilot Instructions

Canonical source: [`AGENTS.md`](../AGENTS.md).

Use this file as an entrypoint only.

- Read and follow [`AGENTS.md`](../AGENTS.md) first.
- Load [`flext-context-routing`](../.agents/skills/flext-context-routing/SKILL.md) to auto-select tools/MCP/skills by context.
- Load scoped rules from `.agents/skills/` for the files being changed.
- For broad simplification, deduplication, pyrefly/ruff reduction, or contract-centralization requests, load [`.github/prompts/flext-aggressive-scale-refactor.prompt.md`](./prompts/flext-aggressive-scale-refactor.prompt.md) after `AGENTS.md` and the path-scoped skills.
- Never use fallback instruction paths.
- Do not duplicate governance here; update `AGENTS.md` for normative policy changes.
- Keep this file concise and pointer-only.
