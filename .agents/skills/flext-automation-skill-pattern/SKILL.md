---
name: flext-automation-skill-pattern
description: 'Use when creating a reusable FLEXT automation or enforcement skill with a typed owner, deterministic script, rules manifest, fixtures, dry-run behavior, and canonical Make integration.'
license: MIT
metadata:
  version: 1.0.0
---
# Flext Automation Skill Pattern

## Workflow

1. Define one observable invariant, its owner, scan scope, severity, and remediation.
2. Prefer declarative `rules.yml` plus ast-grep rules; use a custom script only when
   structured or cross-file evaluation is required.
3. Add positive, negative, and idempotence fixtures before enabling the rule broadly.
4. Expose the automation through the existing dispatcher and canonical Make verb.
5. Run read-only baseline mode, inspect findings, then run strict mode in isolation.

## Automation contract

- Detection and remediation are separate; default execution never mutates the tree.
- Apply mode is explicit, deterministic, bounded to declared paths, and safe to repeat.
- Rules declare stable identifiers, severity, owner skill, include/exclude scope, and
  actionable failure text.
- Scripts follow [`rules-scripts`](../rules-scripts/SKILL.md), use stable exit codes,
  and emit machine-readable summaries when consumed by another gate.
- A new enforcement route updates its catalog entry, dispatcher, documentation, and
  real fixtures in the same change.

## Validation

Prove one compliant fixture passes, each violation fixture fails for the intended
reason, apply mode produces the expected diff, a second apply is empty, and the
canonical Make gate propagates the exit status.
