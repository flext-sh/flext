# AGENTS.md — AI Agent Configuration Index

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
