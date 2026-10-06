# ADR-023 — Repair Phases as Mod-Loop Callbacks

<!-- TOC START -->

- [Context](#context)
- [Decision](#decision)
- [Consequences](#consequences)
- [Rejected alternatives](#rejected-alternatives)
- [Verification contract](#verification-contract)

<!-- TOC END -->

- **Status:** ACCEPTED TARGET — port and both phases implemented on the
  `fix-verbs-mod-loop` lane (`p.Infra.ModLoopPhase`, `codemod/loop_phases.py`,
  `batch_apply.phase_callbacks`); becomes CURRENT IMPLEMENTATION at lane merge with
  convergence receipts.
- **Date:** 2026-10-05
- **Scope:** `flext-infra` (`_protocols/base.py` `ModLoopPhase`, `codemod/`
  batch apply and loop phases, `refactor/` relocation cascade and accessor rewrite),
  the generated `fix-namespace` / `fix-accessors` verbs, the `make mod` loop in every
  member, and the external-consumer propagation lanes (ADR-022).
- **Complements:** ADR-004 (generated Make — the standalone verbs are projections over
  the declared engines), ADR-017 (parametrized rule surfaces — repairs are declared
  data driving shared engines), ADR-022 (propagation invokes the same engines in
  consumer lanes), ADR-019 (service ports — the same typed-port composition style).

## Context

The two fleet repair engines — the namespace relocation cascade (Rope) and the
origin-aware accessor rename — were reachable only as standalone verbs
(`fix-namespace`, `fix-accessors`). A `make mod` pass could move a symbol the accessor
rename had just rewritten, or vice versa, so converging a repository required running
mod, then a repair verb, then mod again by hand, with no proof the repairs and the
AST/semantic/text phases had reached a state together. A repair that fights another
phase ping-pongs: the loop reports progress, the next pass undoes it. The joint fixed
point the mod loop already proves for its built-in phases needed to include the two
repairs, without duplicating either engine inside the loop and without weakening the
standalone verbs.

## Decision

1. **One port.** `p.Infra.ModLoopPhase`
   (`flext-infra/src/flext_infra/_protocols/base.py`) is the contract for one repair
   phase: a `name`, and
   `apply(root, preflight, rope_workspace) -> p.Result[bool]` — `True` marks changed
   sources. After a callback, the loop refreshes Rope, rescans, and continues toward
   the joint fixed point exactly as for its built-in phases.
2. **Two phases, zero duplicated engines.** The namespace phase
   (`FlextInfraNamespaceRelocationPhase`, name `namespace-relocations`) drives the
   shared `FlextInfraNamespaceRelocationCascade` over the preflight's captured
   relocations, per governed project; the accessor phase
   (`FlextInfraAccessorRenamePhase`, name `accessor-rename`) reuses the accessor
   migration's origin-aware rewrite, so a homonym the rename catalog does not own is
   never renamed inside the loop either. Phases are injected as
   `phase_callbacks: t.VariadicTuple[t.Port[p.Infra.ModLoopPhase]]` into the batch
   apply — the loop knows the port, not the implementations.
3. **One engine per repair, three invocation surfaces.** The relocation cascade and
   the accessor rewrite each exist once. They are invoked from: (a) the mod loop, as
   callback phases inside the joint fixed point; (b) the standalone thin verbs
   `fix-namespace` / `fix-accessors`, which remain selectors over the same engines for
   targeted runs; and (c) external-consumer propagation (ADR-022), which runs those
   same verbs in the consumer's lane. A fourth surface, or a second implementation of
   either repair, is a defect.
4. **Convergence law unchanged, now joint.** A phase's changes participate in the
   loop's fingerprint sequence; if the phases return the tree to its starting state
   (cross-phase cycle), the loop fails loudly — "changes retained for mandatory owner
   repair" — instead of claiming convergence. A phase failure fails the mod verb with
   its cause; no phase result is swallowed.

## Consequences

- `make mod` converges once, with repairs inside the proof: the "joint AST, semantic,
  and text fixed point" verdict now also covers relocations and renames.
- The standalone verbs stay exactly as thin as they are — same engines, same flags,
  one invocation surface among three — so their contracts only restate the engines'.
- New repair phases register by implementing the port and joining `phase_callbacks`;
  the loop body does not change per repair.
- Generated `make help` text already declares the truth ("the same relocation cascade
  runs as a callback phase of make mod"; "the same origin-aware rewrite runs as a
  callback phase of make mod") and stays honest only while the single-engine rule
  holds.

## Rejected alternatives

- Pre/post steps around `make mod` — leaves the ping-pong: no joint fixed point, no
  cross-phase-cycle proof, and a documented manual ordering instead of a mechanism.
- Inlining the cascade or rewrite bodies into the loop — duplicates the engines,
  splits behavior between the verbs and the loop, and guarantees drift.
- Discovering phases by class scan or naming convention — implicit registration,
  hidden behavior, and no typed port for the propagation surface to share.
- Making the repairs optional loop passes behind flags — a mod run without the phases
  can claim a fixed point the next repair verb would break; the joint point is the
  contract.

## Verification contract

- On a tree with pending relocations and renames, one `make mod` run converges and
  emits the joint fixed-point verdict with both phases applied; the pre/post alternative
  would have needed interleaved verb runs.
- The cross-phase-cycle guard is proven once: a constructed cycle fails loudly with
  the retained-changes message, never a green no-op.
- Engine identity: `fix-namespace` and `fix-accessors` standalone on the same tree
  produce byte-identical results to the loop phases (same engines, same inputs), and a
  propagation lane (ADR-022) exercises the identical verbs in a consumer.
- `make gen` twice is no-op on the verb projections; `make fix`, `make fmt`,
  `make check`, `make mod`, `make test` green on the changed fleet.
