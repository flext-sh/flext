# .agents — Project Agent Assets

Canonical instruction-loading policy for this repository is defined in:

- `AGENTS.md` (normative governance)
- `CLAUDE.md` (load-order pointer)
- `.agents/INSTRUCTION_SURFACE.md` (single manifest for instruction sources)
- `.github/prompts/flext-aggressive-scale-refactor.prompt.md` (task-mode prompt for broad simplification/refactor work)

This directory contains only project agent assets.

## Canonical Paths

- Skills: `.agents/skills/`
- Manifest: `.agents/INSTRUCTION_SURFACE.md`
- Prompt: `.github/prompts/flext-aggressive-scale-refactor.prompt.md`

## Required Tooling Surfaces

- Scope routing and freshness rules live in `AGENTS.md` and `.agents/skills/code-navigation/SKILL.md`.
- Serena setup expectations live in `AGENTS.md`, `.vscode/mcp.json`, and `.serena/project.yml`.
- Structural propagation and static enforcement in `flext-infra` are rope-semantic only (`ast`/`ast-grep`/`get_ast` banned; memory:adr005-p3-single-rope-loop). See `AGENTS.md` and `.agents/skills/flext-refactoring-workflow/SKILL.md`.
- MCP routing expectations live in `AGENTS.md` and `.vscode/mcp.json`.

## Refactor Entry

- Read `AGENTS.md` §0 first for execution law.
- Run `qlty smells` first and close one offender only.
- Reuse canonical origin before helpers.
- Let owner `model_validate(kwargs)` / cached `TypeAdapter` own true option bags; keep fixed-shape APIs explicit and validate one packed payload.
- Missing raw `ruff`/`pyrefly` output means incomplete work.

## Non-Canonical Instruction Trees (must not be loaded)

- `.claude/skills/**`
- `.github/skills/**`
- `vendor/**`
- `.cache/**`
- `.venv/**`
- `**/dbt_packages/**`

Keep files here pointer-and-assets only; do not duplicate governance text from `AGENTS.md`.
