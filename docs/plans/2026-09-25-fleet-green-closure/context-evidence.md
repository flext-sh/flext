---
title: Measured context and evidence
updated_at: 2026-09-25T17:27:00Z
---

# Measured context and evidence

<!-- TOC START -->

- [flext-infra current slice](#flext-infra-current-slice)
- [Latest valid local gates](#latest-valid-local-gates)
- [Downstream lanes preserved](#downstream-lanes-preserved)
- [Handoff package lane](#handoff-package-lane)

<!-- TOC END -->

## `flext-infra` current slice

The working tree contains the uncommitted test-convergence slice on top of published
commit `44b3381eaca295eeba280142572f62770a691381`. Its substantive behavior is:

- test repositories now serialize a complete typed `m.Infra.WorkspaceManifestSpec`,
  including repository, project, ledger, integration and `members=()`; public discovery
  consumes it;
- the removed unlocked-toolchain `mise.lock` is no longer copied into fixtures;
- layout tests inject a validated layout context without exposing a Typer option;
- PEP 701 Rope occurrence discovery uses Python's tokenizer and preserves rename/scope
  behavior for nested quote and format-spec cases;
- import-facade discovery invalidates the relevant source index instead of retaining a
  stale external alias;
- CI matrix tests generate one immutable candidate and copy it for mutation/fixed-point
  assertions;
- the pytest runner derives the cold complete inventory from the already executed
  selection and emits a validated zero-execution cache-hit account without starting an
  empty duplicate suite. Warm and partial inventories still execute physically.

The previous complete full-suite report is:

```text
.reports/tests/20260925T155059.707431Z-2762651
inventory=3165 deselected=1818 executed=1347 reported=1347
passed=1126 failed=208 errors=13 warnings=0 skips=0 elapsed=1663.69s
```

Of its 221 red results, 184 were caused by fixtures copying the deliberately removed
`mise.lock`; the remainder covered real timeout duplication and contract mismatches. The
present batch targets all of them. Do not use the interrupted later run as proof.

## Latest valid local gates

All commands below ran in the active `flext-infra` lane:

| Command               | Exit | Decisive result                                                         |
| --------------------- | ---: | ----------------------------------------------------------------------- |
| `rtk make gen`        |    0 | conform and lazy-init completed                                         |
| second `rtk make gen` |    0 | repeated generation completed without a new publication                 |
| `rtk make mod`        |    0 | joint AST/semantic/text fixed point; 0 actionable findings              |
| `rtk make fix`        |    0 | 5/5 active stages; 0 failed, 0 skipped                                  |
| `rtk make fmt`        |    0 | 1062 files unchanged; markdown-format green                             |
| `rtk make check`      |    0 | 15/15 active stages green; Ruff, Pyrefly, Mypy and Pyright all 0 errors |
| `rtk make test`       |  130 | deliberately interrupted for handoff; invalid as acceptance evidence    |

Five configured recovery suspensions remain visible in `make check`: duplication,
codemod, boundary, namespace and runtime-census. Their authority is
`flext-itpd1.3 / operator 2026-09-24 / flext-xp6ec`; do not silently add, remove or
reinterpret them.

## Downstream lanes preserved

`flext-cli` lives at
`/home/marlonsc/fleet-closure-lanes/cli-atomic-interrupt-20260925/flext-cli`, branch
`fix/cli-atomic-interrupt-race-20260925`, HEAD and fetched integration
`c913c0aafda556b95c4c4b45c824c723b98cd2bd`. Its authored fix masks POSIX timer signals
while ownership of an authenticated temporary descriptor is transferred, then restores
the mask so the original interruption propagates after cleanup owns the state. The tree
also contains obsolete generated Mise surfaces from an earlier generator. Regenerate
through the integrated `flext-infra`; do not restore or preserve those old outputs
manually.

`flext-core` lives at `/home/marlonsc/fleet-closure-lanes/core-regen/flext-core`, branch
`fix/core-introspection-contract-20260925`, HEAD
`25738d509372a190f87b509cf6b1ef0af08414d4`, fetched integration
`c47ea7d7975b9c920ca4b1db4a5f7f0ac8b96cfb`. It contains the explicit-owner local alias
work plus generated and test changes. `.beads.gate.lock` is untracked execution residue
and must never be staged.

## Handoff package lane

This package was created in the dedicated superproject worktree
`/home/marlonsc/fleet-closure-lanes/session-handoff-20260925`, branch
`docs/fleet-green-session-handoff-20260925`, from the fetched `origin/0.12.0-dev`
baseline.

`rtk make setup` completed with exit 0 and initialized all declared submodules plus the
root physical environment. The following `rtk make fmt` validated the root project and
the six new Markdown files with 56 files unchanged and `markdown-format` at 0 errors,
then exited 2 when workspace orchestration entered `flext-api`: the member lacked
`.venv/bin/python`. Subsequent members reported the same ownership defect. This is not a
green fleet receipt and must not be described as one. Do not create member environments
with direct `uv`; the pending `flext-infra` producer and generated Make lifecycle own
the repair. Publish this documentation only after that canonical owner is integrated or
the native setup/fmt lifecycle itself is fixed and revalidated.
