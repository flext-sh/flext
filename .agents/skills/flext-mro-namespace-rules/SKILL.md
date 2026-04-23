---
name: flext-mro-namespace-rules
description: Canonical MRO namespace rules for facade naming, organic nested-domain access, and same-project import boundaries. Use when editing `constants.py`, `models.py`, `protocols.py`, `typings.py`, `utilities.py`, `tests/`, or any `models/` and `_utilities/` mixin tree.

---

# Flext MRO Namespace Rules

**Reviewed**: 2026-04-20 | **Scope**: Canonical naming, organic namespace access, cross-facade import boundaries, cross-project c/p/t/m/u slot registry

## Scope

- `flext-*/src/**/constants.py`
- `flext-*/src/**/models.py`
- `flext-*/src/**/protocols.py`
- `flext-*/src/**/typings.py`
- `flext-*/src/**/utilities.py`
- `flext-*/tests/`
- `flext-*/examples/`
- `flext-*/scripts/`
- Private facade mixin trees under `_constants/`, `models/`, `_protocols/`, `_typings/`, `_utilities/`

## References

- `AGENTS.md`
- `flext-infra/src/flext_infra/utilities.py` — root facade composing many `_utilities/*` mixins into `class Infra`
- `flext-tests/src/flext_tests/constants.py` — canonical `src/` facade with a single local root namespace `class Tests`
- `flext-core/tests/base.py` — already follows the `TestsFlext*` naming prefix
- `flext-core/tests/models.py` — legacy `TestsFlextCoreModels` naming that must not be copied into new work
- `.agents/skills/flext-import-rules/SKILL.md`
- `.agents/skills/flext-patterns/SKILL.md`

## Rules

- `src/` facades MUST use `Flext<Project><Tier>`.
- `tests/` facades MUST use `TestsFlext<Project><Tier>`. Legacy `Flext<Project>Test<Tier>` and `FlextTest<Project><Tier>` names are migration debt only.
- `examples/` facades MUST use `ExamplesFlext<Project><Tier>`. Legacy `{Flext<Project>}Examples<Tier>` names are migration debt only.
- `scripts/` facades MUST use `ScriptsFlext<Project><Tier>`. Legacy `{Flext<Project>}Scripts<Tier>` names are migration debt only.
- A public facade root defines exactly one local domain namespace:
  - `src/`: `class <Domain>:`
  - `tests/`: `class <Domain>:` containing `class Tests:`
- Callers MUST keep the organic namespace path emitted by MRO. Use `u.Infra.parse_semver`, `c.Tests.ERR_OK_FAILED`, and `m.TargetOracle.ExecuteResult`. Do not flatten nested domain-local classes back onto the facade root with assignments like `ExecuteResult = TargetOracle.ExecuteResult`.
- Examples and docs should present Pydantic-facing usage through `c`, `p`, `t`, `m`, `u` (and `s` for services), preserving nested classes + MRO composition even in service-only snippets.
- Contract ownership follows the facade split: `p.*` for protocols, `t.*` for composed aliases, `m.*` for models. Do not recreate protocol-shaped aliases in `t` or flatten model/protocol carriers just to shorten an annotation.
- Private mixin files under `models/`, `_utilities/`, `_protocols/`, and similar trees define mixin classes only. The public facade composes them in its inheritance list. Manual flat wrapper nesting such as `class Docker(tk): pass` inside the facade namespace is forbidden.
- Same-project cross-facade imports are forbidden at runtime unless explicitly allowed below:
  - `typings.py` may reference same-project `p` and `m` only under `TYPE_CHECKING`.
  - `protocols.py` may reference same-project `t` and `m` only under `TYPE_CHECKING`.
  - `models.py` may reference same-project `t` and `p` only under `TYPE_CHECKING`.
  - `constants.py` may import same-project runtime symbols when genuinely required.
  - `utilities.py`, `models/*`, and `_utilities/*` may import private classes directly across private modules to resolve cycles, but must not hop through sibling public facades.
  - `flext-core` `FlextRuntime` is the only standing exception to the no same-project facade-import rule.
- Non-canonical short aliases such as `tf`, `tm`, and `td` are forbidden in new work. Fix consumers instead of adding compatibility wrappers.

## Cross-Project Slot Registry

Each project owns specific nested namespaces under `c / p / t / m / u`. A slot is owned by EXACTLY ONE project; overlap is forbidden. To add a new slot, file a workspace RFC and update this table before any code change.

| Project | `c.*` | `p.*` | `t.*` | `m.*` | `u.*` |
| --- | --- | --- | --- | --- | --- |
| flext-core | (base) — `Errors`, `Encoding`, `HttpStatus`, `Severity`, etc. | (base) — `Result`, `Registry`, `Container`, `Dispatcher`, `Logger`, `HasDomainEvents` | (base) — `Scalar`, `Container`, `Primitives`, `JsonMapping`, `JsonValue`, ... | (base) — `BaseModel`, `Value`, `Entity`, `AggregateRoot`, `DomainEvent`, `ConfigMap` | (base) — `Collection`, `Domain`, `Pydantic`, `Runtime` |
| flext-cli | `c.Cli` — `ENCODING_DEFAULT`, `YAML_*`, `JSON_*`, exit codes | `p.Cli` — command, option, result | `t.Cli` — `JsonMapping`, `YamlDict`, adapters | `m.Cli` — command result models | `u.Cli` — `json_*`, `yaml_*`, `toml_*` |
| flext-tests | `c.Tests` — `ERR_OK_FAILED`, fixture paths, golden-file roots | `p.Tests` — matcher, fixture, golden | `t.Tests` — `Testobject`, matcher inputs | `m.Tests` — test record models | `u.Tests` — `tm.*` matchers, builders, factories |
| flext-infra | `c.Infra` — `Encoding`, `SourceCode.*`, transformers | `p.Infra` — rule, scanner, transformer | `t.Infra` — `ChangeCallback`, `StrIndex` | `m.Infra` — scan report models | `u.Infra` — `atomic_write_file`, `parse_semver` |
| flext-auth | `c.Auth` — token kinds, scopes, default lifetimes | `p.Auth` — Token, AuthResponse, Provider | `t.Auth` — token payloads | `m.Auth` — auth records | `u.Auth` — token normalization |
| flext-web | `c.Web` — HTTP method set, status codes | `p.Web` — FastApiLikeApp, FlaskLikeApp, Repository, Handler | `t.Web` — `EndpointPayload`, request body aliases | `m.Web` — request/response models | `u.Web` — request normalization |
| flext-api | `c.Api` — error codes, openapi tags | `p.Api` — handler, middleware, client | `t.Api` — request/response aliases | `m.Api` — DTO models | `u.Api` — serialization helpers |
| flext-ldap | `c.Ldap` — object classes, attribute SSOT | `p.Ldap` — connection, entry, search | `t.Ldap` — filter expressions | `m.Ldap` — entry models | `u.Ldap` — filter builders |
| flext-ldif | `c.Ldif` — RFC magic strings | `p.Ldif` — parser, writer | `t.Ldif` — line types | `m.Ldif` — entry/record models | `u.Ldif` — stream encoders |
| flext-dbt-ldap | `c.DbtLdap` — `Attributes`, `ObjectClasses`, `Timestamps` StrEnums | `p.DbtLdap` — run, macro, source | `t.DbtLdap` — macro inputs | `m.DbtLdap` — run-result models | `u.DbtLdap` — jinja helpers |
| flext-dbt-ldif | `c.DbtLdif` | `p.DbtLdif` | `t.DbtLdif` | `m.DbtLdif` | `u.DbtLdif` |
| flext-dbt-oracle | `c.DbtOracle` | `p.DbtOracle` | `t.DbtOracle` | `m.DbtOracle` | `u.DbtOracle` |
| flext-tap-oracle / flext-tap-oracle-oic / flext-tap-oracle-wms | `c.TapOracle*` | `p.TapOracle*` | `t.TapOracle*` | `m.TapOracle*` | `u.TapOracle*` |
| flext-target-oracle / flext-target-oracle-wms / flext-target-ldap / flext-target-ldif | `c.Target*` | `p.Target*` | `t.Target*` | `m.Target*` | `u.Target*` |
| flext-meltano | `c.Meltano` | `p.Meltano` | `t.Meltano` | `m.Meltano` | `u.Meltano` |
| flext-quality | `c.Quality` | `p.Quality` | `t.Quality` | `m.Quality` | `u.Quality` |
| flext-plugin | `c.Plugin` | `p.Plugin` | `t.Plugin` | `m.Plugin` | `u.Plugin` |
| flext-observability | `c.Observability` | `p.Observability` | `t.Observability` | `m.Observability` | `u.Observability` |
| flext-db-oracle | `c.DbOracle` | `p.DbOracle` | `t.DbOracle` | `m.DbOracle` | `u.DbOracle` |
| flext-grpc | `c.Grpc` | `p.Grpc` | `t.Grpc` | `m.Grpc` — `Generic.ValidationSummary`, `Generic.ValidationResults` | `u.Grpc` |
| flext-oracle-wms | `c.OracleWms` | `p.OracleWms` | `t.OracleWms` | `m.OracleWms` | `u.OracleWms` |

**Conflict Resolution Rule**: a slot is owned by exactly one project. Duplicate ownership requires a new namespace name. If two projects need the same domain concept (e.g. both Tap and Target need "Stream"), the concept lives in `flext-meltano` (parent) and both consume it via MRO.

## Instructions

- Inspect both the public facade file and the private mixin tree it composes before changing namespace structure.
- Keep inheritance exhaustive at the public facade root; every concern-specific private mixin should appear in the MRO once.
- When a consumer wants a shorter annotation, prefer a canonical `p.*` or `t.*` contract over adding facade-root alias assignments that flatten a nested symbol.
- Prefer direct private class imports over sibling facade imports when resolving cycles inside the same project.
- When you find a legacy test facade name, rename the class and propagate consumers in the same change.
- Keep `__init__.py` exports autogenerated; fix generators or facade names, then run `make gen`.

## Workflow

1. Identify the public facade and its single local namespace root.
2. Purge flat nested wrapper classes that only restate a private mixin.
3. Rename legacy test facades to `TestsFlext<Project><Tier>` and update consumers.
4. Remove illegal same-project facade imports and replace them with `TYPE_CHECKING` or direct private-class imports.
5. Re-run targeted linters and, when touching tests, the affected `pytest` scope.

## Examples

### Good: Pydantic models consumed via `m` facade with nested domains

```python
from __future__ import annotations

from typing import Annotated

from flext_core import m, p, r, t


class FlextTargetOracleModels(m):
    """Consumer facade: inherits flext_core m via MRO, adds one local namespace."""

    class TargetOracle:
        """One local namespace for project-specific domain models."""

        class ExecuteResult(m.ArbitraryTypesModel):
            """Result of an Oracle batch execute operation."""

            model_config = m.ConfigDict(frozen=True, strict=True)

            rows_affected: Annotated[
                t.NonNegativeInt,
                m.Field(description="Number of rows modified"),
            ]
            table_name: Annotated[
                t.NonEmptyStr,
                m.Field(description="Target Oracle table"),
            ]


def execute_batch(
    table: str,
) -> p.Result[FlextTargetOracleModels.TargetOracle.ExecuteResult]:
    """Canonical access: via the full nested namespace — no flat aliases."""
    result = FlextTargetOracleModels.TargetOracle.ExecuteResult(
        rows_affected=0,
        table_name=table,
    )
    return r[FlextTargetOracleModels.TargetOracle.ExecuteResult].ok(result)
```

Why good:

- **Facade-only imports** — `from flext_core import m, p, r, t` (never `from pydantic import ...`). Pydantic constructs flow through `m.*`/`u.*` via MRO.
- **Organic nesting preserved** — callers use `FlextTargetOracleModels.TargetOracle.ExecuteResult`, no flat alias assignment
- **MRO chains Pydantic** — the class inherits `m.ArbitraryTypesModel`, exposing `m.Field`/`m.ConfigDict` through the workspace facade
- **Frozen + strict boundary contract** on every public model
- **Clear domain boundaries** — each namespace owns its own models/validators/state

Bad:

```python
from __future__ import annotations

from flext_core import m


class _StubMixin(m):
    """Placeholder representing a cross-project mixin import."""


class _StubUtilities(m):
    """Placeholder representing a cross-project utilities import."""


class FlextTargetOracleModels(_StubMixin):
    class TargetOracle:
        class ExecuteResult(m.ArbitraryTypesModel):
            name: str

    # BAD: flattens domain-local symbol back to facade root
    ExecuteResult = TargetOracle.ExecuteResult


class TestsFlextCoreUtilities(_StubMixin, _StubUtilities):
    class Core:
        class Tests:
            # BAD: manually nests private mixin instead of composing through MRO
            class Docker(_StubMixin):
                pass
```

Why bad: flattens a domain-local symbol back to the facade root and manually nests a private mixin instead of composing it through the facade MRO.

## Verification

- `rg -n "class (Flext[A-Za-z]+Test|FlextTest[A-Za-z]+)(Constants|Models|Protocols|Types|Utilities)" flext-*/tests || true`
- `rg -n "class Flext[A-Za-z]+(Examples|Scripts)(Constants|Models|Protocols|Types|Utilities)" flext-*/examples flext-*/scripts || true`
- `rg -n "^[[:space:]]+[A-Z][A-Za-z0-9_]+ = [A-Z][A-Za-z0-9_]+\\.[A-Z]" flext-*/*/src flext-*/tests || true`
- `rg -n "if TYPE_CHECKING:" flext-*/*/src/flext_*/*.py flext-*/*/tests/*.py || true`
- `make val VALIDATE_SCOPE=workspace`
