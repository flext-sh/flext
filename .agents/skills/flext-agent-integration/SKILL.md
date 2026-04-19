---
name: flext-agent-integration
description: Use when setting up agent tooling, configuring MCP tools, or onboarding to the FLEXT development workflow. Covers skill discovery, tool priority ordering, session start protocols, and agent configuration for Claude Code, GitHub Copilot, and compatible agents.

---

# FLEXT Agent Integration

**Reviewed**: 2026-04-19 | **Scope**: Agent bootstrap and skill-loading efficiency

## Purpose

Use this skill to minimize startup overhead and load only the rules needed for the paths being edited.

## Canonical Load Order

1. `AGENTS.md` at repository root (normative project rules)
2. `CLAUDE.md` at repository root (pointer index)
3. Path-scoped skills only (from `.agents/skills/`)

Do not duplicate governance text in this skill.

## Path-to-Skill Routing

| Path pattern | Load first |
|---|---|
| `flext-core/**` | `rules-flext-core`, `flext-strict-typing` |
| `**/constants.py`, `**/models.py`, `**/protocols.py`, `**/typings.py`, `**/utilities.py`, `**/_models/**`, `**/_utilities/**` | `flext-mro-namespace-rules`, `flext-import-rules` |
| `scripts/**` | `rules-scripts` + matching `scripts-*` skill |
| `docs/**` | `rules-docs` |
| `.agents/skills/**` | `skill-format-universal`, `flext-docs-pointer-policy` |
| General typing failures | `flext-pyrefly-typecheck-fix`, `flext-strict-typing` |

## Session Checklist (Compact)

1. Identify touched paths.
2. Load only mapped skills for those paths.
3. Implement changes.
4. Validate with relevant gates (`ruff`/`pyrefly`/`pytest` or project make targets).

## Anti-Patterns

- Loading many unrelated skills “just in case”.
- Duplicating AGENTS policy into CLAUDE or skill files.
- Using this skill as normative law source (it is routing-only).
