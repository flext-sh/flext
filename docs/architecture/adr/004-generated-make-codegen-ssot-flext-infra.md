# ADR-004 — Generated Make and codegen SSOT owned by `flext-infra`

<!-- TOC START -->

- [Context](#context)
- [Decision](#decision)
  - [1. flext-infra codegen conform is the sole owner](#1-flext-infra-codegen-conform-is-the-sole-owner)
  - [2. The Makefile is a self-contained generated artifact](#2-the-makefile-is-a-self-contained-generated-artifact)
  - [3. custom.mk is a narrow private extension surface](#3-custommk-is-a-narrow-private-extension-surface)
  - [4. Conformance is deterministic and fail-closed](#4-conformance-is-deterministic-and-fail-closed)
- [Consequences](#consequences)
- [Verification contract](#verification-contract)
- [References](#references)
- [0.13 unified planning reconciliation (documentation only)](#013-unified-planning-reconciliation-documentation-only)

<!-- TOC END -->

- **Status:** Accepted (replaces the former Make registry decision)
- **Date:** 2026-06-28
- **Amended:** 2026-10-23 (operation ownership and incremental validation)
- **Scope:** generated Makefiles, repository conformance, command routing, and custom
  project handlers.
- **Tracking:** `mro-wkii.17`

<!-- mro-wkii.17.6 (agent: codex) — replace competing Make owners with the single conform pipeline. -->

## Context

The workspace accumulated generated and handwritten Make surfaces, a testing library
command registry, external includes, script dispatchers, bootstrap generators, and
repository-specific migration paths. Several public targets performed the same action,
while generated files could regenerate themselves during normal Make execution.

Those paths cannot be made deterministic by coordination alone. A generated contract
needs one declarative input, one validated renderer, and one public handler for each
action.

## Decision

### 1. `flext-infra codegen conform` is the sole owner

The explicit repository conformance interface is:

```text
flext-infra codegen conform --root <path> --scope self|members|all --mode check|apply
```

`flext-infra` owns typed planning, profile selection, policy enforcement, and the write
transaction. `flext-cli` owns the universal config, schema, template, file, process, and
output primitives consumed by the pipeline. `flext-core` remains runtime-minimal. The
dependency direction is always:

```text
flext-infra -> flext-cli -> flext-core
```

Generation, conformance verification and structural transformation share these
planning and publication owners through their distinct public operations. Sharing
an implementation does not compose those operations: generation publishes its
declared projections without running the quality gates or structural migrations;
conformance verification is explicit and read-only. Project creation and explicit
candidate bootstrap reuse the same models, schemas, context, renderer and templates.
There is no legacy renderer or fallback producer.

The atomic Make operations follow the canonical command rule's operation-ownership
contract. Setup installs existing locked inputs; upgrade resolves and writes locks;
generation produces projections; modification transforms structure; repair fixes;
formatting formats; checking verifies; tests execute their declared population.
Prerequisites, hooks and callbacks preserve those boundaries. Input and output
integrity checks belong to the operation; a full quality check belongs to an
explicit check invocation. Missing cold-start inputs require their explicit owner,
without hidden generation, lock reconciliation or installation in another verb.

For `flext-0029c`, [ADR-010's native-flow trust amendment](010-unified-project-standardization-via-codegen.md#2-common-verb-surface-for-every-project)
retires pre-install Python setup admission and its copied artifact. The existing
Make/direnv template and catalog owners must delegate provisioning to native
Mise/uv, not port that installer to AWK/shell or another lock parser. Official
Mise acquisition and native locked tool provisioning precede `uv sync --locked`
into the owned physical `.venv`. Installed typed provenance and the
separately consumed post-install import guard remain after native installation,
without retroactive installation attestation. Coordinate the wider generated
cutover with `flext-itpd1.4.13`; direct public Infra subsystem QA comes first and
Make integration last. Other operation ownership and generated-file rules remain.

### 2. The Makefile is a self-contained generated artifact

One template layer emits the complete versioned Makefile for the `workspace` or
`standalone` profile from
`flext-infra/src/flext_infra/templates/project/base/Makefile.j2`. Make never regenerates
itself and never includes a shared implementation from another checkout. Generation
and conformance use their declared public verbs; `check` is read-only.

> **Selector-free (since 2026-09-14).** Verbs are selector-free; mutation is the verb
> default (see root AGENTS.md operator law 2026-09-14). The `WHAT=` selector contract
> described below is retired.

The typed `make.verbs` catalog owns builtin names, profile applicability, descriptions
and named inputs. The operator-approved common surface is `setup`, `upg`, `gen`,
`mod`, `fix`, `fmt`, `check`, `tests`, `help`, `build` and `clean`. Declared product
extensions join it through the repository's existing typed registry. Diagnostics,
profiling, documentation actions and former subverbs belong to their operation's
existing owner, not additional common public targets. `make help` and the per-verb
contract view project that declaration; neither is an independent source of truth.

The sole common testing verb, `tests`, executes the complete applicable suite once
with the existing persistent Testmon database. It has no incremental prepass or
public file/full aliases. Workflow, hooks, receipts and CI cache publication consume
the same typed testing declaration.

General help displays each verb's declared named inputs. A builtin contract view
(`OPTIONS=Y` or `HELP=Y`) displays those inputs without running its prerequisites,
hooks or handler. These flags describe the interface, not an alternate effect mode.

Every operation maps to one canonical handler. The initiating generation or
modification operation completes its coherent publication, including required
generated dependencies, through the same SSOT, semantic engines and publisher.
It never recursively invokes another public verb. Public aliases, duplicate
implementations, daemon targets and alternative dispatch routes are invalid.

### 3. `custom.mk` is a narrow private extension surface

A versioned `custom.mk` may contain only private handlers admitted by the typed
custom-handler policy. Its schema rejects public targets, aliases, help or toolchain
ownership, setup logic, generated-target redefinition, and handlers whose verb is
outside the canonical surface.

The public surface is `help` plus the operations projected into `PUBLIC_VERBS`.
Standard lifecycle verbs accept no operation selector. Explicitly declared domain
commands may retain selectors interpreted by their domain registry; this does not
authorize selector-dependent implementations of standard lifecycle operations.
Private target-name dispatch outside that registry is not a second public contract.

### 4. Conformance is deterministic and fail-closed

The pipeline validates the selected declarations and binds every output to its
generating owner. Full-generated files have no author-editable region; mixed files
preserve author-owned and separately owned regions; scaffold seeds become authored
unless an existing recurring generator owns their projection. Missing or competing
owners fail explicitly for every artifact family.

Publication preserves the operation's first causal exception and its traceback.
Independently admitted effects remain available for fix-forward, while any failed
required component keeps the aggregate operation failed. A partial result never
attests completion. There is no compatibility renderer or silent fallback.

Scaffold generation uses the target's own project, integration, kind and source
declarations and the existing planner. The workspace's `.gitmodules` remains the
only member-list authority. A prepared Git/worktree and complete own declarations
are required. An established non-Python repository that never tracked
`pyproject.toml` may receive the Python automation layer; a missing file alone does
not declare scaffold intent or bypass damaged-metadata checks. Generation
materializes files, while setup installs and bootstraps the runtime. Generation does
not initialize remotes or create empty commits for bookkeeping.

The same declarative input must produce byte-identical output. A second apply has an
empty plan and a new project must converge to the same generated tree as an existing
project with the same manifest.

## Consequences

- `flext-tests` tests public behavior but owns no Make registry or dispatcher.
- Repository-local scripts may implement private handlers but cannot redefine routing or
  generation.
- Replaced generators, templates, dispatchers, and public targets are deleted in the
  same migration slice.
- CI invokes the same canonical verbs and cannot suppress a failing result.
- Refactoring proceeds in bounded slices: documentation is reconciled first,
  implementation and real public runtime follow, and tests change last. Every
  slice retains its native results before propagation. Passing receipt probes
  alone never establishes that the real operation works.

## Verification contract

- Parse and `help` validation cover every generated profile.
- Schema tests reject public custom targets and handler collisions.
- Conformance check performs no writes; apply is atomic and idempotent.
- Public-surface discovery reports only `help` and the operational verbs declared by
  `PUBLIC_VERBS`, with one handler per verb.

## References

- [ADR-003 — Manifest-owned topology, root workspace, and autonomous Git libraries](./003-workspace-tooling-hub-distribution.md)
- [ADR-005 — Config, settings, constants, templates, and schemas SSOT](./005-config-settings-constants-templates-schemas-ssot.md)

## 0.13 unified planning reconciliation (documentation only)

- Disposition for the unified 0.13 plan: Keep generation/Make in Infra; correct stale
  selectors and manifests.
- This note records planning reconciliation only. It does not change the ADR's recorded
  maturity, implementation status, or acceptance evidence.
- Future 0.13 API/ecosystem migration remains gated by `flext-ik359` (publication
  `flext-1wjg1` plus separate authorization) and approval of the documented contracts
  and consumer migration matrix. Current 0.12 validation, bug fixes and documentation
  continue under their owners; the ADR's proposal/status is unchanged.
