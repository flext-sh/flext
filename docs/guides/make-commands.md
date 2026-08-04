# FLEXT Make command surface

Canonical reference for the workspace Make control plane on `0.12.0-dev`.
Discover live verbs with `make help` only. Do not invent retired verbs.

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
| `test` | `all` | Pytest via Make; optional `FILE=` / `MATCH=` | `make test PROJECT=flext-infra FILE=tests/unit/...` |
| `fmt` | `check` | Format check/apply (`APPLY=Y` for mutate) | `make fmt WHAT=apply APPLY=Y` |
| `fix` | `check` | Auto-fix apply (`APPLY=Y`) | `make fix WHAT=apply APPLY=Y` |
| `run` | `default` | Run project entry | `make run` |
| `status` | `diagnostics` | Profile/attached/runtime + lock/pip checks | `make status` |
| `docs` | `all` | `all|generate|fix|audit|build|validate` | `make docs WHAT=audit` |
| `clean` | `generated` | Requires `APPLY=Y` | `make clean APPLY=Y` |
| `release` | `status` | Release status surface | `make release` |
| `gen` | `check` | Codegen conform; mutate with `WHAT=apply APPLY=Y` | `make gen WHAT=apply APPLY=Y` |
| `work` | `status` | Bead + GitFlow lane saga | `make work WHAT=start BEAD=<id> KIND=bugfix NAME=<slug> APPLY=Y` |

Retired / not public: `val`, `codegen`, `format`, `boot`, `ship`, `coordination`, `makefile`, `DOCS_PHASE`, `CHANGED_ONLY`.

## `gen` (codegen SSOT)

Edit SSOT under `flext-infra/config/codegen.yaml` and
`flext-infra/src/flext_infra/templates/project/base/` (`Makefile.j2`,
`.github/workflows/*.j2`), then regenerate:

```bash
make gen WHAT=apply APPLY=Y
```

Contracts locked by `flext-infra` tests (`test_review_mro_vw2w_template_contracts.py`):

- Bootstrap pins `flext-infra` to the recorded gitlink OID when resolvable (`FLEXT_INFRA_BOOTSTRAP_REF`), else the integration branch
- `make deps WHAT=upgrade APPLY=Y PROJECT=...` modernizes via `SELECTED_PROJECTS` (honors `PROJECT`)
- CI failure artifacts upload only `junit.xml` / `coverage.xml` / `coverage.json` (no raw logs)
- TestPyPI release: root/tag verify → `make setup` → flext-core gitlink verify → publish

## Integration line (operator gate)

Day-to-day land line is `0.12.0-dev`. Absorbing `main` into `0.12.0-dev` or promoting
`0.12.0-dev` into `main` is operator-gated (`custom.mk` workspace sync helpers) and
must not be treated as default ULW closeout.

## `work` saga

| WHAT | Mutates? | Description |
| --- | --- | --- |
| `start` | yes (`APPLY=Y`) | Branch `KIND/NAME`, registered worktree, bead metadata |
| `status` | no | Branch / worktree / head / PR for the bead |
| `land` | yes (`APPLY=Y`) | Open/update PR into the integration base |
| `finish` | yes (`APPLY=Y`) | Close lane after merge |

## Quick recipes

```bash
make setup
make check
make test PROJECT=flext-core
make gen WHAT=apply APPLY=Y
make work WHAT=land BEAD=<id> APPLY=Y
```
