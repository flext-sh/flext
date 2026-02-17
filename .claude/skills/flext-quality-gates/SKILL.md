---
name: flext-quality-gates
description: Mandatory verification gates with exact tool commands, thresholds, and configuration sources from base.mk
---

# FLEXT Quality Gates

> **Source of truth**: Verified from `base.mk` lines 114-202, `ruff-shared.toml`,
> and individual `pyproject.toml` files on 2026-02-17.

## Gate 1: Lint (Ruff) - ZERO TOLERANCE

```bash
make lint    # or: make l
# Runs: ruff check . --quiet
# Config: ruff-shared.toml (workspace) + pyproject.toml (project extensions)
```

- **ANY lint error = build failure**
- Auto-fix available: `make fix` (runs `ruff check --fix . --quiet`)
- Format check: `make format-check` (runs `ruff format --check . --quiet`)

## Gate 2: Type Check (Pyrefly) - ZERO TOLERANCE

```bash
make type-check    # or: make tc
# Runs: pyrefly check src/ --config pyproject.toml
```

- **ANY type error = build failure**
- Pyrefly is the ONLY type checker used (`base.mk` line 128-129)
- mypy/pyright are NOT used in the make targets

## Gate 3: Tests (Pytest) - MIN 80% COVERAGE

```bash
make test    # or: make t
# Runs: pytest tests/ --cov=COV_DIR --cov-report=term-missing:skip-covered --cov-fail-under=80
```

- Coverage minimum: 80% (configurable per project via `MIN_COVERAGE`)
- Fast mode (no coverage): `make test-fast`

## Gate 4: Complexity (Radon) - MAX CC 10

```bash
make complexity    # or: make cx
# Runs: radon cc src/ -a -nb --total-average
# Also: radon mi src/ -nb (Maintainability Index)
```

## Gate 5: Cognitive Complexity (Complexipy) - MAX 15

```bash
make cognitive-complexity    # or: make cc
# Runs: complexipy src/ --max-complexity-allowed 15
```

## Gate 6: Docstring Coverage (Interrogate) - MIN 80%

```bash
make docstring-check    # or: make dc
# Runs: interrogate src/ --fail-under=80 --ignore-init-method --ignore-magic -q
```

## Gate 7: Dead Code Detection (Vulture) - MIN CONFIDENCE 80%

```bash
make dead-code    # or: make dd
# Runs: vulture src/ --min-confidence 80 --exclude "tests,examples"
# Note: Runs from WORKSPACE_ROOT where vulture is installed
```

## Gate 8: Spell Check (Codespell)

```bash
make spell-check    # or: make sp
# Runs: codespell src/ --toml pyproject.toml --quiet-level 3
```

## Gate 9: Security (Bandit)

```bash
make security
# Runs: bandit -r src/ -q -ll
```

## Gate 10: Dependency Analysis (deptry)

```bash
make deps    # or: make dp
# Runs: uvx deptry . --no-ansi
```

---

## Composite Gates

| Target | What It Runs |
| --- | --- |
| `make check` | lint + type-check (quick daily gate) |
| `make validate` | lint + format-check + type-check + complexity + docstring-check + security + test |
| `make validate-full` | validate + dead-code + cognitive-complexity + spell-check |

---

## Thresholds Summary

| Metric | Value | Source |
| --- | --- | --- |
| Line length | 88 | `ruff-shared.toml` line 19 |
| Python target | 3.13 | `ruff-shared.toml` line 24 |
| Coverage min | 80% | `base.mk` line 14 (`MIN_COVERAGE`) |
| Docstring min | 80% | `base.mk` line 15 (`DOCSTRING_MIN`) |
| Max cyclomatic complexity | 10 | `base.mk` line 16 (`COMPLEXITY_MAX`) |
| Max cognitive complexity | 15 | `base.mk` line 182 |
| Dead code confidence | 80% | `base.mk` line 174 |

---

## When to Run Which Gate

| Change Type | Required Gates |
| --- | --- |
| Any code change | `make check` (lint + type-check) |
| Before PR/commit | `make validate` |
| Release prep | `make validate-full` |
| Type/model changes | `make check && make test` |
| Security-sensitive | `make security` + `make validate` |
| New public API | `make validate` + verify docstring coverage |
| Docs only | `make lint` (catches doc formatting issues) |
