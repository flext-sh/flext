# Continuation — facade nested owner last, dcdoc strict contract, then the approved Pydantic plan

## Paste this into the next session

> Continue o plano FLEXT no estado atual. SSOT: `.kilo/plans/1795043736423-mod-enforced-pydantic-unification.md` + Bead ativo. Primeiro retome `flext-0in0k.33` na worktree `/home/marlonsc/flext/worktrees/flext-0in0k.33` (branch `fix/facade-nested-owner-last-20261119`): valide/commite o diff 44/11 de `facade_components.py` que coloca o owner canônico por último na composição aninhada, com testes focados; não edite artefato gerado e não rode `make gen` full. Depois valide o dcdoc com `FLEXT=/home/marlonsc/flext` (superprojeto), um único `gen-scope WHAT=facades MODULE=tests SCOPE=self`, e o teste `tests/unit/dcdoc/_infra/test_test_package_strict.py`. Preserve a WIP de `flext-vjj1s.14` (branch `refactor/data-domain-logging-profile-20261119`), o `.32` (`wip/flext-0in0k.32`), a WIP do `flext-infra` attached e os gens concorrentes. Só então siga `.32`, `.14/.24`, `.13`, `.15`, `.16` conforme o plano aprovado.

## SSOT

- Approved plan: `.kilo/plans/1795043736423-mod-enforced-pydantic-unification.md`.
- Active slice: **`flext-0in0k.33`** (P1, claimed by the previous session): nested `Tests` composition puts the canonical owner first; the dcdoc strict contract requires it last.
- Umbrella/epic: `flext-0in0k`; sibling `flext-0in0k.32` (P0, facade generator flattens own parts; outer must inherit only the upstream family, nested composes own parts).
- Pydantic program: `flext-vjj1s`; `.14` is a parallel WIP, `.24` is the deferred `DocumentationLanguage` slice blocked by `.8`.
- Do not re-plan or re-scope these beads. The plan file and the Bead are the authority.

## Current state (as measured 2026-11-19T01:xxZ)

- Root `/home/marlonsc/flext`, branch `0.12.0-dev`; root tip last observed `9b5ef6f5`. Global full `gen` is not green: two full runs were terminated at `flext-tap-oracle` (900 s cap and a persistent 3600 s run that logged `Terminado`; the latter shell appended `GEN_EXIT=0`, so do not treat it as success). Other sessions held concurrent `make gen`/`gen-scope` runs; treat them as inputs, never kill or reset them.
- `flext-0in0k.33` worktree: `/home/marlonsc/flext/worktrees/flext-0in0k.33`, branch `fix/facade-nested-owner-last-20261119`, base `c0da0ebdb7` (`fix(import-law) ... #2633`), one modified file:
  `flext-infra/src/flext_infra/_utilities/facade_components.py` — 44 insertions, 11 deletions.
  The diff:
  - `_facade_retained_providers` drops the `path` parameter, gains keyword-only `project_root: Path | None` and `upstream_last: bool`.
  - The nested-namespace call passes `upstream_last=namespace is not owner`; the outer facade keeps the existing order.
  - `origin_path`/`rank` sort providers imported from outside the project **last**, after the project parts, preserving the `precedence` order inside each group.
  - The occupied-binding failure message uses the module resource path instead of the removed `path`.
- Expected contract (`/home/marlonsc/cosmos-docgen/tests/unit/dcdoc/_infra/test_test_package_strict.py:88-92`):
  - Outer: `tests.u.__bases__ == (flext_tests.FlextTestsUtilities, dcdoc.u)`.
  - Nested: `tests.u.Tests.__bases__[-1] is flext_tests.FlextTestsUtilities.Tests`; the dcdoc parts come first.
  - Current generated `/home/marlonsc/cosmos-docgen/tests/utilities.py:84` still has `FlextTestsUtilities.Tests` **first**; the dcdoc `tests/__init__.py` is an auto-generated lazy re-export and **cannot** reorder the class bases.
- dcdoc consumer `/home/marlonsc/cosmos-docgen`: branch `dev`, behind 10, unrelated WIP in `data/prop-dhl-rfq`, `layouts/marp-theme.css*`, `.build/`. `make setup FLEXT=/home/marlonsc/flext/worktrees/flext-0in0k.33` failed with “not a FLEXT workspace: no .gitmodules” (the member worktree is not a superproject); it did install `flext-infra==0.12.1` from that worktree before failing. The dcdoc `gen-scope WHAT=facades MODULE=tests SCOPE=self` was aborted by the operator. The dcdoc `.venv` is the canonical runtime; do not hand-edit its generated files.
- `flext-vjj1s.14` WIP (separate, preserve): `flext-core` branch `refactor/data-domain-logging-profile-20261119` with uncommitted:
  `LoggingProfile` StrEnum in `_constants/loggings.py`; `FlextSettings.logging_profile` in `_settings.py`; `t.LoggingProfile` alias in `_typings/services.py`; `p.LoggingSettings.logging_profile` return in `_protocols/loggings.py`; `c.LoggingProfile.CONSOLE` in `_utilities/_logging/composition.py`; the redundant test removed. Scoped `make gen ROOT=flext-core` rc=0 wrote `.mise.toml`, `Makefile`, `examples/_protocols/ex11.py`. `mise.lock` is dirty from the tool, not from the slice; do not stage it. `DocumentationLanguage` was deferred to `flext-vjj1s.24` (blocked by `.8`).
- `flext-0in0k.32` WIP lane: `/home/marlonsc/flext-wip-flext-0in0k.32/flext-infra`, branch `wip/flext-0in0k.32` (`origin/wip/...` gone), with broad WIP. The attached `/home/marlonsc/flext/flext-infra` is on another lane (`fix/attached-generation-mise-writer-20261118`) with a different `facade_components.py` change and other WIP. Both are inputs; never reset/stash/checkout/clean them.

## Preserve before switching

1. Re-read `git status --short`, `git -C flext-core status --short --branch`, `git -C flext-infra status --short --branch`, `git worktree list`, and the `.32/.33/.14` Beads. Record the current SHAs and the untracked/ignored state.
2. Preserve the `.14` branch before any worktree switch: commit its explicit source/generated paths on `refactor/data-domain-logging-profile-20261119` (not `mise.lock`) and push the branch as a preserve/lane ref; do not merge it and do not run `make gen` full. If the approved `mod` law is not yet available, leave the Bead `.14` in progress with this commit as the WIP receipt.
3. Do not touch the `.32` lane or the attached `flext-infra` WIP. Work the `.33` fix in its own worktree.

## Ordered tasks

### 1. Finish `flext-0in0k.33` (immediate)

1. Claim/resume the Bead and confirm the `.33` worktree HEAD and the 44/11 diff.
2. Review the diff against the contract above. Keep the fix minimal: no second facade, no new registry, no compatibility branch, no hand-edited generated file. Reuse the existing `FlextInfraUtilitiesFacadeComponents` owners and the existing `p.Infra`/`t.Infra` types; the new rank/origin helper must stay inside the facade owner, not become a parallel inventory or planner.
3. Add the focused regression test for the generator in the flext-infra worktree (existing codegen/facade test area):
   - nested namespace: project parts first, upstream owner last;
   - outer facade: upstream first, project facade second (unchanged);
   - no ordering change when `upstream_last=False`.
   Use the existing fixtures/harness; no mock of the facade composer, no second test runner.
4. Run the worktree's canonical focused validation first (the worktree must use its own runtime; `make setup` only if it has no venv):
   `ruff format --check`/`ruff check` on changed files, the focused pytest selection through the worktree's Make test target, and `pyrefly` on the changed source. Then the canonical `CHECK_PHASE=primary make check` and the affected tests. A full `make gen` is **not** part of this slice; the fix is generator source and must be proven by the focused generator test.
5. Commit only explicit paths:
   `src/flext_infra/_utilities/facade_components.py` plus the new test. Commit message must state the nested-owner-last contract and the outer-order preservation. Push the lane; open a PR against `flext-sh/flext-infra:0.12.0-dev`; merge no-ff after green. Do not update the root gitlink in the same commit.

### 2. dcdoc external consumer (after the flext-infra merge)

1. Update the root gitlink in a separate root commit/PR to the merged flext-infra revision. Preserve the other dirty members.
2. In `/home/marlonsc/cosmos-docgen` use the **superproject** path, not a member worktree:
   `make setup FLEXT=/home/marlonsc/flext`.
   Do not reset the dcdoc branch or its unrelated WIP.
3. Run **one** focused generation of the affected facade, using the canonical `gen-scope` (`WHAT=facades MODULE=tests SCOPE=self` or the narrowest declared equivalent). Do not run the full dcdoc `make gen`. The lazy `__init__.py` is a projection: use its generator owner; do not hand-edit it and do not add a second facade to reorder bases.
4. Verify `/home/marlonsc/cosmos-docgen/tests/utilities.py:84` now emits the dcdoc parts first and `FlextTestsUtilities.Tests` last, while `tests/__init__.py` remains the generated lazy re-export.
5. Run the dcdoc canonical test selection for `tests/unit/dcdoc/_infra/test_test_package_strict.py` (via the dcdoc Make test target; the file selector only if the project's declared Make target supports it). Confirm the outer `tests.u.__bases__` and nested `tests.u.Tests.__bases__[-1]` assertions. Record the dcdoc unrelated WIP as untouched.
6. Close `.33` only with the dcdoc test receipt and the flext-infra PR/merge receipt.

### 3. `flext-0in0k.32` (next slice)

1. Resume the existing `.32` lane; do not recreate the fix. Re-read the Bead’s validated recipe:
   public facade `class FlextDbOracleTypes(t): class DbOracle(Base, TypesDbOracle)`; private part flat; outer `class FlextDbtLdifModels(m, FlextLdifModels): class DbtLdif(parts)`.
2. Fix `_facade_namespace_owner` so a facade with no inherited namespace composes own parts into the nested domain namespace instead of flattening them onto the outer. Preserve the `.33` owner-last ordering.
3. Prove with the `.32` repro (`flext-db-oracle` facades, self scope) and the dcdoc/outer-nested contracts; add/keep the focused generator test; run the canonical checks/tests; commit/PR/merge; update the root gitlink in a separate commit.
4. Only after `.32` is stable, start the God-Object / ≤200-line refactor of the facade namespace composition: extract one cohesive responsibility into an owned helper module (the new module ≤200 lines), reuse `c/t/p/m/u`, keep one owner, and expose it through the generated lazy exports. Do not hand-edit generated `__init__.py`; adjust the generator/source and use the focused generation. This is the `.32`/`.11` slice, not a parallel plan.

### 4. `flext-vjj1s.14` / `.24` and the approved Pydantic program

1. The `.14` manual branch is preserved; do not merge it ahead of the approved `mod` law. When the `.8` generator trust and the `mod` law transaction exist, encode the `literal-domain-enum` law (full-domain `Literal` → `c` StrEnum; `Literal` only for subsets/discriminators beside the enum) and run `.14` through it, or land the small manual slice only if the plan explicitly admits it with all gates.
2. `flext-vjj1s.24` (DocumentationLanguage enum + strict generator consumer) remains blocked by `.8`; do not convert it ahead of the generator or weaken the strict `m.Infra.ModelProtocolRenderContext`.
3. Follow the approved plan phases: Phase 0 census/trust, Phase 1 projection trust, Phase 2 mod transaction, then `.13`/`.15`/`.16`. No full fleet `make gen` until the generator termination/performance owners (`flext-grlt5`, `flext-cldup`, the approved plan) are green; use the focused scopes.

## Validation and receipts

Every slice reports:

| item | command | cwd | exit | decisive output | receipt | file:line |
| --- | --- | --- | --- | --- | --- | --- |

Required receipts:

- `.33`: focused generator test; `ruff`/`pyrefly`/primary check; flext-infra PR/merge; dcdoc strict test; the generated `tests/utilities.py` bases.
- `.32`: the `.32` repro and the outer/nested contracts; the generator test; c/ t/ p/ m/ u reuse; checks/tests; PR/merge; root gitlink.
- `.14/.24`: the approved plan's law receipt and gates, or the preserve-branch SHA plus the Bead note; no claimed green from a partial full gen.
- The full gen must be proven 2× no-op at the integrated tip before a wave closes; a partial/terminated run is not a receipt.

## Constraints and risks

- Never hand-edit a generated `__init__.py`/facade; the lazy `__init__` only re-exports and cannot reorder class bases. The class base order is owned by the facade generator.
- The operator’s “less make gen” means use the narrowest declared focused generator and the lazy-init projections; it does not authorize a second facade or editing projections.
- Preserve the `.32` lane, the `.14` branch, the attached flext-infra WIP, the dcdoc unrelated WIP, and every concurrent generator process. No reset/checkout/restore/clean/stash/`git add -A`; no direct push to `0.12.0-dev`.
- Submodule commit first, then the root gitlink in a separate commit/PR; dcdoc is an external consumer and is validated after the superproject gitlink moves.
- The full fleet generation is currently terminated at `flext-tap-oracle`; do not claim `.33/.32/.14` green from a full-gen attempt. Diagnose the termination only under the approved generator owners, not by weakening gates or adding fallbacks.
- The `.33` dcdoc setup failure was a **FLEXT path contract** failure (member worktree is not a superproject), not a code failure; use the superproject path after the merge.
- If the `.33` fix cannot be proven by the focused generator test and the dcdoc strict test without a full gen, stop only after recording the exact failing gate/file:line and the missing owner; do not add a compatibility path.

## Out of scope

- Rewriting the whole 3,783-line `facade_components.py` in this slice; the ≤200-line extraction is the `.32`/`.11` follow-up and must be its own validated change.
- Moving `config_models.py` into `_models`, the full Pydantic wave, and the root/`flext-infra` AGENTS edits; these need separate operator authority per the approved plan.
- Any reset/repair of unrelated dcdoc data/layout WIP.

---

## Consolidation note (2026-11-20)

- `flext-0in0k.33` code landed in `origin/0.12.0-dev` as commit `86ddde18ea` (fix(facade): adjust provider ordering for nested namespaces). Bead `flext-0in0k.33` closed with comment recording the landing.
- `flext-0in0k.32` code landed in `origin/0.12.0-dev` as commit `8576eeadf1` (fix(codegen): compose own facade parts on the nested domain namespace (flext-0in0k.32) (#2727)). Bead `flext-0in0k.32` closed with comment recording the landing.
- Active remaining slices from the approved plan `.kilo/plans/1795043736423-mod-enforced-pydantic-unification.md`: `flext-vjj1s.14` (LoggingProfile, branch `refactor/data-domain-logging-profile-20261119`, flext-core, 24 dirty files, uncommitted) and `flext-vjj1s.24` (DocumentationLanguage, blocked by `.8`), then `.13`/`.15`/`.16`.
- Root `0.12.0-dev` is 12 commits ahead of `origin/0.12.0-dev` (AI Hub MCP wrapper + testmon cache + pin commits). flext-core and flext-infra carry uncommitted lane WIP that must be preserved and landed via PR before the next slice.
- Execution form for future sessions: continue on `0.12.0-dev` tip; never direct-push; submodule commit first then root gitlink in separate commit/PR; use focused `gen-scope` not full `make gen`; full gen must be proven 2x no-op at integrated tip before a wave closes.
