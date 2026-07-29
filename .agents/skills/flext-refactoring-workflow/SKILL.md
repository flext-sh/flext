---
name: flext-refactoring-workflow
description: 'Use when planning or executing a multi-file FLEXT refactor that changes ownership, public symbols, MRO namespaces, runtime responsibilities, or cross-package consumers and can be split into coordinated lanes.'
license: MIT
metadata:
  version: 2.0.0
---
# FLEXT Refactoring Workflow

## Orchestration model

The coordinator owns intent, architecture decisions, the symbol/consumer ledger,
integration order, final gates, and landing. Parallel workers own bounded discovery or
disjoint implementation lanes; they do not independently redefine the target contract.

| Lane | Typical scope | Deliverable |
| --- | --- | --- |
| Authority audit | ADRs, standards, live definitions | target/live delta with evidence |
| Symbol census | definitions, exports, callers, strings | complete migration ledger |
| Owner implementation | canonical source modules | final contract without compatibility path |
| Consumer cutovers | disjoint packages/tests/docs | updated callers against the frozen contract |
| Enforcement | rules, fixtures, validators | failing legacy fixture and passing target fixture |
| Documentation | canonical docs/examples | target behavior and migration evidence |

## Workflow

1. **Frame:** record target, exclusions, accepted authority, live owner, target owner,
   deletion budget, required gates, and stop condition.
2. **Audit in parallel:** delegate architecture, consumer, enforcement, and test audits
   as read-only lanes. Require exact paths/lines and prohibit speculative edits.
3. **Freeze the contract:** reconcile findings into one public target and resolve any
   destructive or competing outcome before implementation.
4. **Partition writes:** assign disjoint path sets. The owner lane changes definitions;
   consumer lanes update complete package groups; one lane owns exports/generated files.
5. **Cut over:** use structural refactoring, update required imports/exports/callers in
   an importable batch, and remove the obsolete route. Never leave old-plus-new APIs.
6. **Integrate continuously:** re-read shared files, review each lane's diff/evidence,
   run owner and direct-consumer gates, then release the next dependency-ready lane.
7. **Prove deletion:** search definitions, imports, strings, docs, and generated maps for
   the legacy symbol. Classify every remaining hit as live, historical, or fixture.
8. **Land:** run narrow-to-workspace gates, record evidence, commit explicit paths, and
   update the execution ledger.

## Delegation contract

Every lane receives the objective, authority links, frozen contract, writable paths,
read-only context, exclusions, expected deliverable, exact validation commands, and
stop condition. Findings must distinguish accepted target architecture from observed
runtime behavior. A worker reports conflicts immediately and never expands scope to
resolve them silently.

## Integration rules

- Parallelize independent discovery and disjoint consumers; serialize edits to the
  canonical owner, shared exports, generated projections, and migration ledger.
- A public cutover is not complete until owner, exports, all live consumers, tests,
  examples, docs, and enforcement agree.
- Keep each implementation slice independently importable and preferably net-negative.
- Regenerate managed projections from their owner and require an empty second run.
- The coordinator validates combined state; isolated worker success is insufficient.

## Evidence

Record the definition/caller census, lane ownership matrix, per-lane command results,
combined diff review, zero-live-reference search, generated idempotence, and final
owner/direct-consumer/workspace gates.
