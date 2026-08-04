# ADR-010 — Unified project standardization via flext-infra codegen and flext-tests

- **Status:** Accepted — split delivery across `0.12.0-dev` and `0.20.0-dev`
- **Date:** 2026-07-18
- **Amended:** 2026-07-28
- **Target lines:** `0.12.0-dev` receives the release-blocking generic
  manifest, capability, Make, codegen, and external-compatibility contract.
  Facade, naming, runtime-directory, layout, and structural-enforcement
  refactors remain forward-only on `0.20.0-dev`.
- **Tracking:** `mro-p68a`, external-compatibility gate `mro-p68a.12`, and the
  forward ecosystem-standardization epic.
- **Complements:** ADR-003 (topology/profiles), ADR-004 (Make/codegen SSOT
  ownership), ADR-005 (config/settings/constants/templates/schemas SSOT and
  facade layering), ADR-007 (operational kernel/CLI/transactional conform),
  ADR-008 (neutral consumer boundaries), ADR-009 (ecosystem coordination).

This ADR does not create a new owner. It separates the compatibility contract
needed to stabilize `flext-infra 0.12.0` from unrelated forward architecture.

## Context

The workspace already has the right generic owners:

- `flext-infra codegen conform` is the sole conformance/generation interface
  (ADR-004), rendering managed files from `codegen.yaml`/`tooling.yaml` and the
  templates under `flext_infra/templates/` (`base_verbs.mk.j2`, `base_venv.mk.j2`,
  `project/base/{Makefile,pyproject.toml,.mise.toml,python-version,custom.mk}.j2`,
  `module_skeleton.py.j2`, `static_package_init.py.j2`, `lazy_init_root.py.j2`).
- `flext-tests` owns the shared test base and generic Make test behavior.
- each consumer owns its topology and capabilities in its local
  `config/workspace.yaml`;
- `flext-tests` owns shared Python test behavior, but it does not own Make
  routing.

The former text treated all standardization as `0.20.0-dev` work and presented
`boot`, `fmt`, and `val` beside the ADR-004 grammar. That contradicted the
release requirement: an isolated `flext-infra` artifact must provide one real,
generic Make/codegen surface to all release consumers before `0.12.0` can ship.

## Decision

Adopt one generated base with two explicitly separated delivery scopes.

### 1. The `0.12.0-dev` stabilization subset is release-blocking

`0.12.0-dev` receives all of the following before release:

- a consumer-owned, typed `config/workspace.yaml`;
- separate topology (`workspace-root`, `workspace-member`, or `standalone`) and
  declared capabilities (Python, Go, Node/frontend, Helm/GitOps, Docker,
  documents/content, and scripts);
- declared command-discovery roots and validated discovery from
  `scripts/<verb>/<what>.*` metadata;
- one generated Make surface and one deterministic codegen transaction;
- proof from an isolated candidate wheel across all 51 executable consumer
  surfaces.

The consumer manifest is the sole topology authority. `flext-infra`
`codegen.yaml` and schemas contain only generic profiles, capability contracts,
defaults, policies, and templates. They must not contain AI Hub, Cosmos, or
other consumer identities, branches, members, or exclusions, and conformance
must not compare a local manifest with a duplicated product catalog.

### 2. The public Make grammar is singular

Every surface exposes `help` plus exactly the twelve ADR-004 verbs:

```text
setup deps build check test format run status docs clean release codegen
```

`make help` lists the choices actually discovered for that
consumer. `PROJECT`, `CHECK_GATES`, `FILE`, `MATCH`, `FAIL_FAST`, and `ARGS`
have uniform meanings. `APPLY=Y` is the only authorization for mutation.
Unknown verbs, selectors, projects, and capabilities fail precisely. A declared
but non-applicable operation reports typed non-applicability; it never becomes
empty success or an implicit fallback.

Capabilities provide concrete handlers only for applicable operations.
`custom.mk` is limited to private `_custom_<verb>_<what>` and `pre/post-*`
hooks. It cannot define public targets, replace environment ownership, or patch
the generator. Legacy `boot`, `fmt`, and `val` aliases and competing Taskfile or
handwritten dispatchers are removed after each consumer completes its cutover.

### 3. Conformance is artifact-isolated and reaches a fixed point

The release candidate is built with `uv build --no-sources`, installed into an
empty environment, and executed without a source checkout, `PYTHONPATH`,
editable link, or workspace cache. It must support ordinary clones, worktrees,
workspace roots, attached members, and standalone repositories.

For every selected surface:

- check mode performs no writes;
- apply requires `APPLY=Y` and writes the complete validated selection;
- `check -> apply -> check` converges, and the second check has no diff;
- staged output is validated by its real Make consumer before any live
  activation, upload, service restart, or cluster rollout.

### 4. The external compatibility matrix is a predecessor gate

The 51 executable surfaces are:

- FLEXT root plus 31 projects;
- `.ai-hub`;
- `cosmos-main` root plus 12 independent subprojects;
- `cosmos-docgen` root plus four document subprojects.

Every surface passes `make help`, `make status`, applicable
`make help`, and `make gen WHAT=check`. Capability-specific
gates then exercise Python, Go, Node/frontend, serialized Helm/GitOps,
Docker/config/scripts, or document build/stage behavior. Upload and deployment
paths remain dry-run unless separately authorized with `APPLY=Y`; the release
gate never activates AI Hub services, uploads to Google Drive, or rolls out a
cluster.

`flext-infra 0.12.0` release preparation and publication remain blocked until
this matrix is green against the exact candidate artifact SHA. Representative
profiles also run on Ubuntu, macOS, and Windows. Helm is always serialized.

### 5. Forward-only `0.20.0-dev` architecture

The historical broader standardization decision remains accepted for
`0.20.0-dev`. It covers:

- canonical package facades, MRO composition, and generated `__init__.py`;
- module, class, and namespace naming;
- canonical `src`, `tests`, `examples`, and `scripts` layout;
- application-namespaced runtime directories and `FlextSettings` root-singleton
  resolution;
- declarative structural and naming enforcement.

None of these forward refactors is a prerequisite for `0.12.0`. Their existing
planning and drift reports remain historical evidence for the `0.20.0-dev`
lanes and must not be used to expand the stabilization release.

## Consequences

- The 0.12 release proves generic generation against real consumers instead of
  a `flext-infra` product catalog.
- Topology and technological capability are independent typed dimensions.
- Every consumer has the same public grammar without pretending every operation
  applies to every stack.
- Forward architecture remains sequenced on `0.20.0-dev`, without being pulled
  into release stabilization.

## Verification contract

1. Valid, invalid, incomplete, and unknown-capability manifests fail or pass
   through the typed local-manifest contract as specified.
2. Command discovery has no duplicated `WHAT` catalog, and every public help or
   invalid-selection path reports the real discovered surface.
3. An isolated wheel proves no source-checkout dependency and reaches the
   codegen fixed point.
4. All 51 Linux surfaces and representative cross-platform profiles pass their
   applicable public Make gates with no introduced warning, skip, suppression,
   fallback, or stale generated output.
5. Exact artifact SHA, consumer SHA, command, working directory, exit code,
   decisive output, and public QA evidence are recorded in `mro-p68a.12`.
6. Forward-only structural gates remain tracked on `0.20.0-dev`.

## References

- [ADR-003 — Manifest-owned topology, profiles](003-workspace-tooling-hub-distribution.md)
- [ADR-004 — Generated Make and codegen SSOT](004-generic-make-framework-in-flext-tests.md)
- [ADR-005 — Config/settings/constants/templates/schemas SSOT](005-config-settings-constants-templates-schemas-ssot.md)
- [ADR-007 — Performance optimization of worktree transactions and mutating CLI
  commands](007-worktree-transaction-performance.md)
- [ADR-008 — Neutral consumer boundaries](008-neutral-consumer-boundaries.md)
- [ADR-009 — Ecosystem coordination](009-ecosystem-coordination-and-library-evaluation.md)
- [Ecosystem coordination](../ecosystem-coordination.md)
- SSOT: `flext-infra/config/codegen.yaml`, `tooling.yaml`;
  templates under `flext_infra/templates/`.
