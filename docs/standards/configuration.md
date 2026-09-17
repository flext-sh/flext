# Configuration Standards

<!-- TOC START -->
- [Ownership](#ownership)
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
