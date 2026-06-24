---
name: flext-quality-gates
description: 'Use this skill to use when running or interpreting quality gates (lint,
  typecheck, test, val) in the FLEXT monorepo. Covers mandatory gate definitions,
  exact tool commands (ruff, pyrefly, pyright, mypy, pytest), pass thresholds, and
  configuration sources from base.mk and pyproject.toml. DO NOT USE FOR: questions
  unrelated to flext-quality-gates creating projects or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---
# FLEXT Quality Gates

**UTILITY SKILL**

## USE FOR

- Requests about flext quality gates.
- Workflows described in this skill.
- Operator tasks within this scope.

## DO NOT USE FOR

- questions unrelated to flext-quality-gates.
- creating projects or architecture from scratch.

## Workflow

1. First edit -> `ruff check <file>`.
2. Same slice -> `pyrefly check <file>`.
3. Same slice -> narrow behavior gate (`pytest` or `make check PROJECT=<affected>`).

## Critical rules

- Prefer canonical sources.
- Require evidence.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
