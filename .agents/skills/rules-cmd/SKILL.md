---
name: rules-cmd
description: 'Use this skill to rules for command entrypoints under `cmd/` and their
  package wiring. Use when modifying command bootstrap files, CLI wrappers, or command-path
  docs. **Reviewed**: 2026-02-17 | **Scope**: Evidence-backed skill refresh and rule
  alignment. DO NOT USE FOR: questions unrelated to rules-cmd creating projects or
  architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---

# Rules Cmd

**UTILITY SKILL**

## Rules

- `AGENTS.md` is canonical; keep this skill limited to `cmd/` entrypoint guidance and do not duplicate broader governance here.
- Keep command entrypoints thin: parse/dispatch/bootstrap only.
- Keep command paths and names consistent with directory names.
- Avoid embedding business logic directly in command wrappers.
- Ensure command examples are runnable from repository root.

## Instructions

- Verify target command directory exists before adding references.
- Anchor docs to actual command files/scripts under `cmd/<name>/`.
- When moving command code, update all docs and call paths in same change.

## Workflow

1. Identify command entrypoint being changed.
2. Verify invocation path from repository root.
3. Apply minimal bootstrap-level changes.

## Examples

Good:

Why good: explicit command path and predictable root-relative invocation.

Bad:

Why bad: ambiguous instruction that cannot be executed or validated.

## Verification

Make gates:

- `make check PROJECT=<name>` — verify project quality after command changes

File checks:

- `ls -la cmd`
- `rg -n "cmd/" docs README.md .agents/skills/*/SKILL.md`
- `rg -n "TODO|FIXME" cmd || true`

## USE FOR

- Requests about rules cmd.
- Workflows described in this skill.
- Operator tasks within this scope.

## DO NOT USE FOR

- questions unrelated to rules-cmd.
- creating projects or architecture from scratch.

## Critical rules

- Prefer canonical sources.
- Require evidence before claiming success.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
- Missing context → state assumptions.
