---
name: coding-standards
description: 'Use when writing or reviewing FLEXT Python code and a compact cross-cutting checklist is needed for imports, facades, typing, results, models, logging, tests, and validation.'
license: MIT
metadata:
  version: 2.0.0
---
# FLEXT Coding Standards

This is a routing checklist. Detailed mechanics belong to the linked focused skills.

## Before editing

1. Identify the package, architectural layer, public surface, and existing owner.
2. Search definitions and callers structurally; inspect configuration and generators.
3. Select the path skill and only the technology skills that match the change.
4. Establish a narrow green baseline and record any pre-existing failure separately.

## Python contract

- Target Python 3.13 and start modules with `from __future__ import annotations`.
- Use `c`, `t`, `p`, `m`, and `u` as the structural facade aliases.
- Use `r[T]` as the result contract. Runtime classes and narrow operational surfaces
  are not structural facade namespaces and must not accumulate unrelated behavior.
- Keep import order: future, standard library, third party, FLEXT packages, local.
- Import abstracted frameworks through FLEXT owners; never bypass `flext-core` or
  `flext-cli` from consumers.
- Do not introduce `Any`, bare `object`, legacy `typing.Dict`, wildcard imports,
  blanket ignores, or runtime imports hidden under `TYPE_CHECKING`.
- Narrow unions with `isinstance` or a reusable `TypeGuard`.

## Ownership and composition

- `c`: immutable constants and enums.
- `m`: Pydantic v2 data, command, event, query, and settings models.
- `p`: runtime-checkable behavioral contracts.
- `t`: type aliases and generic type relationships.
- `u`: stateless utilities and framework adapters.
- `r[T]`: success/failure contract for every fallible application boundary.

Facades remain thin. Put behavior in the owning service or mixin, compose namespaces
through the established MRO, and keep `__init__.py` export-only. A concept has one
owner and one public access path.

## Models, settings, and results

- Parse untrusted or dynamic input once with `model_validate`, `TypeAdapter`, or the
  owning settings model.
- Use Pydantic v2 `ConfigDict`, validators, serializers, and `model_dump*` APIs.
- Keep configurable values in typed settings or configuration, not module literals.
- Return `r.ok(value)` or `r.fail(error)` from fallible services and preserve failure
  context through composition. Do not unwrap results in production flow.
- Do not return `T | None` from a fallible application operation. Translate expected
  external exceptions once at the adapter boundary and return a typed failure.

## Logging and side effects

Use the FLEXT logger, bind structured context, and log once at the boundary that can
act on the failure. Do not use `print` in production source, leak credentials, or
perform network/filesystem work at import time.

## Tests

- Exercise public APIs and real result flows.
- Derive expected configurable values from the same typed source as production.
- Prefer deterministic fixtures and temporary paths over sleeps or global state.
- Assert value and failure semantics precisely; avoid truthiness-only assertions.
- Update examples, docstrings, exports, and caller tests with public changes.

## Validation sequence

1. Fresh import or collection smoke for the touched package.
2. Ruff without auto-fix, then Pyrefly, Pyright, and Mypy as applicable.
3. The narrowest relevant Pytest selection.
4. Direct-consumer checks for public changes.
5. `make check CHANGED_ONLY=1` and broader validation when scope crosses packages.

Never weaken configuration to obtain a green result. Fix the canonical source or
report the exact environmental blocker.

## Focused skills

- [`flext-ecosystem-patterns`](../flext-ecosystem-patterns/SKILL.md): ownership and dependency direction.
- [`flext-import-rules`](../flext-import-rules/SKILL.md): import ordering and boundaries.
- [`flext-strict-typing`](../flext-strict-typing/SKILL.md): aliases, narrowing, and no-`Any` policy.
- [`lib-pydantic-v2`](../lib-pydantic-v2/SKILL.md): model and validation APIs.
- [`lib-returns`](../lib-returns/SKILL.md): railway result composition.
- [`lib-structlog`](../lib-structlog/SKILL.md): structured logging.
- [`testing-patterns`](../testing-patterns/SKILL.md): test design and assertions.
- [`flext-quality-gates`](../flext-quality-gates/SKILL.md): canonical validation selection.
