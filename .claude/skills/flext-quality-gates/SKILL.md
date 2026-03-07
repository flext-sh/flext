<!-- TOC START -->

- [Standardized Make Gate Surface](#standardized-make-gate-surface)
- [Workspace Automation Selectors](#workspace-automation-selectors)
- [Thresholds Summary](#thresholds-summary)
- [When to Run Which Gate](#when-to-run-which-gate)
<!-- TOC END -->

---

name: flext-quality-gates
description: Mandatory verification gates with exact tool commands, thresholds, and configuration sources from base.mk and pyproject.toml

---

# FLEXT Quality Gates

**Reviewed**: 2026-02-19 | **Scope**: Coverage source-of-truth migration to pyproject.toml

> **Source of truth**: Verified from `base.mk` (`check`, `test`, and `validate` targets), `ruff-shared.toml`,
> and individual `pyproject.toml` files on 2026-02-19.

## Scope

- Mandatory quality-gate execution for workspace and project-level changes.
- Verification semantics for `make check`, `make test`, `make validate`, and related selectors.

## References

- `AGENTS.md` — canonical governance source

## Rules
- **Zero Tolerance for Hacks**: Prohibited use of `model_rebuild()`, `eval()`, `exec()`, `cast()`, and `inline imports`. Wait for definition time or use Protocol decoupling.
- **AXIOMATIC**: Every change MUST be INTEGRAL and pass ALL 4 linters (ruff, mypy, pyright, pyrefly) with ZERO errors, ZERO warnings. No partial fixes. ALL impacted references across the ENTIRE codeset MUST be immediately updated using ast-grep (`sg`) search-and-replace. After any type/model/signature change: (1) `sg` find-and-replace ALL references across all 33 projects, (2) `make check` on every affected project, (3) verify ZERO errors from all 4 linters. A change that breaks ANY linter in ANY project is REJECTED — the portfolio is ONE unit.
- **AXIOMATIC**: Linter suppression comments (`# type: ignore`, `# noqa`, `# pyright: ignore`, `# pyrefly: ignore`, `# mypy: ignore`, `typing.cast()`) are FORBIDDEN without ALL of: (1) well-founded technical explanation with REAL, verifiable internet citations (official docs, GitHub issues, PEPs), (2) explicit business necessity in the same comment, (3) per-line ONLY — never per-file, never per-module, never in config. Global suppression rules in `pyproject.toml`, `ruff.toml`, or any config are TOTALLY FORBIDDEN. Fix the code, never silence the linter.

## Instructions

- Select scope intentionally with `PROJECT=` or `PROJECTS=` before running gates.
- Apply fast gate first (`make check`), then deeper validation (`make test`, `make validate`).
- Keep verification evidence tied to actual executed commands.

## Workflow

1. Run `make check` for immediate lint/type/security feedback.
2. Run `make test` for behavior and coverage.
3. Run `make validate` for extended non-lint checks.
4. Re-run scoped gates for every touched project when shared contracts change.

## Examples

```bash
# Focus a single project
make PROJECT=flext-core check
make PROJECT=flext-core test

# Validate a multi-project slice
make PROJECTS="flext-core flext-api" validate
```

## Verification

- `make check`
- `make test`
- `make validate`
- `make PROJECT=<name> check`
- `make PROJECTS="proj-a proj-b" validate`

## Standardized Make Gate Surface

Project `base.mk` and workspace `Makefile` expose only these command verbs:

```bash
make setup
make check
make security
make format
make docs
make test
make validate
make clean
```

Execution semantics:

- `make check`: fast quality gate (ruff + format check + pyrefly + bandit).
- `make test`: pytest with coverage (threshold from `pyproject.toml` `[tool.coverage.report] fail_under`).
- `make validate`: non-lint extended gates (radon + interrogate), optional `FIX=1`.
- `make security`: explicit security scan gate.
- `make format`: canonical formatter gate.

---

## Workspace Automation Selectors

Use root `Makefile` selectors to avoid running full workspace loops when not needed:

```bash
# Single project
make PROJECT=flext-core check
make PROJECT=flext-core validate FIX=1

# Multi-project slice
make PROJECTS="flext-core flext-api" check

# Scoped test execution with pytest args
make PROJECT=flext-api test PYTEST_ARGS="-k unit"
```

Selector contract:

- `PROJECT=<name>` selects one project.
- `PROJECTS="a b c"` selects multiple projects.
- `PYTEST_ARGS="..."` is forwarded to project `make test`.

## Thresholds Summary

| Metric                    | Value                          | Source                                               |
| ------------------------- | ------------------------------ | ---------------------------------------------------- |
| Line length               | 88                             | `ruff-shared.toml` `line-length` setting             |
| Python target             | 3.13                           | `ruff-shared.toml` `target-version` setting          |
| Coverage min              | Per-project (see `fail_under`) | `pyproject.toml` `[tool.coverage.report] fail_under` |
| Docstring min             | 80%                            | `base.mk` variable `DOCSTRING_MIN`                   |
| Max cyclomatic complexity | 10                             | `base.mk` variable `COMPLEXITY_MAX`                  |
| Max cognitive complexity  | 15                             | `base.mk` complexipy gate parameters                 |
| Dead code confidence      | 80%                            | `base.mk` vulture gate parameters                    |

---

## When to Run Which Gate

| Change Type        | Required Gates                    |
| ------------------ | --------------------------------- |
| Any code change    | `make check`                      |
| Before PR/commit   | `make validate`                   |
| Type/model changes | `make check && make test`         |
| Security-sensitive | `make security` + `make validate` |
| New public API     | `make validate` + `make test`     |
| Docs only          | `make docs`                       |
