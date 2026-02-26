<!-- TOC START -->

- [Scope](#scope)
- [References](#references)
- [Rules](#rules)
- [Instructions](#instructions)
- [Workflow](#workflow)
- [Examples](#examples)
- [Verification](#verification)
<!-- TOC END -->

---

name: rules-cmd
description: Rules for command entrypoints under `cmd/` and their package wiring. Use when modifying command bootstrap files, CLI wrappers, or command-path docs.

---

# Rules Cmd

**Reviewed**: 2026-02-17 | **Scope**: Evidence-backed skill refresh and rule alignment

## Scope

- `cmd/flext/`
- `cmd/flext-cli/`
- `cmd/flext-control-panel/`
- `cmd/flext-demo/`
- `cmd/flext-server/`

## References

- `AGENTS.md`
- `Makefile`
- `cmd/flext/`
- `cmd/flext-cli/`

## Rules

- Keep command entrypoints thin: parse/dispatch/bootstrap only.
- Keep command paths and names consistent with directory names.
- Avoid embedding business logic directly in command wrappers.
- Ensure command examples are runnable from repository root.

## Instructions

- Verify target command directory exists before adding references.
- Anchor docs to actual command files/scripts under `cmd/<name>/`.
- When moving command code, update all docs and call paths in same change.

```bash
ls -la cmd
```

## Workflow

1. Identify command entrypoint being changed.
2. Verify invocation path from repository root.
3. Apply minimal bootstrap-level changes.
4. Update command references in docs/scripts if path changed.
5. Validate command directory structure remains coherent.

## Examples

Good:

```bash
python cmd/flext-demo/main.py --help
```

Why good: explicit command path and predictable root-relative invocation.

Bad:

```text
run the demo command module somehow
```

Why bad: ambiguous instruction that cannot be executed or validated.

## Verification

Make gates:

- `make check PROJECT=<name>` — verify project quality after command changes

File checks:

- `ls -la cmd`
- `rg -n "cmd/" docs README.md .claude/skills/*/SKILL.md`
- `rg -n "TODO|FIXME" cmd || true`
