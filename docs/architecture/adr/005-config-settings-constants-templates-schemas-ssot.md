# ADR-005 — Config, settings, constants, templates, and schemas SSOT

<!-- TOC START -->

- [Context](#context)
- [Decision](#decision)
  - [1. Each concern has exactly one owner](#1-each-concern-has-exactly-one-owner)
  - [2. Facade and layer direction is strict](#2-facade-and-layer-direction-is-strict)
  - [3. Repository conformance is data-driven](#3-repository-conformance-is-data-driven)
  - [4. Rendering and application are deterministic transactions](#4-rendering-and-application-are-deterministic-transactions)
  - [5. Migration is deletion-first](#5-migration-is-deletion-first)
- [6. Enforcement is declarative data over a rope-semantic engine](#6-enforcement-is-declarative-data-over-a-rope-semantic-engine)
- [Consequences](#consequences)
- [Verification contract](#verification-contract)
- [References](#references)
- [0.13 unified planning reconciliation (documentation only)](#013-unified-planning-reconciliation-documentation-only)

<!-- TOC END -->

- **Status:** Accepted
- **Implementation status:** CURRENT IMPLEMENTATION (§§1–5); ACCEPTED TARGET (§6
  enforcement migration to rope-semantic). The 2026-10-28 collection and
  transaction amendments are accepted contracts pending implementation and
  runtime proof; the earlier status label does not attest those amendments.
- **Date:** 2026-07-11
- **Scope:** runtime configuration, declarative generation inputs, schemas, templates,
  and enforcement across FLEXT consumers. §§1–5 are CURRENT IMPLEMENTATION; §6 is
  ACCEPTED TARGET (enforcement migration from mixed rope/ast to rope-semantic).
- **Tracking:** `mro-wkii`, `mro-wkii.17`

<!-- mro-wkii.17.6 (agent: codex) — make config ownership and the conform pipeline unambiguous. -->

## Context

Configuration facts, generated file bodies, workspace topology, and validation rules
were duplicated across Python literals, templates, package metadata, Makefiles, scripts,
and repository-specific loaders. Duplicate owners prevent deterministic generation and
allow runtime behavior to diverge from declared policy.

FLEXT requires a single typed path from declarative input to public facades and
generated artifacts, while preserving the runtime dependency direction
`flext-infra -> flext-cli -> flext-core`.

## Decision

### 1. Each concern has exactly one owner

| Concern                                                                   | Canonical owner                                    |
| ------------------------------------------------------------------------- | -------------------------------------------------- |
| immutable invariants                                                      | private constant modules exposed through `c`       |
| configurable policy/defaults, generation inputs, and repository manifests | validated files under `config/`                    |
| environment-overridable runtime values                                    | typed `settings.<Namespace>.*` models              |
| reusable type aliases and constrained annotations                        | the owning `t.<Namespace>` family                  |
| structural capabilities and dependency ports                             | the owning `p.<Namespace>` family                  |
| data, model presets and native Pydantic invariants                        | the owning `m.<Namespace>` family                  |
| algorithms and adapters                                                  | the owning `u.<Namespace>` family                  |
| generated bodies                                                          | `templates/*.j2` rendered only through `flext-cli` |
| Python payload validation contracts                                      | their declaring Pydantic models or type adapters   |
| separately declared document grammars                                    | their owning `schemas/*.schema.json` files         |

Large or derived structures are data-backed and generated; they are not hardcoded as
Python constant tables. `config` and `settings` are independent typed objects.
Consumption imports the public owners and reads their declared fields. This
self-contained example uses the CLI package's typed identity configuration and
inherited runtime debug setting, without copying their current values:

```python
from flext_cli import config, settings

print(config.Cli.name, config.Cli.version, settings.debug)
```

Owned payloads cross boundaries as Pydantic v2 models, validated on input and dumped on
output. Unvalidated raw mappings, untyped values, direct environment access in a
leaf module, and model-less configuration consumption are invalid.

**Amendment 2026-10-28 — Pydantic domain and ingress contract.** A complete
closed string domain is declared by its existing `StrEnum` owner and referenced
by that type; a `Literal` is retained for a proper subset or discriminator.
Strict Python producers pass enum members and typed nested values. Raw JSON
is validated once through the existing JSON boundary; field relaxation,
validation retries and serialization round-trips cannot repair a producer's
wrong input type. The latest operator revision supersedes the earlier
`use_enum_values=True`/primitive-protocol contract with `use_enum_values=False`
throughout governed model presets. `strict=True` controls Python input validation;
the enum option preserves validated members rather than making validation strict
by itself. Preserve the effective strictness of each existing preset; this
revision does not silently turn every settings source or external adapter into
a strict Python constructor.

Model attributes and Python dumps retain enum members. Generated protocols name
the actual enum for reading and, where mutable, writing; frozen fields expose
only reads. Serialize primitive values at the outward JSON boundary with native
serialization. Preserve native JSON ingress semantics, validated defaults and
factories. Pass already validated models by reference and remove redundant
readmission introduced solely for the superseded primitive-storage policy after
proving its replacement. Enum singleton identity is distinct from model equality.
Compose existing presets, nested/generic models, adapters
and schema hooks before adding custom machinery. Pydantic configuration
inheritance is verified on the effective model, not inferred from Python C3
MRO: upstream explicitly documents that multiple-base configuration currently
does not follow it. See [the usage guide](../../guides/using-pydantic.md),
[upstream configuration](https://docs.pydantic.dev/latest/concepts/config/) and
[complete upstream reference](https://pydantic.dev/docs/validation/latest/llms-full.txt).
This records the accepted operator contract; it does not attest fleet migration
or runtime acceptance.

The source-derived payload projection and its concrete schema delegation belong
to [ADR-018](018-generator-declarations.md#model-and-service-protocol-projection).
An injected runtime dependency instead follows
[ADR-019](019-service-contract-ports-operations.md): `t.Port[p.X]` is a FLEXT
annotation built on native Pydantic hooks, not a replacement payload schema.
An unresolved port type parameter fails at its declaring owner; it never
selects an unconstrained schema.

### Domain boundaries and value flow (amended 2026-10-28)

The model declares the shape and invariants of a value; its data source determines
whether the instance is configuration, settings or an operational payload. A
Pydantic model is not another configuration source. Do not copy a reviewed rule
into a field default, a constant and an environment setting. Select its single
owner by who may change it: reviewed policy belongs to `config`, runtime inputs
to `settings`, and stable published vocabularies and invariants to `c`.

Presets own model policy, including enum preservation, once. Their existing
bootstrap-safe constants are schema-contract invariants, not per-deployment
knobs. Reusable constrained annotations belong to `t`, structural consumption
contracts to `p`, payloads and native validators/serializers to `m`, algorithms
and adapters to `u`, and operation orchestration to services. A model validator
enforces its data invariant; it does not read files, discover dependencies or
perform network calls. Reuse native constraints before adding a custom validator.

The composition root selects validated policy and runtime settings and injects
the required values and `p` capabilities into services. Services receive a
validated request, call their injected capabilities and domain utilities, and
return a typed result. They do not serialize and reconstruct the same model to
cross an internal boundary. External input is validated once at its actual
ingress; a changed representation or domain transition is a new explicit
boundary with its own consumed contract, not an implicit global conversion.

**Textual ingress decision (operator selected 2026-10-28).** YAML/environment
tokens and strict Python domain values are different representations. The
operator selected native textual decoding at the existing entry owner: Pydantic
materializes the document's types before the strict domain contract consumes
them. The same owner retains source identity, enum domains, aliases, defaults
and error provenance. Do not add per-field `strict=False`, consumer-side enum
constructors, a YAML-to-JSON round trip, another parser or a catch/default route.
This source grammar is not permission to relax ordinary Python constructors;
its implementation requires public native-ingress and negative-domain proof.

Parsed document values remain JSON-compatible. Elected operational metadata
such as a catalog's owner root is validated separately and travels through the
typed Pydantic validation context; it is not inserted as a Python object into
the document mapping. The declaration owner binds that metadata through native
validation before effects. A document cannot select its own operational origin,
and ordinary Python/JSON construction retains its declared input contract.

A package adds only its own namespace and inherits upstream same-letter facades.
It neither renames upstream domains nor folds a sibling namespace into its own.
Cross-domain dependencies consume the declaring facade or an authored minimal
port. Configuration and settings retain their separate layer-zero owners and
singleton lifecycles; domain payloads are ordinary values, not singletons.
Layer-zero initialization cannot read an unfinished own composite facade.

Python C3 composes classes, method lookup and cooperative `super()`; Pydantic
merges model configuration and validates fields under its own native rules.
Inspect the effective fields, configuration, validators and specialization rather
than assuming that one mechanism proves the others. Use inheritance for a real
contract extension, nested model fields for containment, and injected protocols
for collaboration. Facade namespace classes never become payload model bases.
Frozen models are not recursively immutable, and assignment validation does not
observe mutations inside a list or dictionary. Choose collection and ownership
semantics according to the domain instead of claiming stronger guarantees.

The [Pydantic guide](../../guides/using-pydantic.md) owns usage examples and the
native capability selection checklist. The accepted target is not a statement
that current presets, generators or all consumers already implement it.

**Amendment 2026-10-28 — accepted contract, implementation pending.** An
extensible catalog is a validated sequence of domain records or a mapping
from validated identity keys to those records, declared once by its existing
typed owner. Adding or changing valid entries and values propagates through
that collection without a property, protocol member, helper or orchestrator
branch for every entry. Preserve each record's domain DTO and strict field
validation; this does not permit `dict[str, Any]`, arbitrary attribute access,
untyped payload transport or a parallel registry. Configuration/settings
values retain their existing source ownership, singleton identity and layer
precedence. A genuinely new semantic capability still requires an explicit
contract and implementation at its existing owner; an unknown behavior is
rejected rather than synthesized from data.

### 2. Facade and layer direction is strict

Within a package, runtime dependencies follow `c -> t -> p -> m -> u`; reverse
references are type-checking-only. Fallible operations return `r[T]`. Shared behavior is
composed through the public facade and MRO, with no loose helper or compatibility alias.

Preserve generated lazy exports through `__init__.py`. Model annotations resolve at
their declaring owner through runtime-safe imports. Eager-export rewrites, compatibility
aliases, and `model_rebuild` are not import-cycle repairs.

Constant-family initialization may reuse a value from its pure declaring leaf,
but cannot read the composite `c` facade while that facade is being assembled.
Such bootstrap dependencies use the explicit leaf producer; importing the facade
back into its own parts or substituting an empty/default value is not a repair.

Layer-zero `_config`/`_settings` and their source helpers may import an identity-proven
helper of the same package within layer zero, when the complete proposed
source/import graph is acyclic. The operator's recorded
`operator-ruling-2026-10-08-settings-config-boundary` also permits the canonical
private-family `base.py` as a foundational leaf: its native source identity must
belong to the candidate and it must import no other module of its own package,
including settings/config. This exception does not admit a composite family
facade or another family member. A filename alone does not prove this contract.
Each schema has one owner and reads values from its
declared configuration source; helpers do not copy business rules or depend on a
project `c/t/p/m/u` facade, even under `TYPE_CHECKING`. Helper admission
distinguishes that project's facades from an
authenticated upstream foundation: Core's model facade remains the SDK owner of
Pydantic declarations in other projects.
Both the native import-law validator and its generated declarative rule consume
this same typed decision;
neither a filename prefix nor a package-specific allowlist proves helper ownership.
Analysis of these dependencies resolves source modules and bindings through Rope;
it never imports or executes the package being analyzed.
This is the layer-zero boundary applied by [ADR-028 Decision 1](028-facade-boundary-orchestrators-declarative-enforcement.md#decision-1).

Generated facade imports, declaration references and codemod contexts preserve the
complete package identity elected by the project-discovery owner, including nested
namespace packages. A directory basename is not an import identity. An unresolved
native class remains an error; adding an initializer or accepting an unknown Rope
object is not a substitute for resolving its actual declaring module.

2026-10-23 reconciliation (`algar-723.1.3`): source inspection found basename-derived
imports in facade generation for nested namespaces. The source repair reuses the
existing discovery owner; successful consumer generation and regression evidence are
still required before claiming implementation acceptance.

2026-10-24 open contract (`algar-723.1.3.3`): initial Python capture uses the Git
source-scope owner, while workspace indexing uses declared project discovery.
Their suffix, ignore, hidden-directory and nonparticipant rules are not proven
equivalent. Filtering one inventory by the other does not authenticate absence
and is not an accepted migration. Selecting one authority, preserving private
exclusions and adding its authenticated native route require explicit
adjudication; no scope change is authorized by a timing failure.

Across packages:

- `flext-core` provides runtime-minimal contracts and primitives and never imports the
  higher layers at runtime;
- `flext-cli` is the universal owner of CLI, process, file, output, config, schema, and
  template behavior;
- `flext-infra` consumes those public primitives for generation and enforcement, and
  owns ALL static enforcement rules as config data (§6).

Consumers use only `u.Cli.config_load`, `u.Cli.config_load_dir`,
`u.Cli.yaml_validate_schema`, and `u.Cli.render_template` for the corresponding
operations. Direct YAML, TOML, JSON Schema, Jinja2, Typer, or Click implementations in
`flext-infra` are invalid.

### 3. Repository conformance is data-driven

The parent's `.gitmodules` owns composition (ADR-024); each repository's own
declarations own only its genuine deltas. Conformance maps them into typed models,
including
repository references, workspace specification, Make specification, uv environment plan,
conform request, codegen plan, and codegen result.

The approved `flext-0029c` target projects that composition into native uv workspace
declarations and one root lock shared with root CI. Suppliers use native pyproject
sources; environment-based supplier selection, persisted selection and synthetic
resolver graphs are retired. Mise and uv own interpretation, resolution and
installation of their native inputs, not a second Python or AWK/shell parser.
Native source declarations and lock consistency replace the stronger independent
pre-install supplier admission; installed provenance and authenticated-import
checks remain distinct post-provision concerns. These target boundaries require
their own cutover and runtime evidence, not a documentation-only acceptance claim.

Project creation and existing-project conformance call that same pipeline. The pipeline
supports only the workspace and standalone Make profiles defined by ADR-004 and uses
one schema and template layer. Specialized migration templates or repository-type
renderers are not allowed.

2026-10-23 reconciliation: the typed `MakeProfile` owner declares these two profiles;
governance kind and package/workspace roles are separate facts, not a third profile.

### 4. Rendering and application are deterministic transactions

Conformance performs these stages in order:

1. load config through `flext-cli`;
2. validate every selected input against its schema;
3. build and validate the complete typed plan;
4. render every selected artifact through `flext-cli`;
5. validate the complete rendered set;
6. compare managed-file provenance and block unrecognized edits;
7. write the complete selection only in apply mode.

Check mode never writes. Repeated application of unchanged input is
byte-idempotent and produces no diff.

**Amendment 2026-10-28 — accepted contract, implementation pending.**
[ADR-018's small-transaction contract](018-generator-declarations.md#single-read-single-batch-publication-amended-2026-10-28-campaign-flext-pipol)
defines the publication unit, cooperative-reader visibility, interruption
record and guarded reversal of owned effects. The complete dependency closure
of a transaction is admitted together; this is not invocation-wide physical
atomicity across files. Completed independent transactions remain intact
when a later transaction fails, and the containing operation remains failed.

File mutation uses the existing FilePlan/publication/journal owner and CLI atomic-I/O
primitives. Compare both content and mode for CAS; never add a parallel writer or weaken
recovery checks to make generation pass.

### 5. Migration is deletion-first

Before adding a model, service, utility, command, template, or config file, the
implementer must identify the canonical existing owner and prove the functional gap.
Replaced loaders, renderers, generators, templates, commands, and wrappers are removed
with their callers in the same slice. Refactors target neutral or negative net source
lines and never retain a compatibility or fallback path.

## 6. Enforcement is declarative data over a rope-semantic engine

<!-- mro-wkii.4.8 (agent) — operator laws 2026-07-12; coordinate with mro-wkii.4 / mro-wkii.17.6. -->

**Status: ACCEPTED TARGET — CURRENT IMPLEMENTATION uses a mixed rope/ast engine.**

Rope-semantic enforcement is the accepted target state. In the current tree, static
enforcement uses a mix of rope semantic primitives and Python `ast` in the detection
path; migration to rope-only is in progress and tracked by beads `mro-wkii.4`,
`mro-wkii.4.1`, `mro-wkii.4.8`.

**LAW1 — rules are data, never code.**

- **CURRENT IMPLEMENTATION:** `flext-infra/config/infra.yaml` owns the typed enforcement
  catalog, while specialized Python detectors and embedded rule logic still exist during
  migration. Their presence is tracked debt, not a second approved authority.
- **ACCEPTED TARGET:** 100% of static enforcement rules live only under the typed config
  owner as Pydantic-2-validated records. Bespoke per-rule detector classes and
  `ClassVar` banned/allowlist tables are removed. Rule models remain pure data; the
  shared fact base and closed operator set live in `u.Infra`/services. `flext-core` owns
  runtime/beartype rules only and never becomes the SSOT for static policy.

**LAW2 — static analysis targets rope-semantic only.**

- **CURRENT IMPLEMENTATION:** Enforcement detectors use a mix of rope semantic model
  (`get_scope`/`get_defined_names`/`get_attributes`/`get_superclasses`/ `PyName`) and
  Python `ast` in some paths. For example,
  `flext-infra/src/flext_infra/validate/namespace_validator.py` uses
  `pymodule.get_ast()` and `ast.parse()`/`ast.walk()` for namespace validation;
  `flext-infra/src/flext_infra/_utilities/_rope_analysis/exports.py` uses `ast.parse()`
  for source-based export-name resolution. The flext-infra `AGENTS.md` acknowledges
  this: "Enforcement target is rope-semantic (ADR-005); some detectors still use AST —
  verify before claiming AST is banned."
- **ACCEPTED TARGET:** Facts come ONLY from rope's semantic model
  (`get_scope`/`get_defined_names`/`get_attributes`/`get_superclasses`/`PyName`).
  `import ast`, `ast.parse`, `ast.walk`, `ast.Module`, and
  `PyModule.get_ast()`/`walk_ast_nodes` are deprecated in the static enforcement path
  and will be exterminated as detectors migrate to rope primitives. One shared
  `rope_project` per run serves both detection and fix.

## Consequences

- A declarative fact has one provenance and one validation contract.
- New and existing repositories with the same manifest converge to the same generated
  tree.
- Runtime consumers remain typed and independent of rendering dependencies.
- Configuration or managed-file drift fails before mutation.
- Static enforcement converges on one provenance (`flext-infra/config/infra.yaml`) and
  one rope-semantic engine; specialized Python/ast detectors remain migration debt until
  §6 lands.
- `flext-core` carries runtime/beartype rules only; static rules cannot drift into the
  runtime layer.

## Verification contract

- Models prove Pydantic validation and dump round trips through public facades.
- Integration tests exercise public config, schema, template, and conform interfaces
  without mocking the unit under test.
- New-versus-existing equivalence compares complete generated trees byte for byte.
- A second apply produces an empty plan and check mode preserves all filesystem hashes.
- Alternative valid scalar values and collection entries propagate through the
  same typed public contracts without per-entry Python declarations. Invalid
  records and unknown semantic capabilities fail at origin. Tests derive
  configuration-owned expectations from that same validated owner.

## References

- [ADR-003 — Manifest-owned topology, root workspace, and autonomous Git libraries](./003-workspace-tooling-hub-distribution.md)
- [ADR-004 — Generated Make and codegen SSOT owned by `flext-infra`](./004-generated-make-codegen-ssot-flext-infra.md)
- [Migration plan](../config-ssot-migration-plan.md)
- Enforcement hardening beads: `mro-wkii.4`, `mro-wkii.4.1`, `mro-wkii.4.8`; plan
  `flext-infra/.omo/plans/declarative-enforcement.md`.

## 0.13 unified planning reconciliation (documentation only)

- Disposition for the unified 0.13 plan: Correct direction, bootstrap, topology and tool
  roles; lazy imports do not make reverse dependencies lawful.
- This note records planning reconciliation only. It does not change the ADR's recorded
  maturity, implementation status, or acceptance evidence.
- Future 0.13 API/ecosystem migration remains gated by `flext-ik359` (publication
  `flext-1wjg1` plus separate authorization) and approval of the documented contracts
  and consumer migration matrix. Current 0.12 validation, bug fixes and documentation
  continue under their owners; the ADR's proposal/status is unchanged.
