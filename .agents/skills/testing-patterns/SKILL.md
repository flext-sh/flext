---
name: testing-patterns
description: 'Testing discipline for Python/pytest in FLEXT — public-API-only assertions, real-flow-over-mocks, enforcement warnings as failures, golden-file examples, AAA structure, r[T] result assertions, facade-only imports. Use when writing or reviewing any test, fixture, or example.'
license: MIT
metadata:
  version: 1.0.0
---
# Testing Patterns

## Workflow

1. Write a failing test for the desired PUBLIC behavior (Red).
2. Write minimal code to make the test pass (Green).
3. Refactor while keeping tests green (Refactor).

## Enforced contracts

- assert True is a no-op — tests must verify actual behavior.
- Bare assert False without message should be pytest.fail() with a reason.
- time.sleep() in tests makes them flaky and slow.
- Bare assert on variable (truthy-only) — use specific assertions.
