# FLEXT ast-grep provider reference

This is a compact ownership map, not a second rule catalog.

## Source-of-truth map

| Concern | Canonical owner |
|---|---|
| Intended behavior | owning FLEXT domain declaration, validated config, or fundamental rule |
| Provider identity and exported IDs | provider.toml |
| ast-grep loading paths | sgconfig.yml |
| Detection and rewrite behavior | rules/*.yml |
| Safe execution procedure | SKILL.md |
| Validation samples | tests/*-test.yml |
| Reviewed validation output | tests/__snapshots__/*-snapshot.yml |
| Execution evidence | active workspace-root Bead |

Tests and snapshots never define behavior. They are replaced when they disagree
with the domain owner, provider declaration, configuration, or rule.

## Provider boundary

FLEXT owns this provider directory. ai-hub owns the generic managed engine and
projects it only into workspaces whose canonical pyproject metadata declares
flext-core usage. There is no global FLEXT rule copy in ai-hub and no local
engine fork in this repository.

The exact ID inventory is the sorted rule_ids array in provider.toml. Its count,
uniqueness, and bijection with rule, validator, and snapshot IDs are computed
during validation; they are intentionally not reproduced here.

Rules cover these domains without creating additional catalogs:

- Result propagation and typed exception preservation;
- public CLI finalization and handler boundaries;
- runtime typing and MRO diagnostics;
- narrowly proven active FLEXT-test migrations;
- settings API drift.

The presence of fix in a rule declaration is the only mode authority. A prose
label cannot promote a detection-only rule into a rewrite.

## Invariants

- Each ID has one rule owner, one validator, and one reviewed snapshot.
- Each rule explicitly excludes `**/legado/**`.
- A fix introduces no name or semantic choice not proven by its syntax.
- Application selects one ID and exact preview cardinality, files, and manifest
  hash.
- The post-apply rescan is empty before native repository gates run.
- Failure is repaired forward; no rollback, bypass, suppression, or old/new
  coexistence is part of the engine contract.

## Updating the provider

Change the domain owner first when reality changes. Then update the canonical
rule and provider ID declaration. Only afterward update the validator and
reviewed snapshot to prove the new declaration. Finally run the no-mutation
test, bijection audit, targeted preview, idempotence check, and native gates,
recording exact evidence in the root workspace bead.

Never preserve a stale rule because a fixture is green, regenerate snapshots
before reviewing a changed declaration, or paste a hand-maintained ID table
into another document, skill, agent, or repository.
