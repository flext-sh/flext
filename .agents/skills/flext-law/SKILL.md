---
name: flext-law
description:
  Apply the FLEXT-only architecture, workspace, generation, import, and fleet delta over
  canonical global execution governance.
---

# FLEXT law

## Authority and scope

This branch-matched repository owns FLEXT architecture. The selected governance
bundle owns universal execution; AI Hub selects and delivers instructions. Follow
[the session router](../../commands/flext-law.md), then the nearest member's
scope-only delta. Neither a same-named global skill nor another branch replaces
this file. Third-party forks retain upstream architecture and tooling.

The active operator request and selected tracker own current intent. Historical
issue identifiers, implementation censuses and private plans do not assign work.
A target contract is not an implementation receipt: unresolved producer or
consumer divergence remains implementation pending.

## Responsibility and reuse

Use the existing public c/t/p/m/u families and operational r/e/x/h/d/s surfaces.
Dependency direction is flext-core toward consumers; flext-infra owns tooling
and is not a product runtime dependency. Layer direction is c -> t -> p -> m -> u;
reverse dependencies are TYPE_CHECKING-only. A family must not import its own
public facade to implement that facade.

Constants belong to c, aliases to t, capability protocols to p, Pydantic models
to m and reusable behavior to u. Settings, validated configuration, service
foundations, use cases, API composition and transport retain their declared
owners. Centralize only behavior with the same domain responsibility; a shared
helper must not absorb another domain or become a second dispatcher.

Before adding a declaration or function, inspect that owner, its lower layers,
consumers and pinned libraries. Call the existing primitive directly when its
contract fits. Preserve models, Results and source identities across internal
calls; parse once at ingress and serialize at transport egress. Do not add a
getter, adapter, wrapper, conversion or intermediate copy without a required
contract difference. Retain immutability and ownership where mutation is not
permitted. MRO composes declared family behavior; DI supplies collaborators
explicitly at the API root.

Annotations use the canonical t/p contracts, with no Any, object, unparameterized
collections or concrete models substituted for structural request protocols.
Declaration layers contain declarations and their supported validation metadata;
behavior stays at its behavior owner. Runtime annotations resolve at the
original declaring owner. Eager facade rewrites, model_rebuild and compatibility
aliases do not repair cycles. The current toolchain owner declares the Python
floor; use that floor rather than a compatibility implementation.

## Detailed contract owners

Read the relevant decision instead of maintaining another copy here:

| Subject | Single detailed owner |
| --- | --- |
| Settings, config, constants and schemas | [ADR-005](../../../docs/architecture/adr/005-config-settings-constants-templates-schemas-ssot.md) |
| Family parts, MRO and semantic rewiring | [ADR-014](../../../docs/architecture/adr/014-family-part-shape-rope-codemod-rules.md) |
| Public consumption and facade imports | [Consumption law](../../../docs/standards/consumption-law.md), ratified by ADR-015 |
| Settings singleton | [ADR-016](../../../docs/architecture/adr/016-settings-config-singleton-contract.md) |
| Generator declarations and derived exports | [ADR-018](../../../docs/architecture/adr/018-generator-declarations.md), superseding older alias tables |
| Ports, operation metadata, service MRO and API/CLI composition | [ADR-019](../../../docs/architecture/adr/019-service-contract-ports-operations.md), including the structural request amendment |
| Project-only deltas and configuration injection | [ADR-024](../../../docs/architecture/adr/024-di-config-contract-derived-defaults-minimal-overrides.md) |

## Generation, validation and delivery

Change generator declarations, templates or explicit project deltas at their
owners; generated imports, facets, Makefiles, CI and managed configuration are
published through the native root verbs. Structural rewires reuse the existing
Rope/ast-grep/candidate-publication pipeline through make mod. Do not introduce
another refactoring engine, symbol mapping table or manual projection writer.

Root AGENTS.md owns workspace/member command routing and connectivity-test
applicability. Universal command deadlines, profiling, environment ownership,
selected-tracker handling and Git closure remain with their global owners.
flext-tests supplies shared fixtures and behavior assertions; public runtime
acceptance and every required analyzer retain their declared policy.

FLEXT owns local Git automation through flext-infra. AI Hub's GitHub, CRG and
host integrations are consumed only through their public protocols when selected;
FLEXT imports neither AI Hub nor CRG libraries. Missing optional enrichment is
not a missing required gate.

Integrate validated member commits on their declared remote integration branches
before updating superproject gitlinks. Source, integrated revision and installed
runtime are separate proofs. The [stabilization procedure](../../../docs/ways-of-working/stabilization-checkpoint-0.12.md)
selects current execution evidence without redefining these owners.
