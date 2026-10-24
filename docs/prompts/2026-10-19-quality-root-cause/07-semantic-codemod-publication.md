# Repair semantic codemod publication and typed fixtures

## Authority

Read [the current FLEXT session router](../../../.agents/commands/flext-law.md)
and [this task collection](README.md) before execution. This file supplies only
the task-specific owner, diagnosis and acceptance delta.

## Exclusive ownership

Own the semantic publication owner and its consumer tests, with exclusive ownership agreed before edits.

## Sources to inspect

flext-infra/tests/unit/codemod/test_semantic_publication.py; current semantic-publication implementation discovered through source references; codegen conform rules and typed request models.

## Required correction

Inspect the selected (consumer_root,) argument against the latest source signature. Migrate tests to canonical request/state models and sealed candidate inventories, including current GateContext.candidate_files semantics. Do not change a correct production signature to accept old positional containers. Preserve atomic publication, causal errors and all concurrent changes. Structural migration must be implemented in the canonical codemod, not repetitive manual consumer sweeps.

## Acceptance evidence

Use runtime publication behavior as acceptance: correct consumers rewritten atomically, rejected candidates unmodified, first error preserved. Run native codemod/generation validation separately from pytest; pytest must not generate workspace production artifacts. Prove fixed-point/idempotence and no new lint violations.
