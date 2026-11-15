# FLEXT convergence — session handoff (2026-11-14T12:41Z)

> **ARCHIVED — 2026-11-15**
> All tracked PRs are now merged. This handoff is superseded by the merged state.
> See: flext-cli#411 (merged); flext-infra#2456 (merged); flext#610 (merged); flext-api, flext-observability, flext-auth, flext-core lanes merged.

This supersedes the execution state of the earlier convergence plan. The goal and
constraints are unchanged: finish the WIP, merge every convergence slice, leave the
complete `make check` green on the integration tip, and retire the residue. No new
features.

**Re-verify every SHA, PR state, and worktree status below before acting.** The
values are last observed in this session and other actors share the board.

## 1. What this session completed

- **flext-cli#411** merged. Merge commit `5e97db792d9e34c8c709e3d0c7db57ec267eb6f9`;
  the new cli integration tip is `5e97db79`.
- **flext-infra#2456** merged after merging `origin/0.12.0-dev`. Merge commit
  `c3d37c8b7b25b73b87134526ba5c54c23e185c2e`; the new infra integration tip is
  `c3d37c8b`. The lane's local `CI=N make check CHECK_PHASE=primary` passed before
  the merge.
- Both merges used `--admin` under the operator's 2026-11-14 completion mandate,
  recorded in a PR comment. The real blocker was **not** review:
  - required approving reviews = 0 and `reviewDecision` empty;
  - the integrity rulesets require `merge-guard` (root and cli) and `release-plan`
    (cli), but no workflow in either repo produces `merge-guard`, and flext-cli has
    no `release-plan.yml`;
  - flext-infra required only `ci` + `release-plan` (both green) and still reported
    BLOCKED.
- Defect filed: **`flext-o88as`** (P1 bug) — stale required check contexts. Repair
  the ruleset/workflow owners; never add a fake check.

## 2. Current state

### Open PR and first slice

- **flext#610** is still open (last observed head `809292a9071d5db9f6814dd3a4295a3c1088b204`,
  base `05c75d1430`). Its local lane `/home/marlonsc/worktrees/flext/root-bump-20261114`
  (branch `fix/root-bump-20261114`) has **staged gitlinks**:
  - `flext-infra` → `c3d37c8b`
  - `flext-cli` → `5e97db79`
  - `flext-core` stays `ba238c2478`.
  - `CI=Y make gen` has run once; the working tree showed only those two gitlinks
    (no generated projection changes). The second gen pass, primary check, commit,
    push, CI, and merge are **pending**.
  - Update the PR body: it currently names cli `52e69ab5` and the infra lane tip
    (`5b9798147`/`ce40220e`); it must name the merged integration tips above.

### In-flight member lanes (edits applied, not yet set up/committed)

1. **flext-api** — `/home/marlonsc/worktrees/flext-api/api-request-payload-20261114`,
   branch `fix/api-request-payload-20261114`.
   - `src/flext_api/_utilities/request_utils.py`: `build_request_payload` now returns
     `p.Result[p.Api.HttpRequest]`, builds `m.Api.HttpRequest(...)` through
     `r[p.Api.HttpRequest].create_from_callable(lambda: ...)`, and failure paths use
     `r[p.Api.HttpRequest].from_failure(...)`. The intermediate `m.ConfigMap` is gone.
   - `src/flext_api/api.py`: the `.flat_map(lambda payload: u.parse_model(...))` step
     is removed; the chain is `.flat_map(self.request)`.
   - **Not set up, not gated, not committed.** Verify `create_from_callable` preserves
     Result semantics for invalid method/URL and admits `bytes` bodies. If review or
     mypy rejects it, the fallback is `u.parse_model` plus widening its core input to
     admit request-body bytes (move that to the core lane; do not cast bytes).
2. **flext-observability** —
   `/home/marlonsc/worktrees/flext-observability/observability-labels-json-20261114`,
   branch `fix/observability-labels-json-20261114`.
   - `src/flext_observability/services/custom_metrics.py`: `resolve_metric_info`
     validates labels with `u.json_value_adapter().validate_python(metric.labels)`
     into `t.JsonValue` before `m.Dict`.
   - Not set up, not gated, not committed.
3. **flext-auth** —
   `/home/marlonsc/worktrees/flext-auth/auth-settings-identity-20261114`,
   branch `fix/auth-settings-identity-20261114`.
   - `tests/unit/test_api.py`: exact identity via `id(value) == id(settings)`.
   - Setup done; focused mypy 0 errors; `CI=N make check CHECK_PHASE=primary` passed;
     `CI=N make fmt` passed (no-op).
   - Docs repairs already applied in this lane:
     - `docs/architecture.md` retired to a short historical pointer (the v2.0.0 code
       samples referenced non-existent types and were not executable).
     - `docs/configuration.md`: malformed four-backtick fences fixed; blind
       `except Exception` → `except ValueError`.
     - `docs/development.md`: added `tm` and `c` imports.
     - `docs/getting-started.md`: added `c`, `FlextContainer`, `tm` imports.
   - **`CI=N make fix` is still red** at `docs/guides/authentication.md:85`
     (`tm` undefined). This is a pre-existing docs-example debt across the auth
     guides; the fixer stops at the first failure, so iterate. The remaining map is
     in section 4.
   - Not committed, no PR yet.
4. **flext-core** —
   `/home/marlonsc/worktrees/flext-core/core-typealias-identity-20261114`,
   branch `fix/core-typealias-identity-20261114`.
   - `tests/unit/test_utilities_models_family.py`: the type-alias check now uses
     `any(id(annotation) == id(TypeAlias) for annotation in annotations)` with
     `eq=False`.
   - Not set up, not gated, not committed.

### Not started

- **Infra SSOT policy lane** (authorized, conditional on evidence). No lane exists
  yet. `mypy_path` is still `["src"]`; no `meltano.*` override exists.
- **Final root bump** for the member fixes and the infra policy.
- **Beads/retirement/docs/RCA closure**.

### Beads

- `flext-5jsar` (P1, open) — convergence umbrella; add every receipt and merge SHA.
- `flext-2gzbh.10` (P0, in_progress) — Docs timeout/open-PR reds; close only after
  Docs is green on the merged tip.
- `flext-o88as` (P1, open) — stale ruleset required checks (created this session).
- `bd create` hit a transient MySQL timeout once; retry is okay.

### Authorizations

- Operator authorized both narrow mypy SSOT changes **conditionally on evidence**:
  1. `mypy_path` `["src"]` → `["src", "."]` (root-owned `scripts` package).
  2. A `meltano.*` override with `follow_untyped_imports = true`, same shape as the
     existing `rope.*` axiom, **only** if the six meltano findings reproduce and the
     mechanism is mypy failing to authenticate the installed distribution.
- Operator's completion order authorizes landing these convergence PRs. If the
  ruleset still blocks with every declared check green, use `--admin --merge` only
  for these PRs, after recording the mandate and the exact head in a PR comment.
  Never admin-merge anything else.

## 3. Ordered next actions

### Step 0 — Re-verify state (read-only)

1. Fetch root and every governed member; record tips, open PRs, dirty paths, active
   gates. Compare with section 2; newer repo state wins.
2. Re-read #610, #2456, #411, `flext-5jsar`, `flext-2gzbh.10`, `flext-o88as`.
3. Confirm no other actor is editing the target lanes.

### Step 1 — Land #610 (first slice)

1. In `/home/marlonsc/worktrees/flext/root-bump-20261114`: fetch; merge
   `origin/0.12.0-dev --no-ff` if the base moved.
2. Confirm the staged gitlinks are the merged integration tips above; update the PR
   body.
3. `CI=Y make gen` (second pass; must be a no-op); `CI=Y make check CHECK_PHASE=primary`.
4. Commit with explicit paths, push, wait for CI and the Docs workflow, merge
   (`--merge`, `--admin` only if the stale-check-ruleset still blocks), verify the
   merge commit on `origin/0.12.0-dev`.
5. If the PR is merged with the old pins instead, open a follow-up root bump; do not
   leave the root submodules detached from the integration tips.

### Step 2 — Finish the auth lane (source + docs)

1. Repair the remaining docs-example blocks listed in section 4. Use the canonical
   `CI=N make fix` loop; it stops at the first failure, so repeat until green.
   A diagnostic scanner exists at `/home/marlonsc/tmp/kilo/scan_auth_docs.py`
   (outside the repo; diagnostic only, not evidence).
2. `CI=N make fix` green; `CI=N make fmt` no-op; focused mypy 0; `CI=N make check
   CHECK_PHASE=primary`; `CI=N make tests`.
3. Commit the test fix and the docs repairs with explicit paths. Push a PR. If the
   docs tail is too large to finish in the same slice, split it into a dedicated
   `fix/auth-docs-examples-20261114` PR and record it on `flext-5jsar`, but **do not
   leave the final root `make fix` red**.
4. Merge after green; record the merge commit.

### Step 3 — Flext-api lane

1. `make setup` in the lane; focused mypy; `CI=N make check CHECK_PHASE=primary`;
   `CI=N make tests`.
2. Prove the real request boundary: the API tests that build and send requests must
   pass, including a `bytes` body and invalid method/URL failure results.
3. `CI=N make fix`/`fmt` no-op; commit with explicit paths; push PR; merge after
   green. Record the merge commit.

### Step 4 — Flext-observability lane

1. `make setup`; focused mypy; primary check; tests.
2. Verify `resolve_metric_info` returns the same labels for scalar values and a
   stable `JsonValue` mapping for nested labels; no behavior change.
3. `make fix`/`fmt` no-op; commit/push/PR/merge.

### Step 5 — Flext-core lane

1. `make setup`; focused mypy; primary check; tests.
2. The change is test-only; prove the assertion still fails if a field annotation is
   `TypeAlias` (temporary local check is enough; do not commit a fake).
3. `make fix`/`fmt` no-op; commit/push/PR/merge.

### Step 6 — Infra SSOT policy lane (authorized, conditional)

Create from `flext-infra` `origin/0.12.0-dev` (must include `c3d37c8b`).

1. **Re-measure the six `meltano.*` findings** at the new pins with the canonical
   focused mypy route. Capture command, cwd, exit, interpreter, site-packages path,
   and whether `meltano` is importable. Installed `meltano 4.4.1` ships `py.typed`
   and the generated config already has `follow_untyped_imports = true`; the handoff's
   "untyped distribution" diagnosis is unproven.
2. **scripts** (authorized): change `mypy_path` `["src"]` → `["src", "."]` in
   `flext-infra/src/flext_infra/config/tooling.yaml`. Reason: the repo root is the
   `scripts` package root; `src` is not a package, so no duplicate module name is
   expected. Run `make gen`; prove every governed pyproject and the root projection
   changed. If `source-file-found-twice` appears, stop and report; a different key
   needs a new authorization.
3. **meltano** (conditional): only if step 1 proves the six findings and the
   mechanism is mypy not authenticating the installed distribution, add the
   `meltano.*` override exactly as authorized. If it does not clear the findings,
   stop and report; do not add another key or suppression.
4. `CI=Y make gen` twice; `CI=Y make check CHECK_PHASE=primary`; commit/push/PR/merge.
5. After merge, update the final root lane's infra gitlink, run `make gen`, and prove
   the root `scripts.hooks` finding is gone with the focused mypy/complete check.

### Step 7 — Final root bump and complete proof

Create/refresh a root lane from the merged `origin/0.12.0-dev`:

1. Pin the merged tips for flext-core, flext-infra, flext-cli, flext-api,
   flext-observability, flext-auth (and any other touched member). Regenerate; never
   hand-edit generated files.
2. `CI=Y make gen` twice (second no-op); `make fmt`/`make fix` no-op.
3. `CI=Y make check CHECK_PHASE=primary`.
4. `CI=N make check` complete to **32/32** in a persistent/background process; record
   the receipt path and exit 0. A 23/32 stop is not evidence.
5. `CI=N make tests` and `CI=N make tests-full`; record receipts.
6. Verify the Docs workflow on the final merge commit; record the run ID.
7. Merge after the exact head is green; record the merge SHA.

### Step 8 — Beads, docs, RCA, retirement

1. `flext-5jsar`: receipts, merge SHAs, the docs-example debt, and the final complete
   check. Close only when check + tests are green at the final tip.
2. `flext-2gzbh.10`: close only after Docs is green on the merged tip.
3. `flext-o88as`: repair the ruleset/workflow owner or record the operator-owned
   decision; do not add a fake check.
4. Update affected `AGENTS.md`/`CLAUDE.md` only where this convergence changed state;
   never hand-edit generated projections. Record the RCA: single-gate deadline for
   the Docs timeout, untrusted whitespace for MD064, the untyped `ConfigMap`/invariant
   mappings/protocol identity for the mypy findings, the stale ruleset contexts for
   the PR stall, and the stale docs examples for the `make fix` debt.
5. Retire merged worktrees/branches only after `git status` clean, no active process,
   and `git merge-base --is-ancestor <head> origin/0.12.0-dev`. Use `git branch -d`,
   never `-D`. Preserve the `make-check-complete-budget-20261113` experiment on a
   pushed ref (or record the rejection) before removing it; verify
   `preserve/infra-rig-wip-20261114` on its actual origin. Never touch the other
   actors' worktrees (`adr-*`, `agents-*`, `loc-cap-*`, `root-*` on their branches,
   `tmc-flext-ws`, `ci-layout`, `mypy-ruling-*`, `fix/root-envrc-*`,
   `fix/mcp-direct-launcher-*`, `docs/loc-cap-*`, the kilo pool).

## 4. Auth docs repair map (remaining; iterate `make fix`)

Last scanner output (diagnostic only; the fixer is the authority):

- `docs/guides/authentication.md:85` — `tm` undefined; add
  `from flext_tests import tm`.
- `docs/guides/integration.md`:
  - `:78` — `FlextContainer`; add `from flext_core import FlextContainer`.
  - `:183`, `:239` — `c`; add the `c` letter from the package that owns the used
    scope (`flext_auth` or `flext_core`), then let `make fix` sort.
  - `:386`, `:603` — `auth_m`; replace with `m` and ensure `m` is imported.
  - `:527` — `tm`; add `from flext_tests import tm`.
- `docs/troubleshooting.md`:
  - `:48`, `:71`, `:99`, `:110`, `:141`, `:465`, `:552` — `c`; add the letter.
  - `:167`, `:199` — `u`; add `from flext_cli import u`.
  - `:218`, `:439`, `:449`, `:509`, `:519` — possible indentation/fence issues; the
    fixer will confirm after the earlier blocks pass.

Rules: do not change a fence language to hide a block; do not add suppressions; do
not introduce fictional types. If a block describes a type that no longer exists,
retire the block or point to the current API, as done for `docs/architecture.md`.

## 5. Evidence and validation matrix

| Scope | Command | Evidence |
| --- | --- | --- |
| each member lane | focused mypy, `CI=N make check CHECK_PHASE=primary`, `CI=N make tests` | receipt + exit 0 |
| each member lane | `CI=N make fix`, `CI=N make fmt` | no diff, exit 0 |
| root | `CI=Y make gen` ×2 | second pass no-op |
| root | `CI=N make check` | 32/32, receipt path, exit 0 |
| root | `CI=N make tests`, `CI=N make tests-full` | receipts, exit 0 |
| Docs | workflow on the final merge commit | run ID + success |
| PRs | exact head green; review or recorded admin mandate | check runs + merge SHA |
| retirement | ancestor/PR proof, clean worktree | `merge-base --is-ancestor`, `status` |

## 6. Guardrails and known traps

- Re-verify before acting; this handoff is not live state.
- No lint-rule change beyond the two authorized items; no `disable_error_code` edit;
  no suppressions, stubs, hardcodes, fallbacks, or generated-file hand edits.
- No `stash`, `reset`, `rebase`, or force-push. Merge `--no-ff`.
- The auth docs tail is pre-existing debt; fix it at its owner rather than excluding
  the files or weakening the fixer.
- `--admin` is only for these convergence PRs, with the mandate recorded and every
  declared check green; `flext-o88as` tracks the ruleset defect.
- Heavy verbs run one at a time under ADR-032 admission; light reads, Beads, and docs
  continue while a heavy verb queues.
- Gas City mail is unavailable (suspended city, store/binary skew); coordinate via PR
  comments and the shared board.
- A green partial, a focused receipt, or a 23/32 check is not Done.
