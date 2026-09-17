# Configuration Standards

<!-- TOC START -->
- [Ownership](#ownership)
<<<<<<< HEAD
- [Config-owned facts](#config-owned-facts)
- [Validation](#validation)
<!-- TOC END -->

Configuration conventions for workspace documentation.

## Ownership

Typed `config/*.yaml` and settings own operational values, project-controlled behavior, and environment-tunable knobs. `pyproject.toml` owns package and tool metadata only. Generators derive managed surfaces from these owners.

## Config-owned facts

Facts consumed by documentation (project descriptions, versions, package names, URLs) come from canonical package metadata or typed config/settings. Docs-only policy exists only when it cannot be derived from a typed owner. Derived values are generated projections, never frozen literals.

## Validation

Run configuration propagation and validation from the workspace root:

```bash
make gen
make gen
make check
make test
```

The consecutive second generation pass must be a fixed point. Warnings, stale
projections, and missing tools are failures corrected at their owner.
=======
- [Runtime access](#runtime-access)
- [Generated surfaces](#generated-surfaces)
- [Validation](#validation)
<!-- TOC END -->

Configuration is executable architecture. Every fact has one typed owner and
every projection is derived from that owner.

## Ownership

- `config/workspace.yaml` owns workspace topology and member association.
- Package `config/*.yaml` files own package policy and business rules.
- `flext-infra/config/codegen.yaml` owns fleet generation and toolchain policy.
- `settings` owns environment and command inputs; `config` validates and derives
  package policy from declared sources.
- Schemas and Pydantic models validate boundaries. Constants do not become a
  second configurable-value store.

Tests, examples, and documentation read config-owned expectations through the
same typed public owner as production. They never freeze today's configured
value in a literal.

## Runtime access

Consumers use the package-root singletons only:

```python
from flext_core import config, settings
```

Access owned values as `settings.<Namespace>.*` and
`config.<Namespace>.*`; the namespace and field come from the package's typed
public contract.

Configuration modules remain below the facade graph and import no project
facade. Runtime code does not parse the same external payload twice or resolve
configuration through dictionaries, globals, reflection, or service locators.

## Generated surfaces

Managed `pyproject.toml` sections, Makefiles, CI, package roots, API reference,
and other stamped artifacts are projections. Change their config, schema,
template, or generator owner, then run the owning root Make verb. Never patch a
consumer projection to preserve drift.

Project-specific exceptions are typed overlays in the declared configuration;
they are not alternate templates or handwritten post-processing.

## Validation

Use the selector-free root lifecycle:

```bash
make setup
make gen
make check
make test
make build
```

Run `make gen` again after a generation change and require zero further file
effects. A missing command, warning, stale projection, or second-run mutation is
a defect at the owning configuration or generator.
>>>>>>> origin/0.12.0-dev
