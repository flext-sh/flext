# Using Pydantic in FLEXT

<!-- TOC START -->

- [Authority](#authority)
- [Where each Pydantic concern lives](#where-each-pydantic-concern-lives)
- [Library boundaries](#library-boundaries)
- [What consumers never do](#what-consumers-never-do)
- [Enforcement](#enforcement)
- [Static and runtime typing evidence](#static-and-runtime-typing-evidence)
  - [Analyzer rule review](#analyzer-rule-review)

<!-- TOC END -->

## Authority

The canonical, source-cited law is the `pydantic-development` skill
(`~/agents/skills/technology/pydantic-development/`, distributed to every agent home)
and the `rules/python/pydantic.md` rule. This guide maps that law onto the FLEXT
facades; it does not restate it. The Pydantic version in force is the one locked in
the committed `uv.lock` of the project that installs it; member locks and the
workspace lock that composes them agree by construction
([ADR-030](../architecture/adr/030-member-locks-composition-upg-guard.md)).

Two 2026-10-25 operator rulings bind every FLEXT model (root `AGENTS.md`
"Pydantic law"; ADR-028 Decisions 14 and 19):

- models import `u` only from the upstream FLEXT project or, in very restricted
  cases, from a private `_utilities` class of their own namespace; they export no
  methods, and the Pydantic surface they need lives in `_models/pydantic.py`
  (tracker memory `operator-ruling-2026-10-25-models-u-imports-pydantic-home`);
- entity equality is Pydantic value equality with explicit identity by id
  (tracker memory `operator-ruling-2026-10-25-entity-equality-pydantic-way`; see
  [Domain models](using-flext-core.md#domain-models)).

## Where each Pydantic concern lives

| Concern | FLEXT owner | Consumer form |
| --- | --- | --- |
| Model configuration | `m.*` presets in `flext-core/src/flext_core/_models/_base/` | `class X(m.FrozenModel)` — never a raw base or a hand-written `ConfigDict` |
| Reusable constraints, validators, serializers | `t` aliases (`type X = Annotated[...]`) | `field: t.NonEmptyStr` |
| Closed domains | `StrEnum` classes in `c` | `kind: c.Shipping.EventKind`; union tags `Literal[c.Shipping.EventKind.CREATED]` |
| Dependency-typed fields | `@runtime_checkable` protocols in `p` | `sink: t.Port[p.ShipmentSink]` (`InstanceOf`) |
| Model protocols | generated into `p` by flext-infra during `make gen` | never hand-mirrored |
| Non-model adapters | module-level adapters owned by `u` / `t` | never `TypeAdapter(...)` inside a function |
| Outcomes | `r` / `p.Result[T]`; the `e`/`u` result boundary converts `ValidationError` | `u.model.validate_value(Model, raw, from_json=True)` |
| Runtime knobs | `settings.<Namespace>.*` (pydantic-settings) | read through the singleton, never `os.environ` |
| Static rules | `config.<Namespace>.*` from `config/*.yaml` | read through the singleton |

Only flext-core imports `pydantic`, `pydantic_settings` or `pydantic_core`.

## Library boundaries

Every payload a library returns enters FLEXT as an `m` model at the single adapter
that calls the library, and every payload FLEXT hands to a library leaves through
`model_dump` / `model_dump_json` at that adapter:

- JSON: `Model.model_validate_json(raw)`.
- YAML/TOML: the loaded value goes straight into `Model.model_validate(...)` or a
  module-level adapter — no `cast`, no `isinstance` walk.
- pydantic-settings custom sources return the mapping its `_read_file` contract
  requires; the settings model validates it.
- structlog processors receive a mapping built from the validated record in one place.

## What consumers never do

Re-validate a model they already received, `isinstance`/`cast` owned data, convert
between dict and model by hand, compare closed domains with string literals, hold a
second model for a shape an existing model already expresses, or call
`model_rebuild`, `model_construct` or `model_copy(update=...)` on validated data.

## Enforcement

Each banned form has an ast-grep rule with fixtures in
`flext-infra/src/flext_infra/config/rules/ast-grep/rules/`. `make mod` applies the
rewrites, `make check` fails on any remaining finding, and tests exercise models only
through the public facades (no mocks, private access or tautologies).

## Static and runtime typing evidence

The approved investigation is `flext-itpd1.13.11`; analyzer environment ownership
is [ADR-003, Decision 5](../architecture/adr/003-workspace-tooling-hub-distribution.md#5-analyzers-use-the-environment-owned-by-the-checkout-topology).
The canonical `pydantic-development` procedure owns the diagnosis sequence.
Keep runtime validation and static constructor checking distinct: typed
constructors remain enabled, and external data enters through public validation.

Compare the real public facade with the upstream declaration before calling a
diagnostic a false positive. Record the checker version, loaded configuration,
resolved imports, inferred type and runtime result. Cover inherited and nested
models, generic specialization, defaults, aliases, validators, computed fields
and settings. A descriptor returning the original callable at runtime does not,
by itself, prove that a checker recognizes its field-specifier identity.

Pydantic documents that static constructor synthesis does not interpret
`default`, `default_factory` and `alias` inside `Annotated`. Keep constraints as
metadata and expose constructor-relevant declarations in a statically
recognized form, preserving runtime behavior. Multiple-base configuration
composition also needs observed runtime evidence; ordinary Python MRO is not a
substitute for inspecting the effective model configuration.

References: [Pydantic fields](https://docs.pydantic.dev/latest/concepts/fields/),
[configuration inheritance](https://docs.pydantic.dev/latest/concepts/config/),
and [dataclass transforms](https://typing.python.org/en/latest/spec/dataclasses.html).

### Analyzer rule review

The effective policy is read from Infra's native tooling declarations and the
selected checker's own strict-mode defaults. The following review groups the
diagnostics relevant to this investigation; it is not another configuration
catalog. No row authorizes a severity change.

| Rule family | What it establishes | Required diagnosis and disposition |
| --- | --- | --- |
| Missing imports and module sources | The analyzer can resolve a declaration | Verify interpreter, environment parent, editable origins and execution-environment order before investigating MRO |
| Missing third-party stubs | Availability of an external typing contract | Preserve the existing approved policy; source inference does not make every external API precise |
| Unknown types and untyped bases/decorators | Type information survived the boundary | Follow the first unknown symbol through its declaring export; retaining an overload at runtime does not prove static field/decorator identity |
| Constructor calls and argument types | Requiredness, aliases and declared input types | Compare required/default/factory/alias forms with actual validation; preserve typed constructors and public field semantics |
| Assignment, generic arguments and overrides | Substitution and mutability contracts | Inspect inherited specialization, variance and effective model configuration; a successful coercion is not proof of substitutability |
| Optional and unbound access | A value is present before use | Prove the public invariant and narrow at its owner; do not silence these checks because a model validates other fields |
| Unnecessary operations and unused declarations | Reachability and redundant/dead code | Inspect the inferred type first; fix lost precision before interpreting a cascade as redundant code |
| Mypy plugin diagnostics | Pydantic-specific field and model semantics | Keep the plugin and current two-code exception; assess each diagnostic against the native model and the public facade |

Relevant native options include mypy's import-following, package-base, re-export,
untyped-body, equality, reachability and unused-ignore checks, and Pyright's
strict inference and `reportUnknown*`, constructor, override and decorator
diagnostics. Their values remain owned by the selected configuration, not by
this review table. Lowering strictness can remove evidence without restoring
inference; it is not a causal repair.
