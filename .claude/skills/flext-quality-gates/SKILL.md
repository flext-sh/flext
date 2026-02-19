---
name: flext-quality-gates
description: Mandatory verification gates with exact tool commands, thresholds, and configuration sources from base.mk and pyproject.toml
---

# FLEXT Quality Gates

**Reviewed**: 2026-02-19 | **Scope**: Coverage source-of-truth migration to pyproject.toml


> **Source of truth**: Verified from `base.mk` (`check`, `test`, and `validate` targets), `ruff-shared.toml`,
> and individual `pyproject.toml` files on 2026-02-19.

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

| Metric | Value | Source |
| --- | --- | --- |
| Line length | 88 | `ruff-shared.toml` `line-length` setting |
| Python target | 3.13 | `ruff-shared.toml` `target-version` setting |
| Coverage min | Per-project (see `fail_under`) | `pyproject.toml` `[tool.coverage.report] fail_under` |
| Docstring min | 80% | `base.mk` variable `DOCSTRING_MIN` |
| Max cyclomatic complexity | 10 | `base.mk` variable `COMPLEXITY_MAX` |
| Max cognitive complexity | 15 | `base.mk` complexipy gate parameters |
| Dead code confidence | 80% | `base.mk` vulture gate parameters |

---

## When to Run Which Gate

| Change Type | Required Gates |
| --- | --- |
| Any code change | `make check` |
| Before PR/commit | `make validate` |
| Type/model changes | `make check && make test` |
| Security-sensitive | `make security` + `make validate` |
| New public API | `make validate` + `make test` |
| Docs only | `make docs` |
