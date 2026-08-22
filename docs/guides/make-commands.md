# FLEXT Make command surface

<!-- TOC START -->
- [Conventions](#conventions)
- [Public verbs](#public-verbs)
- [Gas Town lane lifecycle](#gas-town-lane-lifecycle)
- [Generation owner](#generation-owner)
- [Integration line](#integration-line)
- [Quick recipes](#quick-recipes)
<!-- TOC END -->

Canonical reference for the workspace Make control plane on `0.12.0-dev`.
Discover live verbs with `make help`. Do not invent retired verbs.

## Conventions

- Format: `make <verb> [WHAT=<action>] [PROJECT=<member>] [APPLY=Y]`.
- Discovery: `make help`.
- Mutating actions require `APPLY=Y` when declared by the live surface.
- Omit `PROJECT` and `PROJECTS` only when fleet fan-out is intended.

## Public verbs

The canonical generated surface contains `help`, `setup`, `deps`, `build`,
`check`, `test`, `fmt`, `fix`, `run`, `status`, `clean`, `release`, `gen`, and
`mod`. The exact WHAT selectors come from `make help`.

The lane lifecycle is not a Make concern. The former Make lane verb is retired.

## Gas Town lane lifecycle

The repository is the Gas Town rig `flext`.

```bash
gt sling <bead> flext
gt hook status
gt convoy status <convoy-id>
# Choose one completion path:
gt done
gt handoff <bead>
```

See the [worker lane contract](../ways-of-working/worker-lane-contract.md).

## Generation owner

Edit the owning configuration and templates in `flext-infra`, then run the
generated fixed point:

```bash
make gen WHAT=apply APPLY=Y
```

Generated Makefiles, workflows, hooks, and project guidance are projections.
Do not edit them as independent owners.

## Integration line

Day-to-day work lands on `0.12.0-dev` through Gas Town and Refinery. Promotion
to `main` is a separate operator-authorized release action with repository
policy and required checks satisfied.

## Quick recipes

```bash
make setup
make check CHECK_GATES=markdown
make test FILE=<changed-test-file>
make gen WHAT=apply APPLY=Y
```
