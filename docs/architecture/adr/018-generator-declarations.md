# ADR-018 — Generator Declarations Law

<!-- TOC START -->

- [Context](#context)
- [Decision](#decision)
- [Consequences](#consequences)
- [Verification contract](#verification-contract)
- [0.13 unified planning reconciliation (documentation only)](#013-unified-planning-reconciliation-documentation-only)

<!-- TOC END -->

- **Status:** ACCEPTED — operator law 2026-09-20; implementation phased under
  `flext-0in0k`
- **Date:** 2026-09-20
- **Target line:** FLEXT `0.12.0-dev`, forward baseline `0.13.0`
- **Scope:** every FLEXT generator, detector and fix (`make gen`, `make mod`,
  `make fix`, the namespace validator and its gates) and every consumer of them: the
  `flext` workspace and its 31 members, ai-hub, cosmos-main and its apps, cosmos-docgen,
  invest and their FLEXT subprojects.
- **Complements:** ADR-010 (standardization via codegen), ADR-014 (family shape +
  codemod rules), ADR-017 (parametrized rule surfaces). Supersedes every filename→letter
  table, closed folder list and advisory-gate list those ADRs tolerated.
- **Rule owner (routing reconciled 2026-10-26):** this branch-matched ADR and the
  local `flext-law` own FLEXT generator declarations. Global governance ADR-0024
  retires the copied `flext/generator-declarations` rule; it is not a second
  binding text to restore or distribute. Universal source/projection and command
  conduct remain with `workflow/generators-not-projections` and
  `workflow/canonical-commands` in the canonical governance catalog. This routing
  correction is not implementation, integration or installed-delivery evidence.
- **Tracking:** epic `flext-0in0k` (a phased bead set, each carrying the full rule text;
  live membership and counts on the epic, never frozen here); superseded `flext-exbwv`,
  `flext-crd1y`, `flext-b3xmn`, `flext-szjre`, `flext-fdoah`, `flext-s9bxq` (closed,
  linked); `flext-ssnc7` and `flext-mbowt` linked, kept open for their unrelated live
  children. Campaign `flext-pipol` (2026-10-28) owns the single-read, single-batch
  publication and gate-clean projection amendments and their implementation evidence.
  The small-transaction amendment below is an accepted contract pending
  implementation and runtime validation, not a claim about the current publisher.

## Context

The lazy-init and `pyproject.toml` generators accumulated accommodations that decide
behavior from names and hand lists instead of declarations: a filename→letter table
(`NAMESPACE_LAYER_BY_FILE`, five readers), closed folder sets (`ROOT_WRAPPER_SEGMENTS`,
`NON_PUBLIC_LAZY_ROOTS`, `ALL_SCAN_PATTERNS`, `env-dirs`/`test-like-dirs`, a literal
fallback in `namespace_config`), a hardcoded `TEST_RUNTIME_ALIAS_TARGETS`, `ALIAS_NAMES`
used as the list of who exists, hand-declared `root_packages`/`root_modules`, a
single-part package name treated as a public root, an advisory-gate list by name, a
guard for one `services/models.py`, and an `examples/` bypass in the validator. Every
consumer of the generator inherited them. On 2026-09-20 the fleet `make gen` broke
(`flext-infra a43dcf547`) because export discovery accepted any class of a module with
no `__all__` and rendered `from .01_basic_usage import …`.

The operator negotiated the correct contract point by point and ordered it to become a
FLEXT rule generators cannot violate, followed by the extermination of every hack and of
the permission that tolerated it, one by one, at the source.

## Decision

This ADR owns the following fourteen generator declaration requirements:

1. A facade letter belongs to the module that declares it in its explicit `__all__`.
2. An `__init__.py` propagates; it never declares.
3. The root inherits from the main module; the root `__all__` overrides.
4. Internal tiers are detected from folders with Python; `src/` is public, the rest
   internal; no list anywhere.
5. Internal tiers inherit by class MRO and declare their own letter; a subdirectory
   declares no short alias.
6. The generator propagates, never compensates; the validator reports.
7. Violations are fixed at the source; recurrence makes a catalog rule with a fixture.
8. Verdict and count derive from one classification and the current
   [phase-completion contract](../../../AGENTS.md#engineering-and-phase-completion-contract).
   The former blanket statement that warnings do not fail is superseded by that
   contract; a warning, missing execution or partial result never proves acceptance.
9. Every rule is computed from an existing source and proven fleet-wide before commit.
10. Declaration adjustment is automatic; deriving beats listing; unnecessary lists die.
11. Every module is one nested class; nothing loose, no alias outside `__all__`; the
    existing rules become `error`.
12. An exception is a single motivated entry authorized explicitly by the operator.
13. A hack's permission dies in the same commit as the hack.
14. Every module obeys every rule (FLEXT, SOLID, DRY, YAGNI, CA, SSOT, DI); strict
    compliance is the dedup mechanism expected to free 60–80% of the code.

### Nested facade projection

The generator applies [ADR-014's semantic ownership](014-family-part-shape-rope-codemod-rules.md#1-semantic-facade-ownership)
recursively: a direct family domain facade composes the declarations in its private
`_domain/` directory by MRO, and nested private directories repeat that pattern.
Each generated lazy `__init__.py` reflects only its immediate modules' explicit
`__all__`; a subdirectory declares no short alias and an ancestor never republishes
leaf implementations around their owner. A source move and the affected subfacade and
ancestor lazy exports are planned and published as one authenticated candidate, from
source without importing the stale package being repaired. Callers use the nearest
composed facade at every stage (ADR-028 [Decision 10](028-facade-boundary-orchestrators-declarative-enforcement.md#decision-10)).

Planning and runtime acceptance are different boundaries. Planning consumes the
source-authenticated native workspace model, including candidate overlays,
without executing the target package. Acceptance exercises the generated public
surface in a fresh process. A source move must not require its obsolete export
map to import successfully before the replacement can be planned.

The existing lazy-map freshness validator remains the owner of drift reporting.
Its source comparison is necessary but not independent proof of correct exports:
runtime acceptance must also resolve declared exports, their native identities
and consumed MRO capabilities. Static and lazy bindings account for declared
eager metadata without lifting child exports into ancestors. Missing targets,
colliding identities and invalid ownership fail explicitly.

Generation retains the first causal failure and the publisher's confirmed
effects. It does not catch an import failure and continue publishing other
repositories. Unreached work remains unexecuted. The bootstrap consolidation
contract belongs to
[ADR-014](014-family-part-shape-rope-codemod-rules.md#core-lazy-bootstrap);
`flext-s9r3a` and `flext-1engx.15` retain implementation ownership under the
`flext-brr3y` campaign.

### Model and service protocol projection

**Amendment 2026-10-28 — accepted operator target, implementation and runtime
acceptance pending.** `flext-vjj1s.8` owns the existing model-to-`p` restoration;
the operator's newer instruction extends that owner to first-party service
contracts, source-module layout, automatic consumer rewiring and pilot coverage.
The MRO/Pydantic analyzer and environment acceptance tracked by
`flext-itpd1.13.11` remains incomplete and is not replaced by this amendment.

Every `make gen` derives model and service structural protocols through the
existing flext-infra projection owner. Its input is the complete authenticated
native Python inventory of the elected repository/workspace, including `src`,
`tests`, `examples`, `scripts` and every other discovered Python module. These
examples are not a closed tier list. Discovery and classification follow native
declaration identities, inheritance, nested facade ownership and specialization;
neither filename spelling nor an existing consumer reference limits coverage.
Every discovered model and service receives an accounted classification and
projection disposition. Unresolved identities fail with their original cause;
they are not omitted or normalized into an empty successful projection.

The output describes the first-party declaration's actual structural contract.
Model protocols preserve effective field and computed-property types,
inheritance, generic specialization and read/write capability. Service protocols
preserve their own public callable contracts, including sync/async behavior,
parameter kinds, defaults in signatures, overloads, generics and return types.
This does not copy an external SDK into a local typing surface. Existing authored
DI ports remain their declared capability owners; generation neither replaces
them with a service implementation nor weakens an originating contract.
Constructors, validation, field defaults/factories, schema, model configuration,
validators, serializers and handler metadata retain their real runtime owners.
A structural projection never becomes a second runtime model, validation engine
or operation/schema registry.

Projection modules correspond to the semantic source-module owners of the
models and services and group the declarations owned by those modules. They live
in the canonical protocol family under [ADR-014](014-family-part-shape-rope-codemod-rules.md#1-semantic-facade-ownership),
without a `generated` directory/prefix or one file per model. Existing names and
ownership are resolved through the native inventory. Ambiguous ownership or an
incompatible occupied destination fails explicitly before effects; no numbered
suffix, guessed basename or per-symbol mapping table resolves a collision.
Generated protocols, authored ports, composed facades and lazy exports preserve
their distinct owners and public identities.

The existing native Rope workspace model and reference graph drive discovery,
annotation resolution and automatic rewiring through flext-infra. `make gen`
derives the projection on every invocation; `make check` compares its drift
without mutation. Authored annotation and layout cutover, structural consumer
rewiring and obsolete-owner retirement belong to `make mod`, under
[ADR-010's operation ownership](010-unified-project-standardization-via-codegen.md#3b-semantic-discovery-and-automated-rewiring).
Generation does not execute an authored codemod or invoke `make mod`. The existing
modification candidate includes dependent protocols, facades and lazy exports
through their existing projection owner as coherent migration effects; it neither
invokes `make gen` nor implements another generator.

The approved Rope DSL entry is `RopeWorkspaceDsl.protocol_projection()`, returning
one typed, invocation-local `ProtocolProjectionPlan`: projected sources, native
source-to-protocol identities, declaration classifications and dependency edges.
Both operations consume this same projection owner. The modification integration
uses the existing `ModLoopPhase.plan` callback contract and `CodegenFilePlan`
composition after structural callbacks, not another loop or fake per-symbol
`RopeContractRule` pattern. The invocation owns the native session/snapshots and
injects them across callbacks; changed candidate views refresh incrementally.
This is the accepted implementation target, not proof that the entry or callback
has been implemented or validated.

Every structural cutover candidate closes all actual affected workspace consumers:
imports, annotations, inheritance, quoted references, facades and lazy exports
move together. Generation must fail before effects when publication would require
an unplanned authored cutover or leave a consumer pointing to a retired identity.
It reports that original ownership/consumer failure rather than omitting the
projection, publishing a partial replacement or retaining an old/new compatibility
route. A legacy projection is retired only when its generated ownership and
preimage are authenticated and native reference accounting proves that the same
coherent candidate rewires every affected consumer. A filename prefix or generated
header alone never authorizes deletion. Do not publish a protocol and leave its
callers for a later transaction.

Both operations reuse the existing rule catalog, candidate, publisher and read-only
drift comparison; no new public composite verb, parallel scanner, semantic database,
publication engine or manual call-site sweep is introduced. Unchanged observations
reuse native caches and changed resources refresh incrementally under the
transaction contract below.

Complete this entire pattern before extending the same native mechanism to other
expensive ast-grep patterns. Profile the real path with cProfile, tune
the measured owner through CA/DI and existing native capabilities, and preserve
all detection and runtime behavior. The first pilots are distant from core and
follow the existing S5 order: `flext-dbt-ldif`, then `flext-tap-ldif`, then
`flext-target-ldif`. That order is not proof of sufficient coverage; extend the
pilot cases afterward where the native inventory proves a gap. Derive a
variation/coverage matrix from the complete inventory and cover every actual
variation before scaling to the fleet.
Every pilot transaction still includes all of its affected workspace consumers.

**Phase-admission amendment 2026-10-28 — operator authorized, implementation and
runtime acceptance pending.** The operator answered the exact drift-admission
question: "Autorizar admissão por coorte, com pilotos publicados e integrados antes
da frota (recomendado)". The bounded change is generation drift admission from the
whole planned fleet to explicitly admitted coherent cohorts during the pilot.
All Python checker scopes and diagnostic rules remain unchanged. This extends the
existing transaction/admission owner with typed, declarative enrollment, phase
prerequisites and coverage policy.
Discovery and generation planning remain complete across the workspace;
only coherent admitted pilot effects are published before fleet rollout,
including every affected caller outside the initial pilot projects.

Drift admission evaluates the coherent admitted candidate while the fleet remains
explicitly incomplete. It does not filter a final global file list: shared facades
and lazy exports must be recomposed for that candidate through the same planners.
Staged pilot qualification alone is not the selected acceptance strategy.

Fleet effects require complete pilot variation coverage, published-pilot runtime,
applicable native gates and integration proof; staged validation alone does not
replace those receipts. Unelected work
remains explicitly unexecuted and incomplete, never full-workspace success
or an accepted skip. The mechanism must retain the selector-free root
Make interface and unchanged checker includes/excludes, CI mode, file filters and
diagnostic rules. No public selector, project-name allowlist, parallel projector
or orchestration pipeline is introduced. Existing typed configuration owns the
policy grammar, with native inventory/source identities binding cohort coverage.
Beads remains the execution-state owner and publisher receipts remain evidence,
not another tracker. The small-transaction interface and runtime proof below
remain prerequisites where implementation is pending; this authorization certifies
neither their readiness nor a completed pilot.

Successful pilot proof admits only the fleet rollout of this same pattern.
Finish its fleet-wide definitions, uses and complete consumer rewiring, real
runtime proof, applicable native gates and integration closure before beginning
another pattern. A passing pilot never authorizes switching patterns while that
rollout or any affected consumer remains incomplete.
The existing five-second transaction and sixty-second Make budgets, source
authentication, own-effects rollback and frozen analyzer rules remain unchanged.
Acceptance requires real public runtime and invalid-case detection, native
gates, complete coverage accounting, repeated generation/refactoring fixed point
and integrated evidence; a source restoration or sampled pilot is not completion.

### Single-read, single-batch publication (amended 2026-10-28, campaign `flext-pipol`)

**Amendment 2026-10-28 — accepted contract, implementation pending.** The
operator-approved small-transaction and cooperative-reader boundary supersedes
the earlier invocation-wide, physically atomic batch interpretation. It also
authorizes the narrowly scoped rollback below instead of the historical blanket
rollback prohibition; no unrelated WIP or completed independent transaction is
rolled back.

Within one repository invocation, an unchanged source observation is read and
parsed once. One native workspace model per repository (ADR-028
[Decision 17](028-facade-boundary-orchestrators-declarative-enforcement.md#decision-17))
feeds generation, lazy planning, model→protocol and docs. Changed observations
refresh incrementally in that same engine, invalidating only affected native
resources and dependent snapshot facts; no phase rebuilds the repository model
or repeats unchanged discovery. Each small transaction contains a complete
dependency closure, including moved sources, consumers, facades and lazy exports.
Its candidate is staged beside the existing mutation lock on the destination
filesystem, outside the working tree, and validated before live publication.

The existing publication owner extends its common mutation barrier to
cooperating Make and Rope readers. A reader enters before bootstrap imports,
configuration reads, discovery or any other live observation of the affected
scope. It retains protection for every later lazy read, or consumes a pinned,
independent candidate that requires no further live reads. A writer holds the
same barrier through source verification, file effects, Git-index retirement,
modes, directory creation/prune, incremental cache/model refresh, bounded
validation and durable completion. Multiple scope locks are acquired in one
canonical physical-root order, never with an inverted nested acquisition.
Subprocess validators consume the staged candidate and must not reacquire a
barrier their parent holds.

This guarantees atomic visibility of each transaction to those cooperating
readers, not an operating-system atomic replacement of several paths. An
uncooperative editor or raw reader is outside that visibility guarantee; its
changes remain protected by identity checks. Waiting for the barrier consumes
the same public Make deadline; it never creates an extra timeout budget.

Before the first effect, the publisher durably records the transaction identity,
scope, original observations and owned intended effects in its operational
record. It records completion only after validation and model refresh. Every
cooperating reader inspects that record while holding the barrier. An
interrupted or inconsistent transaction rejects live reads even when process
death has released the lock. Recovery reconciles that same record and its
authenticated effects before admitting readers; it never treats an absent
process or an expired lock as successful publication. The record belongs to
the publisher, not a substitute Beads tracker, semantic index or global cache.

On failure, preserve the first cause and undo only this transaction's proven
effects in reverse order, guarded by compare-and-swap against authenticated
published states. This includes index entries, file modes and owned directory
effects. A conflicting external edit is preserved and keeps recovery explicit;
no global reset, historical restore or blind overwrite is permitted. Cleanup or
rollback failures remain attached to the primary failure and the operational
record remains unresolved until recovery is proved. Earlier committed
transactions remain intact; the containing operation is still failed and
unreached work is not successful.

The entire incremental transaction takes at most five seconds, including staged
validation, publication, native refresh and bounded rollback. The existing
performance policy owner declares that budget; the whole Make invocation,
including lock waits, staging and recovery, remains within sixty seconds.
Transaction sizing must leave recovery margin inside these limits. Fast
validation never weakens the frozen analyzer rules or replaces the complete
gates and real consumer proof required for the slice. Exhausting either budget remains a
failure. Superseded planning/publication routes are removed in the same cutover.

The [repository declaration](https://github.com/flext-sh/flext-infra/blob/0.12.0-dev/src/flext_infra/_models/_config/repository.py#L457-L466)
makes `project` optional. An absent subsection declares no additional manifest-only
inherited facets: the generator still uses source-authenticated MRO and explicit
`__all__` for ordinary lazy exports, but must neither invent a manifest nor reject
the public root for lacking one. An explicitly declared facet is still verified
against its upstream native identity before publication. The
[lazy-init owner](https://github.com/flext-sh/flext-infra/blob/0.12.0-dev/src/flext_infra/_utilities/lazy_init_letters.py#L148-L207)
consumes this contract and links back to this decision.

Order of execution (operator): law → extermination of lists, manual declarations and
their permissions → generator/detector/fix repair → census by the validator → automatic
correction (`make mod`) → consumers → strict compliance → close. One bead per phase;
work in the authorized shared-workspace boundary; never roll back unrelated work;
never a manual mass fix. The amendment above alone authorizes guarded reversal
of an unsuccessful transaction's own effects.

## Consequences

- `flext-infra` loses every table and list named in Context; the replacement is one
  derivation each (`u.Infra.discover_python_dirs`, the module `__all__`, the class base,
  the folder on disk). Their permissions (exclusions, bypasses, advisory lists) leave in
  the same commits.
- Every consumer regenerates; the diff is the inventory of hacks it carried. Two
  flext-infra forks (`flext-sh@0.12.0-dev`, `datacosmos-br@baseline-20260919`) converge
  to one line.
- The namespace validator reports one-nested-class, no-alias and nothing-loose
  violations as `error`; the fix derives letter ⇄ base and writes the declaration.
- Measured populations at decision time: 42 internal facades without the letter in
  `__all__` (10 repos, 0 in `src/`), 5 letters bound to non-extending classes, 4 dead
  example classes, 36 numbered scripts inside packages (12 repos), 8 public + 18 private
  reserved names in nested packages, 61 internal inits with divergent shapes.

## Verification contract

- `make gen` exits 0 in 32/32 and a second run has no diff, after every flext-infra
  commit of the epic — before the commit is pushed.
- `make mod` twice is idempotent; the validator's counts above reach 0.
- `make check` and `make test` green in 32/32 and in every consumer; no new exclusion.
- One unchanged observation, one read (campaign `flext-pipol`): profiling receipts
  (`make.generation_profile_path`, `modification_profile_path`) show no repeated
  parse of unchanged source across phases. Changed paths refresh incrementally
  in the same engine; a second consecutive `make gen` has zero artifact effects.
- No partial transaction (campaign `flext-pipol`): a planning failure leaves
  that transaction's live destinations untouched. A publication/validation
  failure reverses only its authenticated owned effects before readers are
  admitted; completed earlier transactions remain intact and the invocation
  remains failed.
- Cooperative visibility and recovery (accepted contract, implementation
  pending): concurrent Make/Rope readers observe only a committed transaction
  or a proven preimage. A crash between file/index/directory effects leaves a
  durable interruption that blocks readers until guarded recovery. Injected
  failure restores only owned effects; conflicting external WIP is preserved.
- Bounded admission (accepted contract, implementation pending): prove the
  five-second transaction and sixty-second Make budgets, including barrier
  waits, staged validation, incremental refresh and recovery. Full slice gates
  remain separately mandatory.
- Gate-clean by construction (campaign `flext-pipol`, ADR-028
  [Decision 8](028-facade-boundary-orchestrators-declarative-enforcement.md#decision-8)):
  `make gen` followed directly by `make check` is green, and `make fmt` /
  `make fix` are no-ops, on every repository.
- Logical LOC measured by the canonical verb before the first commit and after the last;
  the delta is recorded on `flext-0in0k`.
- `bd lint --json` clean for every bead of the epic; each closes with SHA, command and
  exit code.

## 0.13 unified planning reconciliation (documentation only)

- Disposition for the unified 0.13 plan: Reaffirm declarations as export source and
  generation; update API examples.
- This note records planning reconciliation only. It does not change the ADR's recorded
  maturity, implementation status, or acceptance evidence.
- Future 0.13 API/ecosystem migration remains gated by `flext-ik359` (publication
  `flext-1wjg1` plus separate authorization) and approval of the documented contracts
  and consumer migration matrix. Current 0.12 validation, bug fixes and documentation
  continue under their owners; the ADR's proposal/status is unchanged.
