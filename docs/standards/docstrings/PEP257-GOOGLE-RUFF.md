# PEP 257, Google Style, and Ruff

FLEXT public docstrings follow PEP 257 structure and Google-style sections. The
typed Ruff configuration is the executable authority for the precise rule set;
this page owns authoring guidance, not a copied lint registry.

## Purpose

A useful docstring explains why a symbol exists, what public contract it owns,
and which non-obvious boundary or failure matters to a caller. It does not
translate code into prose.

Document public modules, classes, protocols, methods, functions, properties,
and exported facade members. Private implementation earns a docstring only when
its invariant is not evident from its name, annotation, and local context.

## General form

- Start with a concise imperative summary.
- Put a blank line between the summary and extended explanation.
- Use complete sentences and stable domain vocabulary.
- Describe observable behavior, not call order or internal construction.
- Keep annotations as the sole owner of type information.
- Name exceptions only when they escape through the public contract.

```python
def normalize_name(value: str) -> str:
    """Normalize a public name for canonical comparison.

    Args:
        value: Name supplied at the public boundary.

    Returns:
        Canonical name used by downstream comparisons.

    Raises:
        ValueError: The supplied name is empty.
    """
    ...
```

## Modules

State the module's responsibility and ownership. Keep copyright and SPDX text
inside the module docstring.

```python
"""Resolve canonical public names for package consumers.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""
```

Do not place a copyright comment before the module docstring.

## Classes and protocols

Describe the responsibility and boundary, not the class name. Protocol
docstrings explain what consumers may rely on without naming an adapter.
Constructor parameter documentation belongs with the public construction
surface and is not repeated across class and initializer docstrings.

## Functions and methods

Use sections only when they add information:

- `Args:` explains semantic constraints not evident from annotations.
- `Returns:` describes meaning, ownership, and important invariants.
- `Yields:` replaces `Returns:` for generators.
- `Raises:` lists exceptions that intentionally escape the public boundary.
- `Example:` is reserved for a short, public-facade behavior example.

Never document swallowed, normalized, retried, or fallback errors. Such behavior
is itself prohibited; the first causal exception must escape.

## Properties

Describe the value's meaning and invariant. Do not repeat “Get” or “Set” when
the property name and annotation already express that fact.

## Public examples

Examples import public package facades and read project-controlled values from
typed config or settings. They never import private modules, build internal
classes, or freeze current configuration literals.

Test examples use `tm`, the unified `conftest.py`, and typed shared fixtures.
Mocks, fakes, stubs, patching, monkeypatch mutation, and copied setup are
prohibited.

## Avoid

- summaries that merely repeat the symbol name;
- prose that restates annotations;
- promises about implementation order;
- copied configuration values, counts, paths, versions, or thresholds;
- compatibility, fallback, retry, suppression, or partial-success language;
- stale `TODO`, `FIXME`, or generated prose;
- raw tool commands or per-file validation recipes.

## Review checklist

- The symbol is public or the private invariant genuinely needs explanation.
- The summary is imperative and caller-focused.
- Sections match the actual public signature and runtime behavior.
- Every project-owned fact comes from its typed owner.
- Links and examples use public, current surfaces.
- Changed behavior and changed documentation land together.

## Canonical validation

Run validation from the workspace root:

```bash
make fix APPLY=Y
make fmt APPLY=Y
make check APPLY=Y
make test APPLY=Y
make conform APPLY=Y
```

The test verb retains Testmon. Never invoke Ruff, a test runner, or an ad-hoc
script directly, and never add project, file, pattern, action, phase, fix, or
changed-only selectors. If the declared Make surface cannot express a required
check, repair its owner before continuing.
