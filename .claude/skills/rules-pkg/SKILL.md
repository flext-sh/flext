---
name: rules-pkg
description: Rules for package metadata and package-layer structure under `pkg/`. Use when editing package descriptors, plugin manifests, or packaging utilities.
---

# Rules Pkg

## Scope

- `pkg/controlpanel/`
- `pkg/domain/`
- `pkg/flextservice/`
- `pkg/infrastructure/`
- `pkg/plugins/`

## References

- `pyproject.toml`
- `pkg/`
- `Makefile`

## Rules

- Keep package metadata consistent with workspace naming/version patterns.
- Keep package boundaries clear (domain vs infrastructure vs plugin layers).
- Avoid leaking internal-only code via package exports.
- Update consuming docs/scripts when package paths change.

## Instructions

- Verify package path exists and matches intended layer.
- Keep naming stable and deterministic across related files.
- Validate packaging-related references in build/test scripts.

```bash
ls -la pkg
```

## Workflow

1. Identify package area being modified.
2. Apply minimal metadata/structure change.
3. Confirm references in build scripts/docs still resolve.
4. Verify no accidental layer boundary drift.

## Examples

Good:

```text
pkg/domain/ contains domain-focused package artifacts only.
```

Why good: preserves package-layer responsibility.

Bad:

```text
Place infrastructure bootstrap files inside pkg/domain/ for convenience.
```

Why bad: layer mixing increases maintenance and dependency confusion.

## Verification

- `ls -la pkg`
- `rg -n "pkg/" Makefile scripts/*.sh docs || true`
- `rg -n "TODO|FIXME" pkg || true`
