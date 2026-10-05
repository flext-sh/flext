# FLEXT dbt LDIF

<!-- TOC START -->

- [Status & health](#status-health)
  - [Quality signals](#quality-signals)
- [Quick start](#quick-start)
- [Architecture & modules](#architecture-modules)
  - [Key architectural patterns](#key-architectural-patterns)
- [Testing & quality](#testing-quality)
- [Resources](#resources)
- [Support & issues](#support-issues)

<!-- TOC END -->

FLEXT dbt LDIF is the integration project that turns LDIF directory exports into
analytics-ready dbt models. It composes `flext-ldif` (LDIF parsing), `flext-meltano`
(dbt orchestration), and `flext-core` (result contracts, settings SSOT) behind one MRO
facade that parses LDIF files, generates dbt model metadata, runs transformation
workflows, and assesses data quality.

## Status & health

- **Version**: `0.12.0-dev` (active development cycle)
- **Python**: 3.13+
- **Project class**: integration
- **Dependencies**: `flext-core`, `flext-ldif`, `flext-meltano`, `pydantic`

### Quality signals

- All operations return `r[T]` (`p.Result[...]`) with typed payload models under
  `m.DbtLdif.*`.
- Settings are validated Pydantic models (`FlextDbtLdifSettings`); configuration is
  consumed only through the settings SSOT.
- Selector-free root `make check`, `make test`, and `make build` produce the
  authoritative evidence.

## Quick start

From the workspace root, run `make setup`, `make check`, and `make test`.

```python
from flext_dbt_ldif import FlextDbtLdif, settings

api = FlextDbtLdif(settings=settings)

source = settings.DbtLdif.ldif_file_path
workflow = api.process_ldif_file(
    source,
    generate_models=True,
    run_transformations=False,
).unwrap()
quality = api.validate_ldif_quality(source).unwrap()
print(workflow.model_dump(mode="json"), quality.model_dump(mode="json"))
```

Provide an existing LDIF export through typed settings and a writable configured
dbt output project before execution. This performs real model generation and
quality assessment without running transformations or hiding failures.

Focused entry points on the same facade:
`generate_ldif_models(ldif_file, overwrite=False)` (model metadata generation only) and
`validate_ldif_quality(ldif_file)` (quality assessment workflow).

## Architecture & modules

The package follows the canonical FLEXT layout under `src/flext_dbt_ldif/`:

- `api.py` — `FlextDbtLdif` (also exported as `dbt_ldif`), the MRO facade composed from
  the four service mixins below; `fetch_instance()` returns the shared instance.
- `services/client.py` — `FlextDbtLdifClient`: LDIF file parsing via `flext-ldif`.
- `services/core.py` — `FlextDbtLdifCore`: core domain behavior shared by the workflows.
- `services/service.py` — `FlextDbtLdifServiceMixin`: the bound workflow `Service`
  (`generate_and_write_models`, `run_complete_workflow`, `run_data_quality_assessment`).
- `services/unified_service.py` — `FlextDbtLdifUnifiedService`: unified orchestration
  surface.
- `base.py` — service base (`s`) over `flext-meltano`'s dbt service base.
- `_settings.py` / `config/` — settings SSOT (`FlextDbtLdifSettings`), consumed as
  `from flext_dbt_ldif import settings`.
- `constants.py`, `models.py`, `typings.py`, `protocols.py`, `utilities.py` —
  `c/m/t/p/u` facet declarations and behavior.

### Key architectural patterns

- **MRO composition**: the facade carries no wrapper methods; every operation is
  provided directly by a service mixin.
- **Typed workflow results**: `m.DbtLdif.ModelGenerationResult`,
  `m.DbtLdif.WorkflowResult`, and `m.DbtLdif.ParseValidationResult` are the only payload
  shapes crossing the API.
- **Zero direct dbt/LDIF imports**: parsing goes through `flext-ldif`; dbt execution
  goes through `flext-meltano`.
- **Validated boundaries**: parsed LDIF entries are validated through typed adapters
  before model generation, and invalid payloads fail with `r.fail(...)` context.

## Testing & quality

- Tests live in the project `tests/` tree and run through root `make test`.
- Workflow tests use synthetic LDIF fixtures; dbt execution paths need a configured dbt
  target.
- The authoritative quality verdict comes from root `make check`, `make test`, and
  `make build`.

## Resources

- [Project README](https://github.com/flext-sh/flext-dbt-ldif/blob/0.12.0-dev/README.md)
  (auto-generated module map and integration pointers)
- [Workspace AGENTS.md](https://github.com/flext-sh/flext/blob/0.12.0-dev/AGENTS.md) —
  FLEXT engineering law
- Generated API overview: `flext-dbt-ldif/docs/api-reference/generated/overview.md`
- Related projects: `flext-core`, `flext-ldif`, `flext-meltano`, `flext-tap-ldif`,
  `flext-target-ldif`, `flext-dbt-ldap`

## Support & issues

- Issues and discussions: <https://github.com/flext-sh/flext> (monorepo)
- Before contributing, read the workspace `AGENTS.md` and run root `make check`.
