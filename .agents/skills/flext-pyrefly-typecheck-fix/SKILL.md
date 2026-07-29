---
name: flext-pyrefly-typecheck-fix
description: 'Guidance for diagnosing or fixing pyrefly type-check errors across the FLEXT monorepo. Covers recurring error patterns with safe auto-fix rules, suppression guidance, and cross-project consistency strategies for zero-error type-checking.'
license: MIT
metadata:
  version: 1.0.0
---
# Pyrefly Type-Check Fix Rules

## Workflow

1. Detect failing cluster type from gate output.
2. Apply mechanical rewrite when safe.
3. Apply manual semantic fix when required.

## Enforced contracts

- r.ok(None) is a runtime bug — ok() rejects None values.
- r[t.JsonValue] uses type erasure — prefer r[t.JsonValue].
- Legacy t.JsonMapping annotation — normalize to t.JsonValue alias.
- BindableLogger annotation lacks logging method signatures — use p.Logger.
- dict(rootmodel_instance) causes no-matching-overload — use .root instead.
- Mapping type used at mutation site — contract must be MutableMapping or local dict materialization.
