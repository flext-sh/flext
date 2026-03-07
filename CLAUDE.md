# CLAUDE.md — AI Agent Configuration Index

<!-- TOC START -->

- [Agent Configuration Map](#agent-configuration-map)
- [Maintenance Rules](#maintenance-rules)
- [Practical Usage](#practical-usage)
<!-- TOC END -->

**Reviewed**: 2026-02-17 | **Scope**: Pointer policy and mapping consistency

This repository uses multiple AI coding agents. All share a **single source of truth**
for project rules, architecture, and conventions: [`AGENTS.md`](AGENTS.md).

## Agent Configuration Map

| Agent                  | Config File                                                               | Role                                         |
| ---------------------- | ------------------------------------------------------------------------- | -------------------------------------------- |
| **Claude Code**        | [`AGENTS.md`](AGENTS.md)                                                  | Canonical — all rules defined here           |
| **Gemini Code Assist** | [`.gemini/styleguide.md`](.gemini/styleguide.md)                          | PR review priorities, delegates to AGENTS.md |
| **GitHub Copilot**     | [`.github/copilot-instructions.md`](.github/copilot-instructions.md)      | Pointer to AGENTS.md                         |
| **Cursor AI**          | [`.cursor/rules/flext.mdc`](.cursor/rules/flext.mdc)                      | Pointer to AGENTS.md                         |
| **OpenAI Codex**       | [`codex.md`](codex.md)                                                    | Pointer to AGENTS.md                         |
| **Cline**              | [`.clinerules`](.clinerules)                                              | Pointer to AGENTS.md                         |
| **Windsurf**           | [`.windsurfrules`](.windsurfrules)                                        | Pointer to AGENTS.md                         |
| **Continue.dev**       | [`.continue/rules/flext.md`](.continue/rules/flext.md)                    | Pointer to AGENTS.md                         |
| **Aider**              | [`CONVENTIONS.md`](CONVENTIONS.md) + [`.aider.conf.yml`](.aider.conf.yml) | Auto-loads CONVENTIONS.md + AGENTS.md        |

## Maintenance Rules

1. **All rule changes go to `AGENTS.md` first** — agent-specific files only add tool-specific behavior.
2. **Never duplicate rules** across agent configs — reference `AGENTS.md` sections instead.
3. **Agent-specific files must stay under 50 lines** — they are pointers, not copies.
4. When updating architecture, conventions, or quality gates, update `AGENTS.md` only.

## Practical Usage

1. Start with root `AGENTS.md`, then load scoped skills from `.claude/skills/` by touched path.
2. For `flext-core` changes, include `rules-flext-core` and matching `lib-*` skills for dependencies in scope.
3. For docs/governance changes, include `skill-format-universal` and `flext-docs-pointer-policy`.
4. Run `make validate VALIDATE_SCOPE=workspace` and `make check` before finalizing workspace-wide governance edits.
5. In final reports, reference changed paths and provide validation evidence with concrete commands.

## Alignment and anti-drift

- Every project must stay aligned with `AGENTS.md`, root `base.mk`, and the path-to-skill mapping (see AGENTS.md § Skill Enforcement).
- Before claiming completion for policy or automation changes, run `make validate VALIDATE_SCOPE=workspace` and fix any failures.
- Before adding a new submodule or changing base.mk/scripts: run `make validate VALIDATE_SCOPE=workspace` and fix any failure.
- Changes to `base.mk`, shared `scripts/`, or `scripts/dependencies/modernize_pyproject.py` must be validated with `make validate VALIDATE_SCOPE=workspace` and with `make check` / `make validate` on affected projects.
- Baseline and per-project check status: see [.reports/validate/refactoring-baseline.md](.reports/validate/refactoring-baseline.md).

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd sync
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
