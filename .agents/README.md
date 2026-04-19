# .agents — Project Agent Assets

Canonical instruction-loading policy for this repository is defined in:

- `AGENTS.md` (normative governance)
- `CLAUDE.md` (load-order pointer)
- `.agents/INSTRUCTION_SURFACE.md` (single manifest for instruction sources)

This directory contains only project agent assets.

## Canonical Paths

- Skills: `.agents/skills/`
- Manifest: `.agents/INSTRUCTION_SURFACE.md`

## Non-Canonical Instruction Trees (must not be loaded)

- `.claude/skills/**`
- `.github/skills/**`
- `vendor/**`
- `.cache/**`
- `.venv/**`
- `**/dbt_packages/**`

Keep files here pointer-and-assets only; do not duplicate governance text from `AGENTS.md`.
