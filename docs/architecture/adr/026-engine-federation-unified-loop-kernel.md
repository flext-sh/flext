# ADR-026 — Engine Federation: Unified Loop and Parametrized Rule Registry

<!-- TOC START -->

- [FLEXT Law Anchors (binding for every slice under this ADR)](#flext-law-anchors-binding-for-every-slice-under-this-adr)
- [Context](#context)
- [Proposed decision (not implemented or accepted by this record)](#proposed-decision-not-implemented-or-accepted-by-this-record)
- [Supersessions](#supersessions)
- [Exceptions](#exceptions)
- [Consequences](#consequences)
- [Rejected alternatives](#rejected-alternatives)
- [0.13 unified planning reconciliation (documentation only)](#013-unified-planning-reconciliation-documentation-only)

<!-- TOC END -->

- **Status:** PROPOSED — draft recording campaign decisions D1–D7 (2026-10-13).
  Campaign closure (phase F6.4) does not automatically accept this ADR or prove implementation.
  Acceptance requires explicit review against current authority and the evidence below.
  Campaign plan and evidence:
  `.kilo/plans/2026-10-13-engine-unification-p0/` (not published authority).
- **Date:** 2026-10-13
- **Scope:** `flext-infra` orchestration: `codemod/` (batch apply, gates, text gates, loop
  phases), `refactor/` verbs, `check/` workspace checker, `codegen/` pipeline + transaction,
  `release/`, `deps/`, `workspace/` fleet; `_protocols/base.py`, `_models/` (scan, check,
  config), `_utilities/` (refactor evidence, discovery, iteration, project resolution,
  protected edit), `config/rules/**`, `config/codegen.yaml` / `tooling.yaml` sections; the
  generated Make verbs; every fleet member as consumer by projection.
- **Proposed supersession:** the adjudication recorded in bead `flext-q69hv`
  (stdlib-`ast` import-law engine sanction); no supersession is established by this draft.
- **Proposed amendments:** ADR-005 §6, ADR-010 §3b, ADR-014 §3b, ADR-017, ADR-019,
  ADR-023, ADR-024; their current authority remains unchanged.

## FLEXT Law Anchors (binding for every slice under this ADR)

Every slice follows the [governance authority route](../../GOVERNANCE.md#authority),
[root law](../../../AGENTS.md), [session router](../../../.agents/commands/flext-law.md),
and exact [FLEXT law](../../../.agents/skills/flext-law/SKILL.md).
The [engineering conformance review](../../GOVERNANCE.md#engineering-conformance-review)
routes SSOT/YAGNI/DRY/SOLID, Pydantic, DI, and Clean Architecture to their canonical
owners. The private campaign checklist is execution evidence, not normative law.

Before each proposed extraction, record its existing domain owner, public namespace,
`c -> t -> p -> m -> u` declaration boundary, affected consumers, and obsolete route
in the active Bead. Acceptance requires reuse at the correct owner, complete consumer
cutover, and removal of the superseded mechanism; neither a shared-kernel name nor
this proposed ADR authorizes a parallel engine or competing rule SSOT. Runtime,
fixed-point, and fleet-green requirements below are acceptance conditions, not
receipts that those conditions have been met.

The existing engine roles remain binding: ast-grep performs declared mechanical Python
fixes, Rope performs semantic refactors, and real `pyright-langserver` diagnostics validate
the fixed point ([ADR-014](014-family-part-shape-rope-codemod-rules.md),
[ADR-017](017-parametrized-rule-surfaces-single-modernize-cli.md), and local FLEXT law).
This draft establishes no new engine owner and cannot override that composition.
The architecture below is proposed, not an implementation inventory or green receipt.
The operator's original frozen D2 requires Python semantics/analysis through Rope
and retirement of competing internal engines. This draft's narrower description
below does not supersede or soften D2. That discrepancy remains pending explicit
review and the corresponding source/consumer cutovers; this note neither approves
the draft nor certifies those cutovers.
Constraint recorded 2026-10-28 (operator order; ADR-028
[Decision 17 amendment](028-facade-boundary-orchestrators-declarative-enforcement.md#decision-17)):
rope is the only accepted Python interpreter in FLEXT-authored code — ast-grep
(declarative rules carrying their fix forms), sed and the generator stay canonical
in their own domains, and stdlib `ast`, `libcst` and `re`-on-code engines are
banned. This accepted law binds the draft: item 4's "not exclusive Rope ownership
of every Python transformation or read-only analysis" may not be read as
permission to retain an alternative Python parser, and the parametrized rule
registry (item 2) must reject any engine entry that parses FLEXT-authored Python
outside rope's single index. The draft stays PROPOSED; this note constrains its
design and records no acceptance.
Acceptance evidence must identify the complete affected repository, engine, rule, owner,
and consumer inventory with revision and source provenance, then demonstrate actual
public runtime behavior, applicable canonical gates, and validated cutover/retirement on
the integrated candidate. Bead or campaign closure alone is insufficient.

## Context

The campaign inventory reports that `flext-infra` owns build, repair, and verification
loops in the FLEXT fleet and operates nine-plus orchestrators over five rewrite engines,
four loop implementations, four
phase abstractions, four receipt disciplines, four Python-source walkers, four project
resolvers, and three file-application paths (evidence inventory: campaign plan
`10-references.md`). Four independent rename implementations and three TYPE_CHECKING cleanup
implementations coexist. The `make mod` joint fixed-point loop
(`codemod/batch_apply.py:_converge`) is described as proven and disciplined, but sibling
verbs re-implement convergence, evidence, and publication. Ad-hoc internal engines (`re`
patterns, stdlib `ast` rewriting, `libcst` transformers, `tokenize` offset editing) duplicate
what the declared engines and the Rope workspace provide. These inventory and behavior
claims require current full-scope provenance and runtime evidence before acceptance.

The campaign records decisions D1–D7 (2026-10-13): proposed text-engine scope is non-Python
and malformed-Python recovery; Python work retains the canonical ast-grep mechanical,
Rope semantic, and LSP validation roles; the proposed unified orchestration covers each
loop family; increments land one at a time as
pure refactors with zero functional loss and constant functional validation; every engine
(checks, fix, fmt, template, ast-grep, rope, sed, docs) cooperates with a distinct
responsibility, never competing or duplicating; all engines consume shared facilities (SSOT,
DRY, CA, DI); orchestration is strict SOLID; parametrized rules are mandatory at all
times — never hardcoded; the campaign CORRECTS AND REFACTORS what exists (no parallel
structure), each phase delivering high net code reduction with full extermination of
superseded code; a standing
role keeps ai-hub (a heavy flext-infra consumer) green.

## Proposed decision (not implemented or accepted by this record)

1. **One loop contract, refactored in place (no parallel structure).** The linear engine
   is the existing flext-cli `cli.pipeline`/`cli.linear_pipeline` (already adopted by the
   check and codegen loops), extended to the remaining families. The fixed-point engine
   is the proven
   `codemod/batch_apply._converge` behavior extracted in place into a reusable
   `s` service in the `codemod/` domain directory, serving the sibling
   refactor verbs with injectable fingerprint/judgment strategies. The phase contract is
   `p.Infra.ModLoopPhase` (ADR-023) extended in place (admission, rope requirement) — no
   sibling protocol. `m.Infra.LoopOutcome` is the single envelope. Fan-out behaviors remain
   with their owners (violations-sweep repair verbs; fleet thread pool). Every slice is
   a refactor of existing classes: unify, reduce, move, standardize, rewire — never a new
   parallel family or duplicated mechanism (campaign D6). These extraction, placement,
   protocol and envelope choices remain proposals pending owner/consumer and runtime
   validation; this record does not establish their implementation or authorize cutover.
2. **One parametrized rule registry (SSOT).** Every rule in `config/rules/**` (ast-grep,
   sed, rope operations, CSV rename campaigns) declares `id`, `engine`, `capability`
   (detect|transform|fix|generate|verify), `target`, `repair`, `admission`, `expected_counts`,
   `phase`, `seq` — extending the existing `u.Infra.codemod_rule_plan` models and sha256
   cache, never a second loader. Every command declares its loop mode and phase
   selection/order in config (ADR-024 typed models with fail-closed cross-validators in
   the model, following
   `_validate_local_check_gates`). No phase list, engine choice, or application order is
   hardcoded in Python. Tests read the registry; they never freeze it (P0).
3. **Existing engine responsibilities are preserved (federation).** ast-grep: declared
   detection and mechanical Python fixes. Rope: semantic refactors and their semantic
   facts (occurrences, identity, imports, rename, move, restructure). Real
   `pyright-langserver` diagnostics validate the fixed point. sed:
   non-Python files and malformed-Python recovery only; rules targeting valid Python
   migrate to rope/ast-grep and the registry rejects new ones. ruff fix/fmt: lint repair
   and formatting — final authority on form. template (jinja2): declared
   generation/projection only. docs
   engine: documentation validation/generation. check gates: verification only; mutation
   solely under the `--apply` verb law.
4. **Proposed ad-hoc engine cutover.** Removal of competing Python rewrite engines follows
   ADR-014 and ADR-017 through the existing mechanical/semantic pipeline, not exclusive
   Rope ownership of every Python transformation or read-only analysis. Transformer
   extraction, trivia preservation (campaign bead `flext-1ha3`), and analysis migration
   require owner/consumer inventory and real behavior evidence before selecting or retiring
   an implementation. This draft neither selects a replacement class nor certifies a fork
   capability. Each slice requires validated equivalence and complete cutover; any exception
   requires its own authorized Bead and exit under current law.
5. **One shared service per concern.** Single guarded receipt publisher (atomic write,
   byte+mode read-back, sha256 receipt) for every report/evidence artifact, including check
   reports, release receipts, pytest reports, and gate capture (which gains an in-process
   mode; the fresh-interpreter subprocess remains a declared attestation option). Single
   Python-source walker. Single project resolver with explicit modes. Gate vocabulary
   SSOT-projected (the Makefile stops carrying copies). Single file-application path executing
   the campaign's per-unit atomic plan→apply proposal (bead `flext-h9eax`). Retirement of
   the codegen transaction lease/journal remains proposed, subject to current authority,
   complete safety/consumer provenance, and runtime/gate evidence; it is not authorized
   or established by this draft.
6. **Consumption by projection.** Fleet members receive the kernel, registry, and verbs
   through `flext-infra conform` generation and inherit fleet rules by the ADR-017
   discovery mechanism.
   The federation keeps maintained projects strictly on FLEXT standards without member-local
   implementations.
7. **Slice discipline.** Every increment is one slice: smallest indivisible change, pure
   refactoring, zero functional loss, full battery green (`fmt/fix/check/mod/mod-rules/test`),
   stable rule snapshots (or regeneration only via `make mod-snapshots` with documented
   intent), functional proof on a real fixture, high net LOC reduction with the superseded
   owner fully exterminated in the same change (no dual paths; extraction slices
   F1.1/F1.2 may be neutral), bead with evidence, no-ff merge from the integration tip.
8. **ai-hub consumption stays green.** Every slice that changes CLI routes, config
   shapes, or rule declarations ships with the corresponding ai-hub adjustment in the
   same wave (standing
   follow-up role), so external consumers never drift behind the federation.

## Supersessions

- The campaign proposes superseding bead `flext-q69hv`'s stdlib-`ast` import-law sanction
  under epic `flext-itpd1.12`. Its recorded closure does not prove a validated replacement
  or retirement; this draft does not select exclusive Rope ownership.
- No ADR or adjudication is superseded by this proposed record. Proposed amendments in
  the header require explicit reconciliation and acceptance; current law remains binding.

## Exceptions

(none at draft; every future exception is one motivated entry with a bead and an exit —
operator authorization required, ADR-018 style)

## Consequences

- Positive: one learnable orchestration surface; engine responsibilities without overlap;
  rule behavior fully data-driven and replayable; duplicated implementations deleted;
  member
  projects strict by projection; loop semantics (fingerprint, verdicts, receipts) proven
  once and reused by every verb.
- Negative/controlled: migration touches the most safety-critical machinery of the fleet
  — each slice carries snapshot-equivalence proof and the ten mapped integration risks
  (campaign plan `02-f1-kernel-loop.md` §Riscos) require validation one-by-one; any proposed
  Rope-fork
  maintenance for trivia preservation requires capability evidence; the campaign estimates
  ~35 slices landing over multiple sessions under the fleet coordinator (`flext-itpd1.3`).
  These are campaign estimates and proposed consequences, not a validated extraction or
  retirement inventory.
- Verification contract: catalog validator fail-closed; zero-proof dogfooding rules (ban
  competing rewrite mechanisms) must follow current law through the fleet's codemod gate;
  repeated generation/repair/formatting no-op receipts and the applicable full-fleet battery
  must be proven on the integrated candidate. Fleet scope and counts derive from the
  canonical composition and complete inventory, not a frozen 32/32 claim. None of these
  results is established by this record or by campaign closure.

## Rejected alternatives

- A new `_loop/` top-level family: rejected (operator D6) — violates the FLEXT package shape;
  the loop behavior is extracted in place instead.
- A dedicated second pipeline engine inside flext-infra: rejected — `cli.pipeline` from
  flext-cli is already the adopted linear engine.
- A parallel rule-catalog loader: rejected — extends `codemod_rule_plan` and its cache.
- Keeping a competing rewrite engine: proposed rejection subject to the existing law and
  validated owner/consumer cutover (see §Supersessions).

## 0.13 unified planning reconciliation (documentation only)

- Disposition for the unified 0.13 plan: Remain proposed; record extraction/D2 divergences
  before any acceptance.
- This note records planning reconciliation only. It does not change the ADR's recorded
  maturity, implementation status, or acceptance evidence.
- Future 0.13 API/ecosystem migration remains gated by `flext-ik359` (publication
  `flext-1wjg1` plus separate authorization) and approval of the documented contracts
  and consumer migration matrix. Current 0.12 validation, bug fixes and documentation
  continue under their owners; the ADR's proposal/status is unchanged.
