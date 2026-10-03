# Configuration Standards

<!-- TOC START -->

- [Ownership](#ownership)
- [Config-owned facts](#config-owned-facts)
- [Runtime access](#runtime-access)
- [Generated surfaces](#generated-surfaces)
- [Validation](#validation)

<!-- TOC END -->

Configuration is executable architecture. Every fact has one typed owner and every
projection is derived from that owner.

Typed `config/*.yaml` and settings own operational values, project-controlled behavior
and environment-tunable knobs. Package metadata is not a second store for those values;
generators derive managed metadata and other projections.

## Ownership

- `config/workspace.yaml` owns workspace topology and member association.
- Package `config/*.yaml` files own package policy and business rules.
- `flext-infra/config/codegen.yaml` owns fleet generation and toolchain policy.
- `flext-infra/config/tooling.yaml` owns tool configuration and policy, not a separate
  toolchain version catalog.
- `settings` owns environment and command inputs; `config` validates and derives package
  policy from declared sources.
- Schemas and Pydantic models validate boundaries. Constants do not become a second
  configurable-value store.

Tests, examples, and documentation read config-owned expectations through the same typed
public owner as production. They never freeze today's configured value in a literal.

## Config-owned facts

Facts consumed by documentation (project descriptions, versions, package names, URLs)
come from canonical package metadata or typed config/settings. Docs-only policy exists
only when it cannot be derived from a typed owner. Derived values are generated
projections, never frozen literals. See
[ADR-005](../architecture/adr/005-config-settings-constants-templates-schemas-ssot.md)
for ownership and boundary contracts.

## Runtime access

Consumers use the package-root singletons only:

```python

```

Access owned values as `settings.<Namespace>.*` and `config.<Namespace>.*`; the
namespace and field come from the package's typed public contract.

Configuration modules remain below the facade graph and import no project facade.
Runtime code does not parse the same external payload twice or resolve configuration
through dictionaries, globals, reflection, or service locators.

## Generated surfaces

Managed `pyproject.toml` sections, Makefiles, CI, package roots, API reference, and
other stamped artifacts are projections. Change their config, schema, template, or
generator owner, then run the owning root Make verb. Never patch a consumer projection
to preserve drift.

Project-specific policy uses typed overlays in the declared configuration, not alternate
templates or handwritten post-processing. An overlay cannot authorize hiding a defect or
weakening a required gate.

## Validation

Use the selector-free root lifecycle:

```bash
make setup
make gen
make mod
make gen
make gen
make fix
make fmt
make check
make test
make build
```

Follow with the applicable public runtime and native documentation/link validation.
Require repeated `make gen`, `make fix` and `make fmt` to produce zero further effects
and exit zero on the unchanged candidate. Later mutations invalidate affected receipts.
A missing command or tool, warning, stale projection or second-run mutation is a defect
at its canonical owner.

This standard records requirements, not runtime results. Fleet stability needs complete
evidence on published integrated SHAs before another cycle begins. Beads records
execution state; it is not runtime authority. Local/private plans remain session
context, not publication sources or substitutes for the typed owner and real consumer
evidence.
