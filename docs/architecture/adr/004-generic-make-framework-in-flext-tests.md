# ADR-004 — Generated Make and codegen SSOT owned by `flext-infra`

<!-- TOC START -->

- [Context](#context)
- [Decision](#decision)
  - [1. flext-infra codegen conform is the sole owner](#1-flext-infra-codegen-conform-is-the-sole-owner)
  - [2. The Makefile is a self-contained generated artifact](#2-the-makefile-is-a-self-contained-generated-artifact)
  - [3. custom.mk is a narrow private extension surface](#3-custommk-is-a-narrow-private-extension-surface)
  - [4. Conformance is deterministic and fail-closed](#4-conformance-is-deterministic-and-fail-closed)
- [Consequences](#consequences)
- [Verification contract](#verification-contract)
- [References](#references)

<!-- TOC END -->

- **Status:** Accepted (replaces the former Make registry decision)
- **Date:** 2026-06-28
- **Amended:** 2026-07-11
- **Scope:** generated Makefiles, repository conformance, command routing, and
  custom project handlers.
- **Tracking:** `mro-wkii.17`

<!-- mro-wkii.17.6 (agent: codex) — replace competing Make owners with the single conform pipeline. -->

## Context

The workspace accumulated generated and handwritten Make surfaces, a testing
library command registry, external includes, script dispatchers, bootstrap
generators, and repository-specific migration paths. Several public targets
performed the same action, while generated files could regenerate themselves
during normal Make execution.

Those paths cannot be made deterministic by coordination alone. A generated
contract needs one declarative input, one validated renderer, and one public
handler for each action.

## Decision

### 1. `flext-infra codegen conform` is the sole owner

The only repository conformance interface is:

```text
flext-infra codegen conform --root <path> --scope self|members|all --mode check|apply
```

`flext-infra` owns typed planning, profile selection, policy enforcement, and
the write transaction. `flext-cli` owns the universal config, schema, template,
file, process, and output primitives consumed by the pipeline. `flext-core`
remains runtime-minimal. The dependency direction is always:

```text
flext-infra -> flext-cli -> flext-core
```

Project creation writes only the initial manifest and invokes `conform`.
Existing and new projects use the same models, schemas, context, renderer, and
templates. There is no separate migration, bootstrap, workspace, or legacy
rendering path.

> **Note:** the file name retains the historical suffix `in-flext-tests`; the
> content has been repointed — `flext-infra` owns the Make/codegen SSOT for the
> entire fleet (root workspace + members + standalone), not only flext-tests.

### 2. The Makefile is a self-contained generated artifact

One template layer emits the complete versioned Makefile for the
`workspace` or `standalone` profile from `flext-infra/src/flext_infra/templates/project/base/Makefile.j2`.
Make never regenerates itself and never includes a shared implementation from
another checkout. `codegen` performs conformance explicitly; `check` is read-only
and `apply` requires.

> **Selector-free (since 2026-09-14).** Verbs are selector-free; mutation is
> the verb default (see root AGENTS.md operator law 2026-09-14). The `WHAT=`
> selector contract described below is retired.

The public surface is discovered from the live root `Makefile` with `make help`.
At this revision it exposes these selector-free operational verbs:

```text
setup deps build check test fmt fix fix-enforcement audit status docs
clean release-plan release-version release-tag release-build publication
gen initialize mod waza duplication
```

`help` only describes the surface. Every operation maps to exactly one public
verb and one canonical handler. Public aliases, duplicate verbs, daemon targets,
and alternative dispatch routes are invalid.

The meanings are fixed (from the root `Makefile` `_builtin-help`):

| Verb              | Responsibility                                                 |
| ----------------- | -------------------------------------------------------------- |
| `setup`           | provision the pinned toolchain and environment                 |
| `deps`            | upgrade, lock, and conform every declared dependency           |
| `build`           | build the project distribution artifacts                       |
| `check`           | run static and policy gates                                    |
| `test`            | execute real behavior tests through the testmon cache          |
| `fmt`             | apply ruff format + lint autofix                               |
| `fix`             | apply ruff check + all configured safe corrections             |
| `fix-enforcement` | apply the safe fix actions declared by the enforcement catalog |
| `audit`           | inspect ownership, dependency, and generated-state health      |
| `status`          | report the resolved runtime and repository state               |
| `docs`            | generate, repair, build, and validate documentation            |
| `clean`           | remove every declared disposable artifact                      |
| `release-plan`    | resolve the release decision through the public protocol       |
| `release-version` | materialize the planned version                                |
| `release-tag`     | tag the verified release commit                                |
| `release-build`   | build the release receipt and artifacts                        |
| `publication`     | publish only receipt-attested release artifacts                |
| `gen`             | regenerate every managed projection atomically                 |
| `initialize`      | materialize the declared package initializer graph             |
| `mod`             | apply the declared structural codemods                         |
| `waza`            | validate provider-neutral governance semantics with Waza       |
| `duplication`     | run the canonical jscpd duplicate-code gate                    |

### 3. `custom.mk` is a narrow private extension surface

A versioned `custom.mk` may contain only private handlers admitted by the typed
custom-handler policy. Its schema rejects public targets, aliases, help or
toolchain ownership, setup logic, generated-target redefinition, and handlers
whose verb is outside the canonical surface.

The public surface is `help` plus the operational verbs above and accepts no
`WHAT` selector. The current template still contains internal
`_custom_<verb>_<what>` dispatch residue; Bead `flext-5fxu6.4.22` owns its
removal. That residue is not an accepted public contract.

### 4. Conformance is deterministic and fail-closed

The pipeline loads and validates the complete selected manifest, builds the
complete typed plan, renders every selected output, and validates the rendered
set before any write. Unrecognized edits in a managed file abort the apply.
There is no partial write, rollback path, compatibility mode, or coexistence of
old and new generated surfaces.

The same declarative input must produce byte-identical output. A second apply
has an empty plan and a new project must converge to the same generated tree as
an existing project with the same manifest.

## Consequences

- `flext-tests` tests public behavior but owns no Make registry or dispatcher.
- Repository-local scripts may implement private handlers but cannot redefine
  routing or generation.
- Replaced generators, templates, dispatchers, and public targets are deleted
  in the same migration slice.
- CI invokes the same canonical verbs and cannot suppress a failing result.

## Verification contract

- Parse and `help` validation cover every generated profile.
- Schema tests reject public custom targets and handler collisions.
- Conformance check performs no writes; apply is atomic and idempotent.
- Public-surface discovery reports only `help` and the twenty-three operational
  verbs, with one handler per verb.

## References

- [ADR-003 — Manifest-owned topology, root workspace, and autonomous Git
  libraries](./003-workspace-tooling-hub-distribution.md)
- [ADR-005 — Config, settings, constants, templates, and schemas
  SSOT](./005-config-settings-constants-templates-schemas-ssot.md)
