---
name: flext-quality-gates
description: >-
  Select and run the narrowest decisive FLEXT validation before widening to
  project or workspace gates. Use for lint, formatting, typing, tests, docs,
  provider catalogs, and interpreting gate failures.
license: MIT
metadata:
  version: 2.0.0
---

# FLEXT Quality Gates

Gate commands validate the owning source. They do not define behavior,
configuration, catalog membership, or project type.

## Selection

| Changed surface | First gate | Native widening gate |
| --- | --- | --- |
| Python source | `ruff check <path> --no-fix` then `pyrefly check <path>` | affected behavior test or project check |
| Python formatting | `ruff format --check <path>` | project format gate |
| Markdown or skill | `markdownlint-cli2 <path>` | `make docs DOCS_PHASE=audit` |
| Provider TOML | typed parse plus exact declared-path inventory | provider projection probe |
| Make or tooling | `make help` plus targeted verb | `make check` or `make val` |
| Structural codemod | provider preview and exact expected cardinality | apply, rescan, and idempotence |

## Workflow

<!-- mro-wkii.17.26 (agent: codex) — require the complete continuous-green slice. -->
1. First edit → fresh-import smoke for every affected public module.
2. Same slice → Ruff check without fixes and Ruff format check.
3. Same slice → Pyrefly, Mypy, and Pyright with zero errors and warnings.
4. Same slice → narrow real-behavior pytest or the project Make test verb.
5. Same slice → `git diff --check`; record command, exit, and decisive output.

## Critical rules

- Fresh imports and all four lint/type analyzers are mandatory for touched code.
- Bare commands only; do not use `.venv/bin/` prefixes.
- Keep failure evidence in Beads: command, output, and exit code.
- Use check-only modes during validation. A mutating formatter/fixer is a
  separate reviewed change, never a hidden part of a gate.

## Gate commands

| Gate | Command |
|------|---------|
| Lint | `ruff check --no-fix <file>` |
| Format | `ruff format --check <file>` |
| Pyrefly | `pyrefly check <file>` |
| Mypy | `make check PROJECT=<project> FILES="<source files>" CHECK_GATES=mypy` |
| Pyright | `pyright <file>` |
| Project test | `make test PROJECT=<proj> MATCH=<expr>` |
| Workspace check | `make check CHANGED_ONLY=1` |
| Full validation | `make val VALIDATE_SCOPE=workspace` |

## Project-level gate values

Common values for `CHECK_GATES`: `lint`, `format`, `pyrefly`, `mypy`, `pyright`, `markdown`, `go`, `loc-cap`, `boundary`, `coordination`.

```bash
make help
make check PROJECT=<project> CHECK_GATES=<gates>
make test PROJECT=<project> MATCH=<expression>
make docs DOCS_PHASE=<generate|fix|audit|build|validate>
make val VALIDATE_SCOPE=workspace
```

The root `Makefile`, shared make framework, and `pyproject.toml` own available
verbs and thresholds. Do not mirror their changing values in this skill.

## Anti-patterns

| Anti-pattern | Fix |
|--------------|-----|
| Run broad `make val` before narrow gates | start with `ruff check <file>` |
| Use `.venv/bin/ruff` | use bare `ruff` |
| Ignore gate output | paste command + exit code + output into the bead |

## References

- [`flext-development-workflow`](../flext-development-workflow/SKILL.md)
- [`docs/GOVERNANCE.md`](../../../docs/GOVERNANCE.md)
- [`ADR-004`](../../../docs/architecture/adr/004-generic-make-framework-in-flext-tests.md)
