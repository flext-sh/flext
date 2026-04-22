---
name: flext-agent-integration
description: Use when setting up agent tooling, configuring MCP tools, or enabling automatic project-context routing across FLEXT and non-FLEXT repositories. Covers skill discovery, tool priority ordering, session start protocols, safe tool guardrails, and agent configuration for Claude Code, GitHub Copilot, and compatible agents.

---

# FLEXT Agent Integration

**Reviewed**: 2026-04-19 | **Scope**: Agent bootstrap and skill-loading efficiency

## Scope

- Agent bootstrap and task-mode routing across FLEXT workspaces.
- Prompt and skill selection for GitHub Copilot, Claude Code, and compatible agents.

## References

- `AGENTS.md`
- `.agents/INSTRUCTION_SURFACE.md`
- `.github/copilot-instructions.md`
- `.github/prompts/flext-aggressive-scale-refactor.prompt.md`
- `.serena/project.yml`
- `.vscode/mcp.json`

## Rules

- Load `AGENTS.md` first, then `CLAUDE.md`, then path-scoped skills.
- Load a workspace prompt only when the request intent matches that task mode.
- Keep this skill routing-only; do not duplicate canonical governance here.
- Prefer the smallest relevant skill set for the touched paths.
- For any non-trivial task, verify whether `scope`, Serena, `ast-grep`, and configured MCP are applicable before proceeding.
- Do not allow broad edits, weakly justified edits, or incomplete propagation when the required tooling for impact analysis is available.
- If Scope is available, keep it fresh during the task (`scope index` or `scope workspace index` for multi-project work).
- If Serena is available, activate the workspace/project correctly and confirm its configuration before relying on Serena-based navigation or refactors.
- If `ast-grep` is required, prefer a tested structural pattern and confirmation pass over ad-hoc bulk text edits.
- Treat zero `ruff`, `pyrefly`, enforcement, and `pytest` debt as the steady-state requirement for all affected projects, not just the files touched by the current diff.

## Instructions

Use this skill to minimize startup overhead and load only the rules needed for the paths being edited.

## Canonical Load Order

1. `AGENTS.md` at repository root (normative project rules)
2. `CLAUDE.md` at repository root (pointer index)
3. Path-scoped skills only (from `.agents/skills/`)
4. Workspace prompt from `.github/prompts/` when the request is a task-mode match

Do not duplicate governance text in this skill.

## Workflow

1. Identify touched paths.
2. Identify whether the request intent matches a workspace prompt.
3. Check whether `scope` is available, whether Serena is configured/usable, and whether `ast-grep` or MCP is required by the task.
4. Load only the mapped skills for those paths.
5. Load the matching workspace prompt when the task mode requires it.
6. Implement changes.
7. Validate with relevant gates (`ruff`/`pyrefly`/`pytest` or project make targets).

## Path-to-Skill Routing

| Path pattern | Load first |
|---|---|
| `flext-core/**` | `rules-flext-core`, `flext-strict-typing` |
| `**/constants.py`, `**/models.py`, `**/protocols.py`, `**/typings.py`, `**/utilities.py`, `**/_models/**`, `**/_utilities/**` | `flext-mro-namespace-rules`, `flext-import-rules` |
| `scripts/**` | `rules-scripts` + matching `scripts-*` skill |
| `docs/**` | `rules-docs` |
| `.agents/skills/**` | `skill-format-universal`, `flext-docs-pointer-policy` |
| General typing failures | `flext-pyrefly-typecheck-fix`, `flext-strict-typing` |

## Intent-to-Prompt Routing

| Request intent | Load prompt |
|---|---|
| Simplify, deduplicate, remove wrappers, reduce pyrefly/ruff debt, centralize contracts, migrate to canonical facades | `.github/prompts/flext-aggressive-scale-refactor.prompt.md` |
| Narrow single-file fix with no broader refactor intent | none |

## Examples

Good:

- Request: "deduplicate wrapper services in flext-ldif and reduce pyrefly errors"
- Route: load `AGENTS.md`, path-scoped skills for `src/`, then `.github/prompts/flext-aggressive-scale-refactor.prompt.md`.

Bad:

- Request: "fix one typo in a README"
- Route: load the aggressive refactor prompt and a dozen unrelated skills.

Why bad: the task does not need a refactor task mode or unrelated skill loading.

Bad:

- Request: "rename a shared model used across multiple projects"
- Route: skip Scope, do no Serena setup, use plain search/replace, and stop after one local file is green.

Why bad: high-blast-radius structural work requires project-aware setup, structural tooling, and full propagation.

## Anti-Patterns

- Loading many unrelated skills “just in case”.
- Duplicating AGENTS policy into CLAUDE or skill files.
- Using this skill as normative law source (it is routing-only).
- Skipping the workspace refactor prompt for broad simplification or type-debt elimination requests.
- Skipping `scope`/Serena/`ast-grep`/MCP applicability checks and proceeding with a high-blast-radius change anyway.

## Verification

- `rg -n "^name:|^description:" .agents/skills/flext-agent-integration/SKILL.md`
- `for s in "## Scope" "## References" "## Rules" "## Instructions" "## Workflow" "## Examples" "## Verification"; do grep -q "$s" .agents/skills/flext-agent-integration/SKILL.md || echo "MISSING $s"; done`
- `rg -n "flext-aggressive-scale-refactor|task-mode" .agents/skills/flext-agent-integration/SKILL.md .agents/INSTRUCTION_SURFACE.md .github/copilot-instructions.md`
