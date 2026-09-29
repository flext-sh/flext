---
title: Resumption contract
updated_at: 2026-09-25T17:27:00Z
---

# Resumption contract

<!-- TOC START -->

- [Read-only preflight](#read-only-preflight)
- [Exact continuation](#exact-continuation)

<!-- TOC END -->

Start from files and live repositories, never from a prior session cursor. The active
implementation checkout is:

```text
/home/marlonsc/fleet-closure-lanes/infra-convergence-20260925/flext-infra
```

Its branch is `fix/infra-green-convergence-20260925`; its open draft PR is
<https://github.com/flext-sh/flext-infra/pull/861> onto `0.12.0-dev`.

## Read-only preflight

Run these commands in order. Record working directory, exit code and decisive output.

```bash
cd /home/marlonsc/fleet-closure-lanes/infra-convergence-20260925/flext-infra
rtk git status --short --branch
rtk git rev-parse HEAD origin/0.12.0-dev
rtk gh pr view 861 --json url,state,isDraft,headRefOid,baseRefName,mergeStateStatus,statusCheckRollup

direnv exec /home/marlonsc/flext gc rig list --json
direnv exec /home/marlonsc/flext gc bd --city /home/marlonsc/gc show aihub-l42it --rig aihub --json
```

Expected freshness facts at handoff creation:

- lane HEAD `44b3381eaca295eeba280142572f62770a691381`;
- fetched integration `0f5d0cd7042caba1eca841e9678a2229606c0182`;
- PR head still points to `44b3381e...`, state `OPEN`, draft `true`, merge state
  `BEHIND`;
- Gas City root `/home/marlonsc/gc` is running while the `flext` and `aihub` rigs are
  suspended;
- the Beads read fails closed with `PROJECT IDENTITY MISMATCH`, local project ID
  `5e6a1521-55b4-4d51-9920-f683fa085f58`, served database project ID
  `a85fa192-f2e1-48f5-a62f-9d5947920786`.

Any changed SHA, PR state, worktree content, rig state or database identity invalidates
the corresponding fact and must be investigated before mutation. Do not run `bd init`,
set Beads endpoint variables, or create a substitute store.

## Exact continuation

The first repository command is:

```bash
cd /home/marlonsc/fleet-closure-lanes/infra-convergence-20260925/flext-infra
rtk make test
```

The preceding run was stopped intentionally with exit 130 while it still reported
`flext-cli: process still running`; it is not test evidence. Consume the new complete
report. If red, repair every failure at its canonical owner and rerun the full suite. If
green, run `rtk make build`, obtain independent review, commit explicit paths, push
fast-forward, integrate the current `origin/0.12.0-dev` with a no-ff merge, repeat the
full lifecycle, update PR 861, require green CI, merge, and prove the integrated SHA.

Do not begin the CLI or core phase before the `flext-infra` integrated SHA and its
post-merge gates are proven.
