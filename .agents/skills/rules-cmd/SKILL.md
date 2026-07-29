---
name: rules-cmd
description: 'Rules for command entrypoints under `cmd/` and their package wiring. Use when modifying command bootstrap files, CLI wrappers, or command-path docs.'
license: MIT
metadata:
  version: 1.0.0
---
# Rules Cmd

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

## Verification

Make gates:

- `make check PROJECT=<name>` — verify project quality after command changes

File checks:

- `ls -la cmd`
- `rg -n "cmd/" docs README.md .agents/skills/*/SKILL.md`
- `rg -n "TODO|FIXME" cmd || true`
