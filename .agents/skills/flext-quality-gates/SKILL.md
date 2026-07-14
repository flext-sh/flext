---
name: flext-quality-gates
description: 'Use when running or interpreting quality gates (lint, typecheck, test,
  val) in the FLEXT monorepo. Covers mandatory gate definitions, exact tool commands
  (ruff, pyrefly, pyright, mypy, pytest), pass thresholds, and configuration sources
  from base.mk and pyproject.toml. DO NOT USE FOR: questions unrelated to flext-quality-gates
  creating projects or architecture from scratch'
license: MIT
metadata:
  version: 1.1.0
---
# FLEXT Quality Gates

**UTILITY SKILL**

Commands and thresholds for the FLEXT quality gates.

## USE FOR

- Running lint, format, typecheck, or test gates.
- Interpreting failures from `make check` or CI.
- Choosing the narrowest gate for a changed file.

## DO NOT USE FOR

- Questions unrelated to FLEXT quality gates.
- Creating projects or architecture from scratch.

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
make check PROJECT=flext-core CHECK_GATES=pyrefly
```

## Coverage

`pyproject.toml` sets `fail_under = 45` for the consolidated workspace. Project-local targets may be higher.

## Anti-patterns

| Anti-pattern | Fix |
|--------------|-----|
| Run broad `make val` before narrow gates | start with `ruff check <file>` |
| Use `.venv/bin/ruff` | use bare `ruff` |
| Run `ruff --fix` inside a gate | emit and review an explicit fix transaction |
| Run `mypy --no-incremental` or pass test modules directly | use the cached Make gate on production source paths; validate tests with Ruff, Pyrefly, Pyright, and pytest |
| Treat one type checker as proof for all | run Pyrefly, Mypy, and Pyright |
| Ignore gate output | paste command + exit code + output into the bead |

## References

<!-- mro-lo34 (agent: kimi) — canonical ADR refs added per docs-renaissance S1. -->
- `.agents/skills/coding-standards/SKILL.md` — general coding standards
- `.agents/skills/flext-development-workflow/SKILL.md` — workflow and CI/CD
- `docs/architecture/adr/004-generic-make-framework-in-flext-tests.md` — make framework contract behind the gate verbs
- `docs/architecture/adr/005-config-settings-constants-templates-schemas-ssot.md` — config/template SSOT
- `AGENTS.md` — verification expectation
