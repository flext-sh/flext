# ADR-022 — External Consumers as Propagation Guests

<!-- TOC START -->

- [Context](#context)
- [Decision](#decision)
- [Consequences](#consequences)
- [Rejected alternatives](#rejected-alternatives)
- [Verification contract](#verification-contract)

<!-- TOC END -->

- **Status:** SUPERSEDED (2026-10-08) by
  [ADR-024](024-di-config-contract-derived-defaults-minimal-overrides.md) — a workspace
  that lists its consumers violates dependency inversion (D1, D5): consumers pull through
  their own `make upg`, and FLEXT declares nothing about them. Historical record of the
  2026-10-05 implementation (root PR #417, `flext-20yyv`).
- **Date:** 2026-10-05
- **Scope:** `config/workspace.yaml` (manifest SSOT), `flext-infra`
  (`ExternalConsumerSpec`, `workspace/propagation.py`), the five declared external
  consumers, and every future out-of-workspace repository the manifest admits.
- **Complements:** ADR-003 (workspace topology — the manifest is the SSOT for who is
  in the fleet and who visits it), ADR-008 (neutral consumer boundaries), ADR-015
  (consumption law — consumers consume through published refs and their own verbs),
  ADR-021 (the `make fix` those lanes run carries the mandatory unsafe-fix channel),
  ADR-023 (the repair engines the lanes share with the mod loop).
- **Tracking:** `flext-20yyv`.

## Context

Five repositories outside the workspace consume FLEXT as sibling checkouts, not
submodules: `algar-oud-mig` (integration `0.12.0-dev`), `cosmos-main` (`develop`),
`cosmos-docgen` (`dev`), `invest` (`dev`), and `dataop` (older Makefile generation,
without the `fix-namespace`/`fix-accessors` verbs). When the fleet advances — locks
move (`make upg`), projections regenerate (`make gen`), repair engines gain reach
(`fix-namespace`, `fix-accessors`) — consumers drift unless the same wave reaches them.
None of them, however, is fleet property: each keeps its own governance, its own
integration branch, and its own review flow, and two adjacent areas
(`datacosmos.bkp`-class credential/backup areas) hold no code repositories at all.
FLEXT needed a declared, bounded way to carry a fleet wave into a consumer without
imposing fleet governance or touching what must never be automated.

## Decision

1. **Declared guests, typed.** The manifest SSOT (`config/workspace.yaml`) carries an
   `external_consumers` section; each entry is an `ExternalConsumerSpec`
   (`flext-infra/src/flext_infra/_models/_config/workspace.py`): `name`, absolute
   `root` outside the workspace, `integration_branch` (the consumer's own), and
   per-consumer `fix_namespace` / `fix_accessors` toggles. A consumer not in the
   manifest is not a guest; a guest is never silently a member.
2. **Per-consumer lane through the consumer's own canonical verbs.** Propagation
   advances each consumer in its own lane branch by running the consumer's declared
   canonical Make verbs, in order: `upg` → `gen` → `fix-namespace` (if enabled) →
   `fix-accessors` (if enabled) → `fix` → `fmt`, then publishes one PR per consumer
   repository against its declared integration branch. The workspace never edits
   consumer files by hand, never bypasses the verbs, and never merges into the
   consumer's branch.
3. **Consumer governance untouched.** FLEXT law (this AGENTS.md, the ADR set, the
   submodule topology, fleet gates) is not imposed on a guest: the consumer's own
   AGENTS.md, config, and CI govern its lane. Toggles stay explicit in the manifest —
   `invest` declares `fix_namespace: false` and `fix_accessors: false` — and are never
   inferred from file inspection at run time.
4. **Credential areas never enter automation.** `datacosmos.bkp`-class
   credential/backup areas — no code repositories — have no manifest entry, no scan,
   no propagation, no verb run, ever. Absence from the manifest is the guard, and the
   manifest comment records the exclusion so the boundary outlives the authors.
5. **Deferred consumers defer by declaration.** `dataop` rides a later wave because
   its Makefile is an older generation without the repair verbs; it joins when its
   Makefile regenerates through the same flow, and the deferral is recorded in the
   manifest comment, not in run-time special cases.

## Consequences

- A fleet wave reaches every declared consumer as one reviewable PR each; blast radius
  per consumer is one lane, and a red consumer never blocks another.
- The guest relation is visible in one place (the manifest SSOT) and typed, so
  membership, guests, and excluded areas cannot be confused.
- Consumers receive fleet-wide law changes (for example ADR-021's mandatory flag) only
  through their own regenerated verbs — the propagation lane is an invocation surface,
  never a patch channel.
- Roots are absolute because consumers are sibling checkouts; moving a checkout is a
  manifest edit, not code.

## Rejected alternatives

- Submodules — consumers keep independent repositories, governance, and integration
  lines; submodules would convert guests into members and couple their release
  cadence to the fleet's.
- Direct file edits from workspace scripts — bypasses the consumer's canonical verbs,
  produces changes no consumer gate or review validated, and cannot be replayed.
- A FLEXT-owned runner installed inside each consumer — imposes fleet tooling on
  non-member repositories and duplicates the verb surface the consumer already owns.
- Auto-detecting consumers by scanning the filesystem — undeclared guests, undeclared
  exclusions, and a credential area one glob away from automation.

## Verification contract

- A propagation dry run lists, per consumer, exactly the verb sequence its manifest
  entry implies (toggles honored; `invest` omits both repair verbs) and the declared
  integration branch.
- Each published consumer PR contains only changes its own verbs produced, and the PR
  body records the verb list (`upg, gen, fix-namespace, fix-accessors, fix, fmt` —
  minus disabled verbs).
- No path under a `datacosmos.bkp`-class credential area appears in any manifest
  entry, log, or lane diff.
- Manifest round-trip: `make gen` accepts the declared section unchanged and rejects a
  spec missing `name`, `root`, or carrying a relative root.
