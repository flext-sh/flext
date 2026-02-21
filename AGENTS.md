# AGENTS.md — AI Agent Configuration Index


<!-- TOC START -->
- [Agent Configuration Map](#agent-configuration-map)
- [Maintenance Rules](#maintenance-rules)
- [Practical Usage](#practical-usage)
<!-- TOC END -->

**Reviewed**: 2026-02-17 | **Scope**: Pointer policy and mapping consistency


This repository uses multiple AI coding agents. All share a **single source of truth**
for project rules, architecture, and conventions: [`CLAUDE.md`](CLAUDE.md).

## Agent Configuration Map

| Agent                  | Config File                                                               | Role                                         |
| ---------------------- | ------------------------------------------------------------------------- | -------------------------------------------- |
| **Claude Code**        | [`CLAUDE.md`](CLAUDE.md)                                                  | Canonical — all rules defined here           |
| **Gemini Code Assist** | [`.gemini/styleguide.md`](.gemini/styleguide.md)                          | PR review priorities, delegates to CLAUDE.md |
| **GitHub Copilot**     | [`.github/copilot-instructions.md`](.github/copilot-instructions.md)      | Pointer to CLAUDE.md                         |
| **Cursor AI**          | [`.cursor/rules/flext.mdc`](.cursor/rules/flext.mdc)                      | Pointer to CLAUDE.md                         |
| **OpenAI Codex**       | [`codex.md`](codex.md)                                                    | Pointer to CLAUDE.md                         |
| **Cline**              | [`.clinerules`](.clinerules)                                              | Pointer to CLAUDE.md                         |
| **Windsurf**           | [`.windsurfrules`](.windsurfrules)                                        | Pointer to CLAUDE.md                         |
| **Continue.dev**       | [`.continue/rules/flext.md`](.continue/rules/flext.md)                    | Pointer to CLAUDE.md                         |
| **Aider**              | [`CONVENTIONS.md`](CONVENTIONS.md) + [`.aider.conf.yml`](.aider.conf.yml) | Auto-loads CONVENTIONS.md + CLAUDE.md        |

## Maintenance Rules

1. **All rule changes go to `CLAUDE.md` first** — agent-specific files only add tool-specific behavior.
2. **Never duplicate rules** across agent configs — reference `CLAUDE.md` sections instead.
3. **Agent-specific files must stay under 50 lines** — they are pointers, not copies.
4. When updating architecture, conventions, or quality gates, update `CLAUDE.md` only.

## Practical Usage

1. Start with root `CLAUDE.md`, then load scoped skills from `.claude/skills/` by touched path.
2. For `flext-core` changes, include `rules-flext-core` and matching `lib-*` skills for dependencies in scope.
3. For docs/governance changes, include `skill-format-universal` and `flext-docs-pointer-policy`.
4. Run `make validate-scripts` and `make check-clean` before finalizing workspace-wide governance edits.
5. In final reports, reference changed paths and provide validation evidence with concrete commands.

## Alignment and anti-drift

- Every project must stay aligned with `CLAUDE.md`, root `base.mk`, and the path-to-skill mapping (see CLAUDE.md § Skill Enforcement).
- Before claiming completion for policy or automation changes, run `make validate VALIDATE_SCOPE=workspace` and fix any failures.
- Before adding a new submodule or changing base.mk/scripts: run `make validate VALIDATE_SCOPE=workspace` and fix any failure.
- Changes to `base.mk`, shared `scripts/`, or `scripts/dependencies/modernize_pyproject.py` must be validated with `make validate VALIDATE_SCOPE=workspace` and with `make check` / `make validate` on affected projects.
- Baseline and per-project check status: see [.reports/validate/baseline-report.md](.reports/validate/baseline-report.md).
