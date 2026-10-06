# ADR-021 — Mandatory Unsafe-Fix Lint Repair Channel

<!-- TOC START -->

- [Context](#context)
- [Decision](#decision)
- [Consequences](#consequences)
- [Rejected alternatives](#rejected-alternatives)
- [Verification contract](#verification-contract)

<!-- TOC END -->

- **Status:** ACCEPTED TARGET — operator law 2026-10-05; supersedes the 2026-09-08
  safe-only posture (flext-itpd1.5) and the T201 incident rationale. Becomes CURRENT
  IMPLEMENTATION when the generator, the `MakeRuffSpec` validator, and every projection
  carry the flag with post-change receipts.
- **Date:** 2026-10-05
- **Scope:** `flext-infra` (Make generation, `MakeRuffSpec` contract, tooling/codegen
  SSOT comments), every generated `Makefile`, the lint repair inside `make fix`, the
  external-consumer propagation lanes (ADR-022), and every member and consumer that
  regenerates the verb.
- **Complements:** ADR-004 (generated Make as codegen SSOT — the flag is declared in
  `flext-infra/config/codegen.yaml`, never hand-edited into a Makefile), ADR-005
  (config SSOT — `unfixable` stays a `tooling.yaml` rule selection), ADR-015
  (consumption law — consumers receive the same verb through regeneration, not patches).
- **Supersedes:** the 2026-09-08 safe-only lint repair posture and its T201 incident
  rationale, both formerly encoded in `MakeRuffSpec._reject_unsafe_fixes`
  (`flext-infra/src/flext_infra/_models/_config/make.py`) and in the
  `lint_fix: [--preview, --fix]` declaration
  (`flext-infra/config/codegen.yaml`).

## Context

An unsafe Ruff fix once deleted diagnostics: T201 removed
`print(..., file=sys.stderr)` from a consumer script and turned its failures silent.
The 2026-09-08 answer (flext-itpd1.5) was to make the lint repair information-safe by
construction:

- `make fix` applied Ruff's **safe fixes only**; `MakeRuffSpec` carried a
  `_reject_unsafe_fixes` model validator that rejected `--unsafe-fixes` inside
  `make.ruff.lint_fix`, backed by the `RUFF_UNSAFE_FIXES_FLAG` constant documented as
  "never part of the lint repair";
- rules whose fixes delete code, comments or diagnostics were declared `unfixable` in
  `tooling.yaml` (T201/`p-print`/`print` among them — the T201 protection lives there);
- an `extend-safe-fixes` channel promoted individual unsafe fixes into the repair with
  per-rule written evidence (relative-imports, TC001, N813).

The posture costs more than it protects: every `make fix` pass leaves findings only
unsafe fixes can close, so repairs need extra passes and manual owner work; the
`extend-safe-fixes` channel grows rule-by-rule evidence reviews for fixes the operator
now simply authorizes; and one tool carries two fix postures (safe-only by default,
unsafe by promotion) whose boundary is documentation, not mechanism. The operator
ruled on 2026-10-05 that the flag is the default, forever, and rule selection — not
flag absence — is the information-preservation guard.

## Decision

1. **The channel is mandatory, everywhere, forever.** `make fix` always runs
   `ruff check --fix --unsafe-fixes --preview` in every project: members, the root, and
   every external-consumer propagation lane through the consumer's own regenerated
   verb. There is no project, selector, or lane where the lint repair drops the flag.
2. **Validation requires the flag.** `MakeRuffSpec` inverts: `lint_fix` MUST contain
   `--unsafe-fixes` (and keeps `--preview` per the 2026-09-08 preview ruling and
   `--fix`); a declaration missing the flag fails validation. The
   `RUFF_UNSAFE_FIXES_FLAG` constant stays the single named spelling of the flag; its
   contract docstring inverts from "never part of the lint repair" to "mandatory in
   every lint repair". `_reject_unsafe_fixes` is replaced by the requiring validator in
   the same change — no period where both postures coexist.
3. **`unfixable` stays as rule selection.** Rules whose fixes delete code, comments or
   diagnostics remain declared `unfixable` in `tooling.yaml`; the T201-class rules
   (`p-print`, `print`) stay there. This is the only information-preservation
   mechanism: a rule is opted out of auto-fix by declaration, never by weakening the
   channel.
4. **The `extend-safe-fixes` promotion channel is superseded.** A fix is either the
   rule's declared behavior (unsafe channel on) or the rule is `unfixable`. Per-rule
   promotion entries retire with the safe-only posture; their evidence notes merge into
   the `unfixable` complement where the rule still must not auto-fix.
5. **Supersession, not accumulation.** The 2026-09-08 safe-only posture (flext-itpd1.5)
   and the T201 rationale ("unsafe fixes delete information") are superseded: T201's
   protection is preserved exactly by the `unfixable` declarations, so the incident is
   answered by rule selection instead of a global flag ban. The SSOT comments that
   still argue the safe-only posture (`codegen.yaml` around `lint_fix`, `tooling.yaml`
   around `unfixable`/`extend-safe-fixes`, the `MakeRuffSpec` docstring, the generated
   `make help` text) flip in the same change.

## Consequences

- `make fix` closes strictly more findings per pass; residual repair work and extra
  passes shrink fleet-wide.
- Risk management moves from a global flag ban to per-rule declarations: the
  `unfixable` census is the audit surface, and a dangerous fix reaching the tree is
  answered by declaring its rule unfixable — never by reverting to a safe-only channel.
- Generated surfaces change together through the canonical flow: `codegen.yaml` gains
  the flag in `lint_fix`, `make gen` regenerates every Makefile and help text, and the
  propagation lanes (ADR-022) deliver the regenerated verb to external consumers as
  guests.
- `make fix` remains "never repeat another gate's mutation" (single-pass verb law):
  only the lint repair's fix strength changes, not the verb decomposition.

## Rejected alternatives

- Keeping safe-only plus a growing `extend-safe-fixes` list — two postures for one
  tool with a documentation boundary, and bounded coverage the operator declined to
  keep paying for.
- Making unsafe fixes opt-in per project — the operator law is "everywhere, forever";
  per-project flags would fragment the fleet and revive the drift the manifest and
  codegen SSOT exist to prevent.
- Dropping `unfixable` and relying on review to catch T201-class deletions — that
  reopens the exact silent-failure incident the declarations close mechanically.

## Verification contract

- `MakeRuffSpec` round-trip: a `make.ruff` declaration without `--unsafe-fixes` fails
  validation with the requiring message; the declared one with
  `[--preview, --fix, --unsafe-fixes]` passes and is what `make gen` projects.
- `make gen` twice reaches a fixed point with the new declaration; every generated
  Makefile's `fix` target shows `--unsafe-fixes --preview`.
- One live `make fix` run per member proves the ruff invocation carries the flag, and
  the `unfixable` census shows no T201-class deletion (no removed `print`/`p-print`
  diagnostic anywhere in the diff).
- `make fmt`, `make fix`, `make check`, `make mod`, `make test` green on the changed
  fleet; propagation re-runs the consumer lanes through their own regenerated verbs
  (ADR-022).
