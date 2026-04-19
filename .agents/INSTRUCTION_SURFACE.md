# Instruction Surface Manifest

Single manifest for instruction loading in this repository.

## Canonical Loading Precedence

1. `AGENTS.md` (normative policy)
2. `CLAUDE.md` (routing and skill selection)
3. `.agents/skills/` (path-scoped skills)

No other tree is canonical for project instruction loading.

## Canonical Pointer Files (must remain pointer-only)

- `.github/copilot-instructions.md`
- `.clinerules`
- `.windsurfrules`
- `.continue/rules/flext.md`
- `.cursor/rules/flext.mdc`
- `.gemini/styleguide.md`
- `codex.md`
- `CONVENTIONS.md`

Required pointer behavior:

- Reference `AGENTS.md` as canonical governance.
- Reference `.agents/skills/` as the only project skill root.
- Never use fallback instruction paths.
- Avoid duplicated policy text.

## Non-Canonical Discovery Trees (must be ignored)

- `.venv/**`
- `.cache/**`
- `vendor/**`
- `**/dbt_packages/**`
- `.claude/skills/**`
- `.github/skills/**`
