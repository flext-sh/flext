# Handoff — goal `flext-w8qmv` (2026-11-08)

The plan is `~/.claude/plans/lexical-baking-harbor.md`. The bead is `flext-w8qmv`; run
`bd show flext-w8qmv` and read the latest comments. This handoff summarizes them.

## Operator orders in force (newest first)

- Defects of the same kind are fixed by the owning `make mod` rule or generator: improve
it, generalize it, then apply it through flext-infra to every project, subproject and
text. Rules must not overlap; overlapping rules are unified into the most general,
strictest rule. No ad-hoc fixes and no workarounds (gambiarras).
- Keep committing every checkpoint ("sempre ir gravando").
- Align with the other active Claude sessions:
  - Algar (`local_b9ec5341…`): owns algar-oud-mig, flext-infra #2205 and #2206, and the
  `make tests` reds in flext-core, flext-cli, flext-ldap and flext-tests;
  - Rope (`local_00f079f9…`): owns flext-infra pyrefly-zero;
  - make-mod (`local_14c414e9…`): its lane is unknown.
- `~/flext` is the working base. Every repo is converged on `upload-20261007` (the
integration tip plus every branch, merged `--no-ff`). Never reset, stash, rebase or
force-push. `gh pr merge --admin` is denied by the auto-mode classifier.

## State

- **Converged members:** all 30 members except flext-infra are converged and pushed on
`upload-20261007`. Landing PRs `upload-20261007 → 0.12.0-dev` are open in all 31 repos
(e.g. flext-web#156, flext-ldif#250). flext-infra #2209 is merged (84a9dca1).
- **Member CI:** it checks out root `flext` at `0.12.0-dev`, which still pins
flext-infra at `460ee36075`, so it runs an old flext-infra. The root needs a gitlink
move past #2200 and taplo `c76fb0ba1b`; Algar asks for that workspace SHA. The root and
flext-infra rigs were held by another actor.
- **Rig breakage:** the flext-infra rig has an uncommitted `codegen.yaml` edit by
another actor that makes FlextInfraConfig invalid, so pytest fails to load the
flext-infra plugin in the workspace.
- **My lane:** `~/worktrees/flext-infra/static-rule`, branch
`fix/static-rule-unify-20261108`, PR flext-infra#2214 (base `upload-20261007`). It has
its own `.venv`.
  - **Rule unification:** the staticmethod law is one rule, ENFORCE-102
  `tests-fixture-method-missing-staticmethod`; the duplicate rule is deleted. Fleet
  census: 0 findings.
  - **Import-law fix (d096973855):** `_import_law_own_family_candidate` no longer skips
  family `base.py` modules. The regression test fails without the fix and passes with
  it.
  - **Gates:** ruff and pyrefly pass. The full `tests/unit/refactor` run gives 189
  failed / 243 passed; the base comparison was not done. Do that first: `git show
  HEAD~2:<file>`-style base comparison or a clean base worktree.
- **Member fixes pushed on upload:**
  - dbt-ldif `4ad7352`;
  - oracle-wms `56bacf4`;
  - observability `aa44c7c` (hand edit; to be reproduced by rule `.13`);
  - plugin `1db4d90` and `88ada6a`;
  - oracle-oic `eacfeac`;
  - db-oracle and ldif merge resolutions.

## Next steps (in order)

1. **Refactor-suite baseline:** compare the 189 refactor failures with the base. Fix
only regressions caused by d096973855.
2. **`flext-w8qmv.12`:** with the lane CLI (`.venv/bin/flext-infra refactor mod
--repository-root ~/flext --projects <repo> --rule-ids
tests-fixture-method-missing-staticmethod`), apply `make mod` to the 9 cycle repos:
    - meltano, oracle-wms, target-ldif, target-oracle, target-ldap, tap-oracle-wms,
    tap-oracle-oic, target-oracle-oic, and the root (42 modules).
    - It aborts on "atomic source changed" while another actor edits the flext-infra
    rig; rerun when it is quiet.
    - Commit each repo on `upload`.
3. **`flext-w8qmv.13`:** relocate the fixture holders out of `tests/fixtures` (auth,
cli, infra, observability, tests), by rule.
4. **`flext-w8qmv.14`:** generalize the rule "each package service base binds its own
Settings" (approved for flext-plugin).
5. **Test-secret rule:** finish the B105/B106 rule from the draft in
`~/worktrees/flext-infra/test-secret-rule`, then apply it fleet-wide (auth 8, db-oracle
13, ldap 1, oracle-wms 12, tap-oracle-wms 18, target-oracle 3, web 2).
6. **Root pin:** move the root flext-infra gitlink and the member upload heads, then
land. Send the SHA to Algar.
7. **Other open beads:**
    - `flext-w8qmv.2`: the editor surface builds its own analyzer context
    (`codegen/_conform/editor.py`) instead of the canonical one
    (`deps/_modernizer/document.py`).
    - `flext-1cl2f`: duplicated AGENTS.md managed blocks.
    - `flext-obayy`: `make gen` exceeds its 900 s budget (facades: core 116 s, cli 61 s).
    - pyright: 1674 errors in flext-web; `p` is rebound in `protocols.py`.

## Uncommitted WIP from stopped agents (based on old `0.12.0-dev`)

These worktrees hold uncommitted WIP; adopt it or redo it on the tip:

- `~/worktrees/flext-infra/editor-analyzer-context`;
- `~/worktrees/flext-infra/gen-facades-speed`;
- `~/worktrees/flext-infra/agents-md-projection`;
- `~/worktrees/flext-infra/test-secret-rule`.
