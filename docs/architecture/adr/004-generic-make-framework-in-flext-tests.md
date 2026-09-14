# ADR-004 — Generated Make and codegen SSOT owned by `flext-infra`

<!-- TOC START -->
- [Context](#context)
- [Decision](#decision)
  - [1. `flext-infra codegen conform` is the sole owner](#1-flext-infra-codegen-conform-is-the-sole-owner)
  - [2. The Makefile is a self-contained generated artifact](#2-the-makefile-is-a-self-contained-generated-artifact)
  - [3. `custom.mk` is a narrow private extension surface](#3-custommk-is-a-narrow-private-extension-surface)
  - [4. Conformance is deterministic and fail-closed](#4-conformance-is-deterministic-and-fail-closed)
- [Consequences](#consequences)
- [Verification contract](#verification-contract)
- [References](#references)
<!-- TOC END -->
- **Status:** Accepted (replaces the former Make registry decision)
- **Date:** 2026-06-28
- **Amended:** 2026-09-14 (selector-free command catalog; supersedes the fixed
  verb count and WHAT routing described by the earlier decision)
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

### 2. The Makefile is a self-contained generated artifact

One template layer emits the complete versioned Makefile for the
`workspace` or `standalone` profile. Make never
regenerates itself and never includes a shared implementation from another
checkout. `make gen` performs conformance explicitly. Each public verb performs
its declared operation directly, without an effect selector.

The public verb catalog and handler mappings are owned by
`flext-infra/config/codegen.yaml`; the complete Makefile is rendered by
`flext-infra/src/flext_infra/templates/project/base/Makefile.j2`. Discover the
current surface through root `make help`, rather than a second list in this ADR.
Each operation has one canonical handler. Public aliases, duplicate dispatchers,
and caller-provided action selectors are invalid.

### 3. `custom.mk` is a narrow private extension surface

A versioned `custom.mk` may contain only the private extensions accepted by the
canonical Make owner. It cannot own help, toolchain provisioning, public command
routing, or generated-target definitions. Project-specific behavior follows the
owner's declared extension contract; it does not introduce public selectors or
a competing dispatcher.

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
- Public-surface discovery agrees with the owner catalog and resolves one
  canonical handler per declared verb.

## References

- [ADR-003 — Manifest-owned topology, root workspace, and autonomous Git
  libraries](./003-workspace-tooling-hub-distribution.md)
- [ADR-005 — Config, settings, constants, templates, and schemas
  SSOT](./005-config-settings-constants-templates-schemas-ssot.md)
