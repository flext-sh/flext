# FLEXT Python Docstring Standards

This directory defines the public Python docstring contract for the FLEXT
workspace.

## Canonical reference

[PEP 257, Google style, and Ruff](PEP257-GOOGLE-RUFF.md) is the single detailed
reference. The typed Ruff configuration owns the exact enabled and ignored
rules; this documentation never duplicates that registry.

## Principles

- Explain why a public symbol exists, its boundary, and meaningful failure
  conditions.
- Do not repeat the symbol name, signature, annotations, or implementation.
- Keep summaries imperative, concise, and specific.
- Document public parameters, returns, yields, and raised exceptions when they
  add information beyond the type contract.
- Keep module copyright and SPDX text inside the module docstring.
- Remove stale prose when behavior or ownership changes.

## Canonical validation

Run documentation and code validation only from the workspace root:

```bash
make fix APPLY=Y
make fmt APPLY=Y
make check APPLY=Y
make test APPLY=Y
make conform APPLY=Y
```

Do not invoke Ruff or another underlying tool directly. Do not add project,
file, pattern, action, phase, fix, or changed-only selectors. Test execution
retains the canonical Testmon cache.
