# ADR-005 — Config, settings, constants, templates, and schemas SSOT

- **Status:** Accepted (§2 amended by ADR-011)
- **Date:** 2026-07-11
- **Scope:** runtime configuration, declarative generation inputs, schemas,
  templates, and enforcement across FLEXT consumers. Enforcement follows the
  two laws in §6 (rules-as-data; rope-only static analysis).
- **Tracking:** `mro-wkii`, `mro-wkii.17`, `mro-7akn`
- **Implementation evidence:** Beads are authoritative for live delivery state;
  this ADR records the decision only.

<!-- mro-wkii.17.6 (agent: codex) — make config ownership and the conform pipeline unambiguous. -->

## Context

Configuration facts, generated file bodies, workspace topology, and validation
rules were duplicated across Python literals, templates, package metadata,
Makefiles, scripts, and repository-specific loaders. Duplicate owners prevent
deterministic generation and allow runtime behavior to diverge from declared
policy.

FLEXT requires a single typed path from declarative input to public facades and
generated artifacts, while preserving the runtime dependency direction
`flext-infra -> flext-cli -> flext-core`.

## Decision

### 1. Each concern has exactly one owner

| Concern | Canonical owner |
| --- | --- |
| invariants and scalar defaults | private constant modules exposed through `c` |
| execution parametrization and repository manifests | validated files under `config/` |
| environment-overridable runtime values | typed `settings.<Namespace>.*` models |
| generated bodies | `templates/*.j2` rendered only through `flext-cli` |
| validation contracts | matching `schemas/*.schema.json` files |

Large or derived structures are data-backed and generated; they are not
hardcoded as Python constant tables. `config` and `settings` are independent
typed objects. Consumption uses only:

```python
from package import config, settings

config.Namespace.domain
settings.Namespace.domain
```

Owned payloads cross boundaries as Pydantic v2 models, validated on input and
dumped on output. Raw mappings, untyped values, direct environment access in a
leaf module, and model-less configuration consumption are invalid. Settings and
config **data-path delivery** (cache/config/data/state/work directories) is
unified through `settings.py` using the namespaced XDG base-directory pattern
per ADR-011 §7; `config.py` resolves its config-file directory from
`settings.<Ns>.config_dir`, never from an independent CWD/package-relative resolver.

### 2. Facade and layer direction is strict

Within a package, runtime dependencies follow `c -> t -> p -> m -> u`. Forward
references (a higher-index layer importing a lower one) are runtime imports;
reverse references are forbidden entirely, not deferred under `TYPE_CHECKING`
(amended by ADR-011, Runtime-Forward Annotation Law). Every name used in a
runtime-evaluated annotation is a top-level runtime import. Fallible operations
return `r[T]`. Shared behavior is composed through the public facade and MRO,
with no loose helper or compatibility alias.

Across packages:

- `flext-core` provides runtime-minimal contracts and primitives and never
  imports the higher layers at runtime;
- `flext-cli` is the universal owner of CLI, process, file, output, config,
  schema, and template behavior;
- `flext-infra` consumes those public primitives for generation and
  enforcement, and owns ALL static enforcement rules as config data (§6).

Consumers use only `u.Cli.config_load`, `u.Cli.config_load_dir`,
`u.Cli.yaml_validate_schema`, and `u.Cli.render_template` for the corresponding
operations. Direct YAML, TOML, JSON Schema, Jinja2, Typer, or Click
implementations in `flext-infra` are invalid.

### 3. Repository conformance is data-driven

The typed repository catalog and each workspace manifest under `config/` are
the only topology inputs. `flext-infra codegen conform` maps them into typed
models including repository references, workspace specification, Make
specification, uv environment plan, conform request, codegen plan, and codegen
result.

Project creation and existing-project conformance call that same pipeline. The
pipeline supports only the three Make profiles defined by ADR-004 and uses one
schema and template layer. Specialized migration templates or repository-type
renderers are not allowed.

### 4. Rendering and application are deterministic transactions

Conformance performs these stages in order:

1. load config through `flext-cli`;
2. validate every selected input against its schema;
3. build and validate the complete typed plan;
4. render every selected artifact through `flext-cli`;
5. validate the complete rendered set;
6. compare managed-file provenance and block unrecognized edits;
7. write the complete selection only in apply mode.

Check mode never writes. Apply mode never writes a partial selection. Repeated
application of unchanged input is byte-idempotent and produces no diff.

### 5. Migration is deletion-first

Before adding a model, service, utility, command, template, or config file, the
implementer must identify the canonical existing owner and prove the functional
gap. Replaced loaders, renderers, generators, templates, commands, and wrappers
are removed with their callers in the same slice. Refactors target neutral or
negative net source lines and never retain a compatibility or fallback path.

## Consequences

- A declarative fact has one provenance and one validation contract.
- New and existing repositories with the same manifest converge to the same
  generated tree.
- Runtime consumers remain typed and independent of rendering dependencies.
- Configuration or managed-file drift fails before mutation.
- Static enforcement rules have one provenance (`flext-infra/config/*.yaml`)
  and one engine (rope-semantic fact base + closed operator set in `u.Infra`);
  no rule logic lives in Python and no `ast`/`get_ast` path exists (§6).
- `flext-core` carries runtime/beartype rules only; static rules cannot drift
  into the runtime layer.

## 6. Enforcement is declarative data over a rope-only engine

<!-- mro-wkii.4.8 (agent) — operator laws 2026-07-12; coordinate with mro-wkii.4 / mro-wkii.17.6. -->

**LAW1 — rules are data, never code.** 100% of static enforcement rules live ONLY
under `flext-infra/config/*.yaml` as Pydantic-2-validated records — zero rule
logic in Python. Bespoke per-rule detector classes and `ClassVar`
banned/allowlist rule tables are invalid. The rule models are PURE DATA: full
pydantic-2-way (`Field`/`Annotated`/discriminated unions/`computed_field`), with
custom `field_validator`/`model_validator` only as a last resort, and NO methods
of any kind. All behavior — the rope-semantic fact base and the closed operator
set that evaluates rules — lives in `u.Infra`/services, never on a model.
`flext-core` holds runtime/beartype rules only and is never the SSOT for a
static rule.

**LAW2 — static analysis is rope-semantic only.** Facts come only from rope's
semantic model (`get_scope`/`get_defined_names`/`get_attributes`/
`get_superclasses`/`PyName`). `import ast`, `ast.parse`, `ast.walk`,
`ast.Module`, and `PyModule.get_ast()`/`walk_ast_nodes` are BANNED in the static
path — `get_ast()` returns a stdlib `ast.Module`, which is AST. One shared
`rope_project` per run serves both detection and fix.

## 7. Workspace conformance owns broad refactors

<!-- mro-wkii.17.26 (agent: codex) — bind ADR-005 data ownership to the one-workspace transactional engine. -->

`flext-infra codegen conform` is the sole broad-write pipeline for generated
artifacts and structural migrations. In a declared workspace it opens one Rope
session at the manifest owner, indexes every active FLEXT member, builds facts
once per content hash, and evaluates config rules grouped by a closed operator
set. A project selector may narrow reporting or the final plan, but never opens
an incomplete project-local semantic universe. Project mode is valid only when
no workspace manifest or Git superproject contract exists.

Every accepted change is a typed planned change with an input fingerprint,
semantic owner, dependencies, expected diagnostics, and output hash. The
complete plan is rendered and tested in a temporary worktree before apply.
Writer collisions, stale fingerprints, new import cycles, changed public
reachability, patch-check failures, gate failures, or non-idempotence fail the
transaction before the live tree is changed.

Text and graph tools may supply candidate locations and blast-radius evidence.
They do not own rule data, fixes, or acceptance. Static rules remain YAML data;
new rule instances reuse the closed operators, while a genuinely new semantic
operator requires a versioned implementation change and its own tests.

## Verification contract

- Models prove Pydantic validation and dump round trips through public facades.
- Integration tests exercise public config, schema, template, and conform
  interfaces without mocking the unit under test.
- New-versus-existing equivalence compares complete generated trees byte for
  byte.
- A second apply produces an empty plan and check mode preserves all filesystem
  hashes.

## References

- [ADR-003 — Manifest-owned topology, root workspace, and autonomous Git
  libraries](./003-workspace-tooling-hub-distribution.md)
- [ADR-004 — Generated Make and codegen SSOT owned by `flext-infra`](./004-generic-make-framework-in-flext-tests.md)
- [ADR-007 — Operational kernel, universal CLI, and transactional conformance](./007-operational-kernel-cli-conform.md)
- [Migration plan](../config-ssot-migration-plan.md)
- Enforcement hardening beads: `mro-wkii.4`, `mro-wkii.4.1`, `mro-wkii.4.8`; plan
  `flext-infra/.omo/plans/declarative-enforcement.md`.
