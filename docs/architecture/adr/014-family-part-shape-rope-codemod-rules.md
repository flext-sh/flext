# ADR-014 — Family Part Shape Law and Rope-Driven Codemod Rules

> **Amended by ADR-018** (generator declarations): its filename-to-letter tables, closed
> folder lists and advisory-gate lists are superseded; see
> [ADR-018](018-generator-declarations.md).

<!-- TOC START -->

- [Context](#context)
- [Decision](#decision)
  - [1. Semantic facade ownership](#1-semantic-facade-ownership)
  - [2. Declarative Rope rules (one YAML file per rule)](#2-declarative-rope-rules-one-yaml-file-per-rule)
  - [3. Shared change cycle (Rope replication)](#3-shared-change-cycle-rope-replication)
  - [3b. rope-in-gen (one engine, two modes)](#3b-rope-in-gen-one-engine-two-modes)
  - [4. Authenticated publication cycle](#4-authenticated-publication-cycle)
  - [5. Gate alignment (one law, shared consumers)](#5-gate-alignment-one-law-shared-consumers)
  - [6. Native tool responsibilities (amended by ADR-028)](#6-native-tool-responsibilities-amended-by-adr-028)
- [Consequences](#consequences)
- [Verification contract](#verification-contract)
- [References](#references)

<!-- TOC END -->

- **Status:** ACCEPTED TARGET; implementation requires current native receipts
- **Date:** 2026-09-09
- **Target line:** FLEXT `0.12.0-dev`, with `0.13.0` as the forward baseline.
- **Scope:** Every internal FLEXT package with the five private families (`_constants/`,
  `_typings/`, `_protocols/`, `_models/`, `_utilities/`): their internal layout, the
  declarative Rope rule format that governs structural rewrites, the shared semantic
  change cycle in `flext-infra`, and the namespace/codemod gate alignment. Third-party
  forks stay outside FLEXT architecture (fleet boundary, `flext-law`).
- **Tracking:** the active branch-matched Bead (`flext-joe2x` at authoring).
- **Complements:** ADR-005 (config/settings SSOT and canonical pattern), ADR-010
  (unified standardization via codegen), `flext-law` (facade and import law).
- **Operator basis:** operator directives of 2026-09-09 (this session): flat part
  declarations, no pure namespace wrappers, hoist-not-alias, rules in dedicated folders
  as one YAML file per rule driving the dedicated Rope engine, changes replicated
  through the common Rope cycle. The 2026-10-20 governance reconciliation below
  replaces the historical backup-based publication contract.

## Context

At authoring on 2026-09-09, the namespace gate (`flext-infra`,
`validate/namespace_validator.py`) required every
member package to declare the five private families, each beginning with `base.py`, and
every canonical facade to compose its private family through a nested namespace with
multiple inheritance. Members drifted from that law: flat facet files without families,
orphan top-level helper classes (for example a private `_Materialization` StrEnum
declared beside its part class), and pure namespace-wrapper children (a base-less class
whose body only groups constants or classes, such as a `class Dbt:` layer inside a
part). Hand-fixing such shapes member by member is unscalable and produces one-off
rewrites that do not replicate to consumers.

The fleet already owns the required machinery: the ADR-010 codemod cascade (detection
rules shipped one per file, applied through `make mod` until a guarded fixed point), the
shared Rope change cycle (`FlextInfraUtilitiesRopeRuntime` change primitives plus
`rope_project.do(changes)` in `_utilities/rope_class_move.py` and
`_utilities/namespace_moves.py`, which replicate every change to all referencing
modules), and the then-current centralized execution pipeline `FlextInfraUtilitiesSafety`
(`backup_files → transform → validate → cleanup | rollback`, the same cycle behind the
workspace timestamped `.bak` artifacts). These are dated implementation observations,
not an alternative to the amended semantic ownership and publication contracts below.

## Decision

### 1. Semantic facade ownership

The operator's 2026-10-23 amendment replaces the numbered-part and mixin
prescription. This is the target contract, not a claim that the fleet migration
has already passed its runtime and native validation gates.

1. Each package retains its canonical private families and `base.py` entry points.
   Ordinary module filenames do not begin with `_`; facade-owned directories do.
   Python protocol files retain their required names.
2. Related declarations form a meaningful domain directory, such as `_acl`, with
   responsibility-based modules such as `behavioral.py`, `comparator.py`,
   `converter.py`, `events.py`, and `runtime.py`. Do not emit `_part`, `_parts`,
   numeric chunk identities, or arbitrary collision suffixes as module owners.
   At every nested domain level, the module basename states the remaining
   responsibility without repeating a directory-owned prefix. For example,
   `_rope/rope_source_bases_runtime.py` becomes `_rope/source_bases_runtime.py`;
   `_rope/_analysis/rope_analysis_workspace.py` becomes `_rope/_analysis/workspace.py`
   only when native identity proves one unoccupied destination. Preserve a repeated
   word when it names a distinct domain responsibility; ambiguity fails before
   effects rather than manufacturing another suffix.
3. A facade imports its owned concrete subclasses or subfacades and reexports
   only those through its canonical base-class namespace. Implementations remain
   in their declaration owners; the facade does not duplicate their bodies or
   introduce forwarding boilerplate. At each nested stage, callers invoke methods
   through the nearest composed MRO facade, never through a component subclass or
   its implementation module. A domain facade such as `_utilities/rope.py` owns
   `_utilities/_rope/`; `utilities.py` composes that domain facade, and external
   consumers use `u.Infra`. The [nested lazy projection](018-generator-declarations.md#nested-facade-projection)
   preserves this boundary without lifting leaf exports into ancestors.
   Library-owned native exports keep their existing public contracts.
4. MRO composition joins meaningful, self-contained facades. A numbered fragment
   relying on undeclared members of a sibling is not a facade. Do not force extra
   bases or wrappers merely to satisfy a count. Fragments implementing the same
   capability consolidate at one owner rather than receiving invented names to evade
   a destination collision. The [Core failure-factory declaration](https://github.com/flext-sh/flext-core/blob/0.12.0-dev/AGENTS.md#failure-factory-responsibility)
   is one such case, linked back to [ADR-028 Decision 17](https://github.com/flext-sh/flext/blob/0.12.0-dev/docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-17).
5. Only an owning facade imports its internal modules. Other production modules,
   tests, scripts, and examples consume that facade. Preserve declared dependency
   direction and use explicit protocol injection where a runtime back-import
   would otherwise create a cycle.
6. Semantic rewiring updates inheritance, annotations, imports, quoted references,
   exports, and generated surfaces together. Preserve payload behavior and intended
   MRO; reject unresolved ownership and occupied destinations before publication.
   Compatibility aliases and duplicate old/new owners are not migration results.

The refactor and generator owners enforce this contract together. Existing symbol
names are not renamed merely to decorate a file move; any required symbol change
must have a semantic owner and preserve the observable consumer contract.
Recursive generated subfacades apply to all five configured families. The native
source identity elects an existing domain composition before deriving a missing
sibling declaration; a meaningful MRO owner is not duplicated merely to match a
directory's spelling. Children are planned before their owning facade, and their
lazy projections, native source moves and dependent imports share one authenticated
candidate and publisher. Convergence is a source fixed point, not a limit derived
from the number of facade families.

This applies equally when a utility facade extends an upstream public namespace
already inherited by the final facade. Preserve that native contract and the
component's declared dependencies; do not remove necessary inheritance or make a
component depend on undeclared siblings to satisfy a renderer predicate. A predicate's
classification is evidence to diagnose against the declared role, not authority to
invent a universal static-method requirement or a package-specific exception.

### 2. Declarative Rope rules (one YAML file per rule)

Structural shape rules for the Rope engine are planned as declarative YAML files (one
file per rule), mirroring the ast-grep rule file style of the ADR-010 cascade. Current
rule fixtures live under `src/flext_infra/codemod/rules/`,
`src/flext_infra/codemod/tests/`, and `src/flext_infra/codemod/utils/`; the
`flext-infra/config/rules/rope/` surface (ADR-017) now exists on the integration tip
(`README.md`, `flatten-family-namespace-wrapper.yaml`). Operator ruling D-ENF
(2026-09-24) makes `flext-infra/config/rules/` the single home of static enforcement
rules; the rules still under `src/flext_infra/codemod/rules/` are a pending migration
tracked by `flext-itpd1.3.10.9`, not a second home:

The following YAML records the original 2026-09-09 orphan-hoisting rule shape.
Its automatic part-class prescription is superseded by decision 1; it is not an
active rule to copy into the catalog:

```yaml
id: hoist-family-orphan-class
severity: error
message: "top-level orphan class in a family part; hoist as a public nested entity"
files: ["**/_[constants|models|typings|protocols|utilities]/**/*.py"]
rope:
  action: hoist_into_part_class
  rename: { strip_underscore: true, case: pascal }
```

Rules are parsed once at the boundary through the canonical YAML owner (`u.Cli.yaml_*`,
flext-cli) into typed Pydantic models (`m.Infra` rope-rule models); the loader fails
loud on any invalid rule. Detection thresholds and file globs are rule data — never
hardcoded detector branches.

### 3. Shared change cycle (Rope replication)

Family-shape rewrites run inside the `make mod` circuit (`FlextInfraCodemodBatchApply`),
as a phase beside `FlextInfraCodemodSemanticApply`, and extend the common base rather
than introducing a second path:

- Detection consumes the typed rules and produces typed findings.
- Semantic rewrites use the shared `FlextInfraUtilitiesRopeRuntime` /
  `FlextInfraUtilitiesRefactorNamespaceMoves` primitives and native Rope changes
  wherever they express the operation, replicating the change to referencing
  modules before the existing rewritten-file normalization. Distinct capabilities
  that the native workspace model cannot express retain their existing owners,
  as specified in decision 6; no parallel semantic engine is introduced.
- The fixed-point, no-progress guard, and final validation of the mod circuit (canonical
  formatting, zero Ruff/Pyrefly/LSP diagnostics) govern the phase identically.

Rope source folders use the canonical empty resource path for the repository root,
not `.`. A dot-prefixed source folder gives declarations a second resource identity
(`./provider.py` versus `provider.py`) and can leave a declaration unchanged while
renaming its consumers. The atomic declaration/caller regression also verifies that
unrelated homonyms retain their names.

### 3b. rope-in-gen (one engine, two modes)

The 2026-09-15 operator ruling (plan-of-record `rope-gen engine strict/total init`,
Bead `flext-crd1y`) established one shared engine. Its gen-only projection-writer
restriction is superseded by the current root
[operation-ownership contract](../../../AGENTS.md#build--test) and
[Make guide](../../guides/make-commands.md#operation-ownership), reconciled here on
2026-10-26: `gen` and `mod` complete their own dependent projections through the
same typed planner and publisher, without recursively invoking another public verb.
This alignment records the target contract, not completed implementation, runtime
acceptance or fleet rollout.

1. **One engine.** The Rope change primitives (`FlextInfraUtilitiesRopeRuntime` /
   refactor / `_utilities/rope_*`) are the shared motor. There is no second engine and
   no reimplemented lazy-init.
2. **Shared engine, distinct operations.** The historical `codegen init` and `conform`
   modes do not establish a second public lifecycle. Generation renders current
   declarations; `make mod` owns semantic and structural rewiring. Each uses the
   existing shared primitives within its declared operation.
3. **One projection owner and publisher.** Generated facets and lazy exports remain
   owned by their generator declarations and templates. Both `gen` and `mod` use
   that owner to publish the projections required by their own coherent change;
   neither calls the other public verb. Hand-written split output is adoption
   input, never authority. Divergence is repaired at the canonical source and
   re-proven, not patched by a competing projection writer.
4. **Strict/total init.** Generated `__init__` exports are the ordered union of the
   immediate modules' explicit `__all__`: a sibling without `__all__` emits warning
   `GEN-W001`, which blocks acceptance until corrected; a
   stale `__all__` (export listed but absent from the sibling) is an error (`GEN-E001`)
   that fails loud; a symbol collision between siblings is an error. Exceptions are
   declared as one data line in `flext-infra/config/codegen.yaml` (rules-as-data — never
   a detector branch).
5. **Blocking diagnostics.** gen emits `GEN-W*` warnings; `make fix` corrects the auto-fixable
   subset (relativized self-imports `GEN-W002`); `make check` reports anything
   remaining. Warnings remain blocking under the current acceptance contract.
   No detector is ever disabled and no finding turns into a silent success.
6. **Render purity.** `render = f(SSOT, templates, PINS)` and nothing else: any
   environment input (filesystem probing, wall clock, dependency resolution, worktree
   WIP state) reaching the render is a P0 engine defect.
7. **Transactional loop.** Per repository: authenticated original inputs → complete
   candidate plan → publication through the existing atomic owner → durable receipt.
   The native journal owns an active invocation's recovery; a consumed journal
   is not a durable receipt. Do not restore source snapshots or overwrite
   shared work. After committed effects, reconcile forward from the owner's
   receipt. A failed or interrupted invocation is never a successful publication.
8. **Gate before propagation.** Validate the selected producer and complete
   affected consumer group before propagation. The active authorized scope selects
   pilot repositories; historical private repository names are not standing targets.

### 4. Authenticated publication cycle

Family-shape changes reuse the native candidate and authenticated publication
owners described in decision 3b. The earlier `execute_safely` backup/rollback
description records the implementation at authoring; it is superseded by this
2026-10-20 reconciliation and grants no alternative publication route.
Preserve current source identity and shared WIP, use the owner's active journal
only within its lifecycle, and retain durable publication evidence afterward.
No private backup, second writer or repository rollback is permitted.

### 5. Gate alignment (one law, shared consumers)

The [ADR-028 Decision 5](https://github.com/flext-sh/flext/blob/0.12.0-dev/docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-5)
and [Decision 18](https://github.com/flext-sh/flext/blob/0.12.0-dev/docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-18)
amendment of 2026-10-25 supersedes the former "one law, two engines" description.
A static law has one declarative owner in flext-infra's rule catalog; apply and
detection routes consume that owner. Independently maintained detector logic for the
same law is a duplicate to retire. This accepted target does not claim that the
migration from every legacy source is complete; the current owner-claim census and
cutover evidence remain in Bead `flext-43iz8`.

### 6. Native tool responsibilities (amended by ADR-028)

The [ADR-028 Decision 15](https://github.com/flext-sh/flext/blob/0.12.0-dev/docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-15),
[Decision 17](https://github.com/flext-sh/flext/blob/0.12.0-dev/docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-17),
and [Decision 18](https://github.com/flext-sh/flext/blob/0.12.0-dev/docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-18)
amendment of 2026-10-25 makes the 2026-09-15 "three instruments" taxonomy and its
blanket ban on Python parsing/rewriting mechanisms historical, not current policy.
Use the repository-scoped native workspace model and its refactorings wherever they
express the operation; use one generalized declarative rule per law; retain separate
tools only for distinct capabilities that the workspace model does not provide.
Remove duplicated custom analysis and refactoring, not unrelated native functionality.
The current cutover and zero-residue evidence are tracked by `flext-1engx.15`; this
amendment is not proof of implementation completion.

**Historical execution authority (2026-09-17):** Gas City Bead `flext-itpd1.2`
recorded the structural-rewrite state at that date; the recovery references were
this ADR and `docs/roadmap/rope-gen-engine-runbook-2026-09-15.md`. Workspace-local
plans are dated evidence, not published authority.

## Consequences

- The original 2026-09-09 first execution target was
  `flext-dbt-oracle-wms` (its `_constants` enumeration hoist, `Dbt` wrapper flatten, and
  three consumer rewires). This dated inventory does not select current execution targets.
- The original wrapper-flattening example was
  `c.DbtOracleWms.Dbt.PROJECT_NAME` → `c.DbtOracleWms.PROJECT_NAME`.
  Current rewrites require the semantic ownership proof in decision 1; this dated
  example does not authorize flattening a meaningful domain facade.
- Rules, detector, and gate text share one vocabulary; adding a new structural law means
  adding one YAML rule plus its typed action — no engine fork.

## Verification contract

- `make mod` reaches the guarded fixed point with zero pending findings on the target
  member.
- `make check` passes the namespace and codemod gates on the member with the family law
  active; `make tests` validates through the canonical Testmon contract. An
  integrity-checked incremental cache hit is a cache receipt, never tests passed.
- `make gen` proves the generation fixed point after any export-affecting move; zero
  residue (no `.bak`, no orphan files) remains in the tree.

The 2026-10-26 reconciliation aligns the normative text only. It supplies no new
runtime, gate, integration or fleet-rollout acceptance.

## References

- ADR-005 (config/settings SSOT and canonical pattern), ADR-010 (unified
  standardization).
- `flext-law` skill — facade composition, import direction, `make mod`
  structural-rewrite law.
- `flext-infra`: `validate/namespace_validator.py`, `validate/_namespace_rules/*`,
  `codemod/batch_apply.py`, `codemod/semantic_apply.py`, `codemod/sgconfig.yml`,
  `_utilities/safety.py`, `_utilities/rope_core.py`, `_utilities/rope_class_move.py`,
  `_utilities/namespace_moves.py`.
