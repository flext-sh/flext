---
name: flext-agent-integration
description: Guide for using MCP tools, skills, and agents in the FLEXT development workflow. Use at session start or when configuring agent tooling for FLEXT work.
---

# FLEXT Agent Integration

**Reviewed**: 2026-02-17 | **Scope**: Disabled skill revival

## Scope

- Agent and tool configuration for FLEXT development sessions
- `.claude/skills/` — skill loading and selection
- `CLAUDE.md`, `AGENTS.md` — canonical agent configuration

## References

- `CLAUDE.md` — canonical project rules
- `AGENTS.md` — agent configuration index
- `.claude/skills/skill-format-universal/SKILL.md` — skill format

## Rules

- Load relevant skills based on the files being touched (e.g., `rules-flext-core` for `flext-core/` changes).
- Use `mcp_memory` for cross-session context — search before implementing to avoid duplicating past work.
- Use Context7 (`mcp_context7_resolve-library-id` + `mcp_context7_query-docs`) for external library documentation.
- Start sessions by checking `CLAUDE.md` for current project rules and conventions.
- Prefer `make validate` for verification over ad-hoc lint/type-check commands.

## Instructions

### Session Start Checklist

1. Check `CLAUDE.md` for current project rules.
2. Search memory for recent context on the task area: `mcp_memory(mode="search", query="<topic>")`.
3. Load path-appropriate skills based on files to be modified.
4. Check for open work items: `bd ready`.

### Skill Selection by Path

| Path Pattern | Skills to Load |
|---|---|
| `flext-core/` | `rules-flext-core`, `lib-returns`, `flext-strict-typing` |
| `flext-core/src/flext_core/result.py` | `lib-returns` |
| `flext-core/src/flext_core/settings.py` | `lib-pydantic-settings` |
| `scripts/validation/` | `scripts-validation` |
| `scripts/` | `rules-scripts`, `scripts-infra` |
| `.claude/skills/` | `skill-format-universal` |
| `docs/` | `rules-docs` |
| `Makefile` | `flext-development-workflow` |
| `*.py` (any model) | `lib-pydantic-v2` |

### Memory Search Patterns

```
mcp_memory(mode="search", query="architecture decision for <topic>")
mcp_memory(mode="search", query="implementation pattern for <module>")
mcp_memory(mode="search", query="recent changes to <file>")
```

### Context7 for Library Docs

```
mcp_context7_resolve-library-id(libraryName="pydantic", query="validators")
mcp_context7_query-docs(libraryId="/pydantic/pydantic", query="field_validator examples")
```

## Workflow

1. Start with `CLAUDE.md` and `AGENTS.md` for project configuration.
2. Search memory for relevant prior work and decisions.
3. Load path-specific skills before making changes.
4. Use Context7 when working with unfamiliar library APIs.
5. Run `make validate` before reporting completion.
6. Store significant decisions in memory for future sessions.

## Examples

Good:

```
# Before modifying flext-core result.py:
Load skills: rules-flext-core, lib-returns, flext-strict-typing
Search memory: "FlextResult recent changes"
```

Why good: loads relevant skills and checks prior context before making changes.

Bad:

```
# Immediately edit flext-core/src/flext_core/result.py without loading any skills
```

Why bad: misses project-specific rules, naming conventions, and recent context that prevent regressions.

## Verification

```bash
ls .claude/skills/*/SKILL.md | wc -l
rg -n "^name:" .claude/skills/*/SKILL.md | head -10
cat CLAUDE.md | head -20
cat AGENTS.md | head -20
```
