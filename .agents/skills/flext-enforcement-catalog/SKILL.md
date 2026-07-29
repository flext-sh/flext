---
name: flext-enforcement-catalog
description: 'Use when adding, changing, retiring, or auditing a cross-layer enforcement rule registered in the typed `c.ENFORCEMENT_CATALOG` and executed by the flext-tests dispatcher.'
license: MIT
metadata:
  version: 1.0.0
---
# FLEXT Enforcement Catalog

## Workflow

1. Locate the existing invariant, owner skill, rule identifier, and dispatcher route.
2. Change the typed catalog entry and implementation together.
3. Add a positive and negative real fixture for the dispatcher.
4. Run the focused enforcement test and the catalog consistency gate.

## Contracts

- Register each cross-layer rule once in `c.ENFORCEMENT_CATALOG`.
- Keep rule identifiers, severity, owner skill, scan scope, and remediation typed and synchronized.
- Add or retire the dispatcher integration and its real fixture in the same change.
