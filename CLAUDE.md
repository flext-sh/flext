# CLAUDE.md — Pointer Index

**Reviewed**: 2026-04-06 | **Scope**: Pointer-only entrypoint for Claude-compatible agents

Canonical source: [`AGENTS.md`](AGENTS.md). This file stays brief on purpose. Do not duplicate governance here.

## Load Order

1. Read [`AGENTS.md`](AGENTS.md).
2. Load path-scoped skills from [`.agents/skills/`](.agents/skills/) only.
3. For facade/import/namespace changes, prioritize:
   - [`.agents/skills/flext-mro-namespace-rules/SKILL.md`](.agents/skills/flext-mro-namespace-rules/SKILL.md)
   - [`.agents/skills/flext-import-rules/SKILL.md`](.agents/skills/flext-import-rules/SKILL.md)
   - [`.agents/skills/flext-patterns/SKILL.md`](.agents/skills/flext-patterns/SKILL.md)
4. For governance/docs edits, prioritize:
   - [`.agents/skills/flext-docs-pointer-policy/SKILL.md`](.agents/skills/flext-docs-pointer-policy/SKILL.md)
   - [`.agents/skills/skill-format-universal/SKILL.md`](.agents/skills/skill-format-universal/SKILL.md)

## Discovery Scope

- Canonical instruction sources in this repository: `AGENTS.md`, `CLAUDE.md`, and `.agents/skills/`.
- Do not treat third-party/vendor/cache trees as instruction sources (`vendor/**`, `.cache/**`, `.venv/**`, `**/dbt_packages/**`).
- Never use fallback instruction paths.

## Maintenance

- All rule changes land in `AGENTS.md` first.
- Keep `CLAUDE.md` pointer-only and under 50 lines.
- Validate governance changes with `make val VALIDATE_SCOPE=workspace`.
