# FLEXT Make command surface

<!-- TOC START -->
- [Conventions](#conventions)
- [Public verbs (`PUBLIC_VERBS`)](#public-verbs-publicverbs)
- [Gas Town CLI surface](#gas-town-cli-surface)
- [`gen` (codegen SSOT)](#gen-codegen-ssot)
- [Integration line (operator gate)](#integration-line-operator-gate)
- [`work` saga](#work-saga)
- [Quick recipes](#quick-recipes)
<!-- TOC END -->

Canonical reference for the workspace Make control plane on `0.12.0-dev`.
Discover live verbs with `make help` only. Do not invent retired verbs.

The Gas Town CLI (`gt`) is the worker dispatch surface. See the
[worker lane contract](../../ways-of-working/worker-lane-contract.md#6-gas-town-cli-surface)
for the full `gt` command reference. The Make verbs below are the operator
control plane; `gt` commands are the worker execution surface — complementary,
not interchangeable.

## Conventions

- Format: `make <verb> [WHAT=<action>] [PROJECT=<member>] [APPLY=Y]`
- Discovery: `make help` (there is no `WHAT=help` on most verbs)
- Mutation: verbs that change the tree require `APPLY=Y` (`deps` upgrade/lock, `fmt`/`fix` apply, `gen` apply, `docs` generate/fix, `clean`, `work` start/land/finish)
- Scope: omit `PROJECT`/`PROJECTS` to fan out across declared workspace members from the root

## Public verbs (`PUBLIC_VERBS`)

| Verb | Default WHAT | Notes | Example |
| --- | --- | --- | --- |
| `help` | `usage` | Lists the live surface | `make help` |
| `setup` | (none) | Provision `.venv` + governed gitlinks; no `APPLY` gate | `make setup` |
| `deps` | `check` | `check` / `lock` / `upgrade`; mutators need `APPLY=Y` | `make deps WHAT=upgrade APPLY=Y PROJECT=flext-core` |
| `build` | `artifacts` | Build/package orchestration | `make build` |
| `check` | `all` | Read-only quality gates; optional `CHECK_GATES=` | `make check PROJECT=flext-infra CHECK_GATES=lint,format,pyrefly` |
| `test` | `all` | Default `--testmon` without coverage; `COV=Y` full coverage without testmon; `WHAT=cache-status|cache-clear|cache-checkpoint`; optional`FILE=` / `MATCH=` | `make test PROJECT=flext-infra` / `make test COV=Y PROJECT=flext-infra` |
| `fmt` | `check` | Format check/apply (`APPLY=Y` for mutate) | `make fmt WHAT=apply APPLY=Y` |
| `fix` | `check` | Auto-fix apply (`APPLY=Y`) | `make fix WHAT=apply APPLY=Y` |
| `run` | `default` | Run project entry | `make run` |
| `status` | `diagnostics` | Profile/attached/runtime + lock/pip checks | `make status` |
| `docs` | `all` | `all|generate|fix|audit|build|validate` | `make docs WHAT=audit` |
| `clean` | `generated` | Requires `APPLY=Y` | `make clean APPLY=Y` |
| `release` | `status` | Release status surface | `make release` |
| `gen` | `check` | Codegen conform; mutate with `WHAT=apply APPLY=Y` | `make gen WHAT=apply APPLY=Y` |
| `work` | `status` | Bead + GitFlow lane saga | `make work WHAT=start PROJECT=<member> BEAD=<id> KIND=bugfix NAME=<slug> APPLY=Y` |

Retired / not public: `val`, `codegen`, `format`, `boot`, `ship`, `coordination`, `makefile`, `DOCS_PHASE`, `CHANGED_ONLY`.

## `gen` (codegen SSOT)

Edit SSOT under `flext-infra/config/codegen.yaml` and
`flext-infra/src/flext_infra/templates/project/base/` (`Makefile.j2`,
`.github/workflows/*.j2`), then regenerate:

```bash
make gen WHAT=apply APPLY=Y
```

Contracts locked by `flext-infra` tests (`test_review_mro_vw2w_template_contracts.py`,
`test_codegen_ci_matrix.py`, `workflow_orphan_guard_tests.py`):

- Bootstrap pins `flext-infra` to the recorded gitlink OID when resolvable (`FLEXT_INFRA_BOOTSTRAP_REF`), else the integration branch
- `make deps WHAT=upgrade APPLY=Y PROJECT=...` modernizes via `SELECTED_PROJECTS` (honors `PROJECT`)
- CI failure artifacts upload only `junit.xml` / `coverage.xml` / `coverage.json` (no raw logs)
- TestPyPI release: root/tag verify → `make setup` → flext-core gitlink verify → publish
- `ci-matrix` projected only for `workspace-root` / `standalone`; never for `workspace-member`
- `ci-matrix` defaults to `workflow_dispatch` only; set `repository_policy_overlays.ci_matrix_auto_run: true` to also auto-run on push to `main` (no `pull_request`; never bind the integration-line variable)
- `make gen WHAT=apply APPLY=Y` prunes orphan member `.github/workflows/ci-matrix.yml` copies
- `codeql.yml` is not Jinja-projected (CodeQL default setup stays a GitHub repo setting)

## Integration line (operator gate)

Day-to-day land line is `0.12.0-dev`. Absorbing `main` into `0.12.0-dev` or promoting
`0.12.0-dev` into `main` is operator-gated (`custom.mk` workspace sync helpers) and
must not be treated as default land/finish closeout on 0.12.0-dev.

## `work` saga

On a workspace-root Makefile, when `PROJECT` names a `WORKSPACE_MEMBERS` entry and `WORKSPACE` is not a command-line override, `WORKSPACE` becomes `$(PROJECT_ROOT)/$(PROJECT)` so land/finish use the member git primary.

| WHAT | Mutates? | Description |
| --- | --- | --- |
| `start` | yes (`APPLY=Y`) | Branch `KIND/NAME`, registered worktree, bead metadata |
| `status` | no | Branch / worktree / head / PR for the bead |
| `land` | yes (`APPLY=Y`) | Sync registered lane to integration base, push head, open (or reuse open) PR; does not merge |
| `finish` | yes (`APPLY=Y`) | Close lane after merge |

Workers use the Gas Town CLI for the same lifecycle:

| Make verb | Gas Town CLI | Notes |
| --- | --- | --- |
| `make work WHAT=start` | `gt sling <bead> <rig>` | Dispatch + spawn polecat |
| `make work WHAT=status` | `gt hook` or `gt work` | Show hook status |
| `make work WHAT=land` | `gt done` | Submit to merge queue |
| `make work WHAT=finish` | `gt done` | Same — refinery closes lane after merge |

## Quick recipes

```bash
make setup
make check
make test PROJECT=flext-core
make gen WHAT=apply APPLY=Y
make work WHAT=land PROJECT=<member> BEAD=<id> APPLY=Y
```
