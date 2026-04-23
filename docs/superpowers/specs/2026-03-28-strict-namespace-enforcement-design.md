# Strict c/t/p/m/u Namespace Enforcement — Design Spec

**Date**: 2026-03-28
**Scope**: ALL 34 projects — zero exceptions, zero loose classes, zero MRO gaps
**Authority**: AGENTS.md §2.2, §2.3, §2.4, §3.1, §3.4, §4, §9.1

---

## 1. Problem Statement

301 loose classes across 31 projects violate AGENTS.md §2.3: "Loose module-level objects or functions outside the namespace class are STRICTLY FORBIDDEN." Additionally, 9 MRO gaps exist where `_models/` or `_utilities/` subclasses are not wired into their facade's MRO chain.

## 2. Rules (Non-Negotiable)

### 2.1 Absorption Rule

Every class in `src/` MUST exist inside a namespace facade or be an MRO base of one. No class may exist standalone at module level unless it meets an explicit exception (§2.5).

| Class type                               | Target facade                                   | Access pattern              |
| ---------------------------------------- | ----------------------------------------------- | --------------------------- |
| Pydantic models, value objects, entities | `m.{Project}.*`                                 | `m.Api.Client`              |
| Constants, enums, literals               | `c.{Project}.*`                                 | `c.Grpc.ErrorCode`          |
| Type aliases                             | `t.{Project}.*`                                 | `t.Api.ResponseType`        |
| Protocols, ABCs                          | `p.{Project}.*`                                 | `p.Auth.Provider`           |
| Utilities, helpers, stateless functions  | `u.{Project}.*`                                 | `u.Api.Serializer`          |
| Exception hierarchies                    | `e.{Project}.*` or `m.{Project}.Exceptions.*`   | Standalone `e` file OK      |
| Services (s subclasses)                  | `u.{Project}.*` inner class                     | `u.DbtLdif.UnifiedService`  |
| Clients                                  | `u.{Project}.*` inner class                     | `u.TargetLdap.Client`       |
| Streams, Sinks                           | `m.{Project}.Streams.*` / `m.{Project}.Sinks.*` | `m.TargetLdap.Sinks.Writer` |
| Adapters, Middleware                     | `u.{Project}.*` inner class                     | `u.Api.Middleware`          |
| Decorators                               | `d.{Project}.*` or absorb into `u`              | Project-specific            |

### 2.2 MRO Completeness Rule

Every class in a `_models/`, `_utilities/`, `_constants/`, `_protocols/`, `_typings/` subdirectory MUST appear in the corresponding facade's inner namespace MRO bases. No orphan subclasses.

### 2.3 Same-Type Import Rule

A facade file NEVER imports its own-type alias from any package:

- `constants.py` → never `from pkg import c`
- `models.py` → never `from pkg import m`
- Same for u, p, t

### 2.4 Propagation Rule

Every rename/move uses `sg` (ast-grep) for IMMEDIATE workspace-wide propagation. No manual find-and-replace.

### 2.5 Exceptions (Exhaustive List — Nothing Else)

| File pattern                                                                 | Reason                                               | Rule                                   |
| ---------------------------------------------------------------------------- | ---------------------------------------------------- | -------------------------------------- |
| `settings.py`                                                                | Generic param `s[T]`                                 | Standalone OK                          |
| `__main__.py`                                                                | Entry point                                          | Standalone OK                          |
| `__version__.py`                                                             | Metadata                                             | Standalone OK                          |
| `__init__.py`                                                                | Auto-generated exports                               | Never manual edit                      |
| `lazy.py` (flext-core only)                                                  | PEP 562 infrastructure consumed by all `__init__.py` | Standalone OK                          |
| MRO base classes of facades                                                  | Python MRO requires base before child                | Standalone OK, must have alias         |
| `_models/`, `_utilities/`, `_constants/`, `_protocols/`, `_typings/` subdirs | These ARE the MRO composition                        | Must be wired into facade MRO          |
| `services/` subdir (if classes inherit from `s` subclass base)               | Scoped service implementations                       | Must be wired into facade `api.py` MRO |
| `providers/` subdir (flext-auth)                                             | Auth provider implementations                        | Must be registered, OK standalone      |
| `protocol_impls/` subdir (flext-api)                                         | Protocol implementations                             | Must be registered, OK standalone      |
| `servers/` subdir (flext-ldif)                                               | Server quirk implementations                         | Must be registered, OK standalone      |
| `domain/` subdir                                                             | Domain entity re-exports                             | Must reference facade `m.*`            |

### 2.6 flext-core Foundation Classes

These classes are MRO bases of the namespace facade chain. Python requires them to be defined before their children. They CANNOT be absorbed as inner classes.

**Already aliased (conformant):**

| Class | File            | Alias | Status |
| ----- | --------------- | ----- | ------ |
| `d`   | `decorators.py` | `d`   | ✅      |
| `e`   | `exceptions.py` | `e`   | ✅      |
| `h`   | `handlers.py`   | `h`   | ✅      |
| `r`   | `result.py`     | `r`   | ✅      |
| `s`   | `service.py`    | `s`   | ✅      |
| `x`   | `mixins.py`     | `x`   | ✅      |

**Unaliased infrastructure (must fix):**

| Class             | File            | Business Role                                                  | Fix                                                                                                                                                         |
| ----------------- | --------------- | -------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `FlextContainer`  | `container.py`  | DI container singleton (base of `x` container access)          | Keep standalone — MRO base. Already exported as `FlextContainer` from `__init__.py`. No absorption needed — it IS the DI infrastructure, accessed directly. |
| `FlextContext`    | `context.py`    | Request-scoped context (inherits `m.ArbitraryTypesModel`, `u`) | Keep standalone — MRO peer of `x`. Already exported.                                                                                                        |
| `FlextDispatcher` | `dispatcher.py` | CQRS message bus (used by `h`, `s`, `FlextRegistry`)           | Keep standalone — MRO peer. Already exported.                                                                                                               |
| `FlextLogger`     | `loggings.py`   | Structured logger (inherits `u`, `p.Logger`)                   | Keep standalone — MRO peer. Already exported.                                                                                                               |
| `FlextRegistry`   | `registry.py`   | Handler registry (inherits `s[bool]`)                          | Keep standalone — `s` subclass. Already exported.                                                                                                           |
| `u`               | `runtime.py`    | L0.5 bridge (BASE of `FlextUtilities`)                         | Keep standalone — MRO base of `u`. Already exported.                                                                                                        |

**Must absorb into facades:**

| Class              | File        | Target                                            | Reason                                              |
| ------------------ | ----------- | ------------------------------------------------- | --------------------------------------------------- |
| `FlextError`       | `errors.py` | `m.Error` (inner class of `FlextModels`)          | Pydantic BaseModel value object — belongs in models |
| `FlextErrorDomain` | `errors.py` | `c.ErrorDomain` (inner class of `FlextConstants`) | StrEnum — belongs in constants                      |

## 3. MRO Gaps to Fix

| #   | Project                 | Facade         | Missing base                                                                  | File                                                   |
| --- | ----------------------- | -------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------ |
| 1   | flext-api               | `typings.py`   | `FlextApiTypes` inherits `FlextTypes` — should inherit `FlextWebTypes`        | `flext-api/src/flext_api/typings.py`                   |
| 2   | flext-ldif              | `models.py`    | `FlextLdifModelsBases` not in `Ldif` MRO                                      | `flext-ldif/src/flext_ldif/_models/base.py`            |
| 3   | flext-ldif              | `utilities.py` | `FlextLdifUtilitiesPipeline` not in `Ldif` MRO                                | `flext-ldif/src/flext_ldif/_utilities/pipeline.py`     |
| 4   | flext-ldif              | `utilities.py` | `FlextLdifUtilitiesTransformers` not in `Ldif` MRO                            | `flext-ldif/src/flext_ldif/_utilities/transformers.py` |
| 5   | flext-infra             | `typings.py`   | `FlextInfraProtocolsBase` mixed into typings bases (protocol in wrong facade) | `flext-infra/src/flext_infra/typings.py`               |
| 6   | gruponos-meltano-native | —              | Missing `utilities.py` facade                                                 | Create new file                                        |
| 7   | gruponos-meltano-native | —              | Missing `typings.py` facade                                                   | Create new file                                        |

## 4. Loose Class Inventory by Project

### 4.1 Wave 1 — Leaf Integration L3 (low risk, 10 projects)

**flext-dbt-oracle** (4 loose):

- `api.py` → FlextDbtOracle (entry point) — KEEP
- `core.py` → FlextDbtOracleCore — absorb into `u.DbtOracle.Core`
- `dbt_client.py` → FlextDbtOracleClient — absorb into `u.DbtOracle.Client`
- `dbt_exceptions.py` → FlextDbtOracleError — already namespace pattern, rename to `errors.py`

**flext-dbt-oracle-wms** (4 loose):

- `simple_api.py` → FlextDbtOracleWms (entry point) — KEEP
- `core.py` → FlextDbtOracleWmsCore — absorb into `u.DbtOracleWms.Core`
- `services.py` → FlextDbtOracleWmsService — absorb into `u.DbtOracleWms.Service`
- `dbt_exceptions.py` → FlextDbtOracleWmsError — rename to `errors.py`

**flext-dbt-ldif** (7 loose):

- `simple_api.py` → FlextDbtLdif (entry point) — KEEP
- `core.py` → FlextDbtLdifCore — absorb into `u.DbtLdif.Core`
- `cli.py` → FlextDbtLdifCliService — absorb into `u.DbtLdif.CliService`
- `dbt_client.py` → FlextDbtLdifClient — absorb into `u.DbtLdif.Client`
- `dbt_exceptions.py` → FlextDbtLdifError — rename to `errors.py`
- `services.py` → FlextDbtLdifService — absorb into `u.DbtLdif.Service`
- `dbt_models.py` → ALREADY ARCHIVED ✅

**flext-dbt-ldap** (16 loose):

- `api.py` → FlextDbtLdap (entry point) — KEEP
- `core.py` → FlextDbtLdapCore — absorb into `u.DbtLdap.Core`
- `dbt_client.py` → FlextDbtLdapClient — absorb into `u.DbtLdap.Client`
- `dbt_exceptions.py` → FlextDbtLdapError — rename to `errors.py`
- `services.py` → FlextDbtLdapService — absorb into `u.DbtLdap.Service`
- `services_data.py` → FlextDbtLdapDataService — absorb into `u.DbtLdap.DataService`
- `services_generation.py` → FlextDbtLdapGenerationService — absorb into `u.DbtLdap.GenerationService`
- `services_infrastructure.py` → FlextDbtLdapInfrastructureService — absorb into `u.DbtLdap.InfrastructureService`
- `services_ldif.py` → FlextDbtLdapLdifService — absorb into `u.DbtLdap.LdifService`
- `services_materialization.py` → FlextDbtLdapMaterializationService — absorb into `u.DbtLdap.MaterializationService`
- `services_pipeline.py` → FlextDbtLdapPipelineService — absorb into `u.DbtLdap.PipelineService`
- `services_project.py` → FlextDbtLdapProjectService — absorb into `u.DbtLdap.ProjectService`
- `services_runner.py` → FlextDbtLdapRunnerService — absorb into `u.DbtLdap.RunnerService`
- `services_schema.py` → FlextDbtLdapSchemaService — absorb into `u.DbtLdap.SchemaService`
- `services_sync.py` → FlextDbtLdapSyncService — absorb into `u.DbtLdap.SyncService`
- `services_validation.py` → FlextDbtLdapValidationService — absorb into `u.DbtLdap.ValidationService`

**flext-tap-ldif** (3 loose):

- `tap.py` → FlextTapLdif (entry point) — KEEP
- `tap_client.py` → FlextTapLdifClient — absorb into `u.TapLdif.Client`
- `tap_streams.py` → FlextTapLdifStreams — absorb into `m.TapLdif.Streams`

**flext-target-oracle-wms** (7 loose):

- `target.py` → FlextTargetOracleWms (entry point) — KEEP
- `target_client.py` → FlextTargetOracleWmsClient — absorb into `u.TargetOracleWms.Client`
- `target_exceptions.py` → rename to `errors.py`
- `sinks.py` → absorb into `m.TargetOracleWms.Sinks`
- `target_services.py` → absorb into `u.TargetOracleWms.Services`
- `streams.py` → absorb into `m.TargetOracleWms.Streams`
- `transformation.py` → absorb into `u.TargetOracleWms.Transformation`

**flext-target-oracle-oic** (7 loose):

- `target.py` → FlextTargetOracleOic (entry point) — KEEP
- `target_client.py` → absorb into `u.TargetOracleOic.Client`
- `target_exceptions.py` → rename to `errors.py`
- `sinks.py` → absorb into `m.TargetOracleOic.Sinks`
- `target_services.py` → absorb into `u.TargetOracleOic.Services`
- `streams.py` → absorb into `m.TargetOracleOic.Streams`
- `transformation.py` → absorb into `u.TargetOracleOic.Transformation`

**algar-oud-mig** (2 loose):

- `api.py` → AlgarOudMig (entry point) — KEEP
- `migration.py` → AlgarOudMigMigration — absorb into `u.OudMig.Migration`

**gruponos-meltano-native** (2 loose + 2 missing facades):

- `orchestrator.py` → GruponosMeltanoOrchestrator — absorb into `u.Gruponos.Orchestrator`
- `_orchestrator/jobs.py` → GruponosMeltanoJobs — absorb into `u.Gruponos.Jobs`
- CREATE `utilities.py` with `GruponosMeltanoNativeUtilities(FlextMeltanoUtilities)`
- CREATE `typings.py` with `GruponosMeltanoNativeTypes(FlextMeltanoTypes)`

**flext-tap-oracle-wms** (10 loose):

- `tap.py` → FlextTapOracleWms (entry point) — KEEP
- `tap_client.py` → absorb into `u.TapOracleWms.Client`
- `tap_exceptions.py` → rename to `errors.py`
- `tap_streams.py` → absorb into `m.TapOracleWms.Streams`
- `discovery.py` → absorb into `u.TapOracleWms.Discovery`
- `filtering.py` → absorb into `u.TapOracleWms.Filtering`
- `replication.py` → absorb into `u.TapOracleWms.Replication`
- `schema_manager.py` → absorb into `u.TapOracleWms.SchemaManager`
- `state_manager.py` → absorb into `u.TapOracleWms.StateManager`
- `wms_streams.py` → absorb into `m.TapOracleWms.WmsStreams`

### 4.2 Wave 2 — Tap/Target L3 (6 projects)

**flext-tap-oracle** (8 loose):

- `tap.py` → entry point — KEEP
- `tap_client.py` → `u.TapOracle.Client`
- `tap_exceptions.py` → rename to `errors.py`
- `tap_streams.py` → `m.TapOracle.Streams`
- `catalog.py` → `u.TapOracle.Catalog`
- `discovery.py` → `u.TapOracle.Discovery`
- `replication.py` → `u.TapOracle.Replication`
- `schema_builder.py` → `u.TapOracle.SchemaBuilder`

**flext-tap-oracle-oic** (20 loose):

- `tap.py` → entry point — KEEP
- `tap_client.py` → `u.TapOracleOic.Client`
- `tap_exceptions.py` → rename to `errors.py`
- `tap_streams.py` → `m.TapOracleOic.Streams`
- `streams_consolidated.py` (10 classes) → absorb into `m.TapOracleOic.Streams`
- `health.py` → `u.TapOracleOic.Health`
- `domain/entities.py` → re-export aliases, must reference `m.TapOracleOic.*`
- `domain/services.py` → `u.TapOracleOic.DomainServices`

**flext-tap-ldap** (10 loose):

- `tap.py` → entry point — KEEP
- `tap_client.py` → `u.TapLdap.Client`
- `tap_exceptions.py` → rename to `errors.py`
- `tap_streams.py` → `m.TapLdap.Streams`
- `discovery.py` → `u.TapLdap.Discovery`
- `processing.py` → `u.TapLdap.Processing`
- `ldap_client.py` → `u.TapLdap.LdapClient`
- `replication.py` → `u.TapLdap.Replication`
- `schema.py` → `u.TapLdap.Schema`
- `state.py` → `u.TapLdap.State`

**flext-target-oracle** (13 loose):

- `target.py` → entry point — KEEP
- `target_client.py` → `u.TargetOracle.Client`
- `target_exceptions.py` → rename to `errors.py`
- `sinks.py` → `m.TargetOracle.Sinks`
- `target_services.py` → `u.TargetOracle.Services`
- `batch_processor.py` → `u.TargetOracle.BatchProcessor`
- `schema_manager.py` → `u.TargetOracle.SchemaManager`
- `state_manager.py` → `u.TargetOracle.StateManager`
- `table_manager.py` → `u.TargetOracle.TableManager`
- `type_mapper.py` → `u.TargetOracle.TypeMapper`
- `validation.py` → `u.TargetOracle.Validation`
- `streams.py` → `m.TargetOracle.Streams`
- `transformation.py` → `u.TargetOracle.Transformation`

**flext-target-ldap** (27 loose — HIGHEST):

- `target.py` → entry point — KEEP
- `target_client.py` → `u.TargetLdap.Client`
- `target_exceptions.py` → rename to `errors.py`
- `sinks.py` (7 classes) → `m.TargetLdap.Sinks.*`
- `target_services.py` (4 classes) → `u.TargetLdap.Services.*`
- `transformation.py` (2 classes) → `u.TargetLdap.Transformation`
- `processing_result.py` → `m.TargetLdap.ProcessingResult`
- `batch.py` → `u.TargetLdap.Batch`
- `connection.py` → `u.TargetLdap.Connection`
- `ldap_writer.py` → `u.TargetLdap.LdapWriter`
- `schema.py` → `u.TargetLdap.Schema`
- `state.py` → `u.TargetLdap.State`
- `validation.py` → `u.TargetLdap.Validation`

**flext-target-ldif** (5 loose):

- `target.py` → entry point — KEEP
- `target_client.py` → `u.TargetLdif.Client`
- `target_exceptions.py` → rename to `errors.py`
- `sinks.py` → `m.TargetLdif.Sinks`
- `streams.py` → `m.TargetLdif.Streams`

### 4.3 Wave 3 — Domain L2 (6 projects)

**flext-oracle-wms** (24 loose — 2ND HIGHEST):

- `wms_exceptions.py` (15 classes) → rename to `errors.py`, namespace as `e.OracleWms.*`
- `wms_api.py` → `u.OracleWms.Api`
- `wms_auth.py` → `u.OracleWms.Auth`
- `wms_client.py` → `u.OracleWms.Client`
- `wms_discovery.py` → `u.OracleWms.Discovery`
- `filtering.py` → `u.OracleWms.Filtering`
- `http_client.py` → `u.OracleWms.HttpClient`
- All service/utility classes → `u.OracleWms.*`

**flext-oracle-oic** (5 loose):

- `service.py` → FlextOracleOicService — KEEP (canonical service)
- `oic_client.py` → `u.OracleOic.Client`
- `oic_exceptions.py` → rename to `errors.py`
- `health.py` → `u.OracleOic.Health`
- `monitoring.py` → `u.OracleOic.Monitoring`

**flext-db-oracle** (6 loose):

- `api.py` → entry point — KEEP
- `db_client.py` → `u.DbOracle.Client`
- `db_exceptions.py` → rename to `errors.py`
- `migration.py` → `u.DbOracle.Migration`
- `schema.py` → `u.DbOracle.Schema`
- `services.py` → `u.DbOracle.Services`

**flext-ldap** (3 loose):

- `api.py` → entry point — KEEP
- `ldap_client.py` → `u.Ldap.Client`
- `ldap_exceptions.py` → rename to `errors.py`

**flext-ldif** (6 loose + 3 MRO gaps):

- `api.py` → entry point — KEEP
- `parser.py` → `u.Ldif.Parser`
- `writer.py` → `u.Ldif.Writer`
- `migration.py` → `u.Ldif.Migration`
- `schema.py` → `u.Ldif.Schema`
- `ldif_exceptions.py` → rename to `errors.py`
- FIX MRO: add `FlextLdifModelsBases` to models.py Ldif bases
- FIX MRO: add `FlextLdifUtilitiesPipeline` to utilities.py Ldif bases
- FIX MRO: add `FlextLdifUtilitiesTransformers` to utilities.py Ldif bases

**flext-plugin** (12 loose):

- `api.py` → entry point — KEEP
- `manager.py` → `u.Plugin.Manager`
- `installer.py` → `u.Plugin.Installer`
- `registry.py` → `u.Plugin`
- `discovery.py` → `u.Plugin`
- `loader.py` → `u.Plugin.Loader`
- `validator.py` → `u.Plugin.Validator`
- `hooks.py` → `u.Plugin.Hooks`
- `lifecycle.py` → `u.Plugin`
- `settings_loader.py` → `u.Plugin.SettingsLoader`
- `plugin_exceptions.py` → rename to `errors.py`
- `sandbox.py` → `u.Plugin.Sandbox`

### 4.4 Wave 4 — Platform L2 (4 projects)

**flext-meltano** (3 loose at top level, services scoped):

- `api.py` → entry point — KEEP
- `base.py` → `FlextMeltanoServiceBase` — MRO base of all services — KEEP
- `cli.py` → scoped service — KEEP
- `services/` subdir → scoped correctly
- `singer/` subdir → scoped correctly
- `dbt/` subdir → scoped correctly
- FIX: `singer/translator.py` → absorb into `u.Meltano.Singer.Translator`
- FIX: `services/validators.py` → absorb into `u.Meltano.Validators`

**flext-grpc** (7 loose):

- `api.py` → entry point — KEEP
- `errors.py` → already correct naming
- `services.py` → KEEP
- `server.py` → `u.Grpc.Server`
- `client.py` → `u.Grpc.Client`
- `interceptors.py` → `u.Grpc.Interceptors`
- `health.py` → `u.Grpc.Health`

**flext-observability** (17 loose):

- `api.py` → entry point — KEEP
- `context.py` → `u.Obs.Context`
- `advanced_context.py` → merge into `context.py` → `u.Obs.Context.Advanced`
- `collectors/` → scoped correctly
- `exporters/` → scoped correctly
- `metrics.py` → `u.Obs.Metrics`
- `traces.py` → `u.Obs.Traces`
- `dashboards.py` → `u.Obs.Dashboards`
- `alerts.py` → `u.Obs.Alerts`
- (remaining files follow same pattern)

**flext-tests** (4 loose):

- `_validator/` subdir → scoped validator extensions — KEEP
- `_factories/` subdir → scoped factory functions — KEEP
- `builders.py` → `u.Tests.Builders`
- `matchers.py` → `u.Tests.Matchers`

### 4.5 Wave 5 — API/Auth/Web (3 projects)

**flext-api** (17 loose + 1 MRO gap):

- `api.py` → entry point — KEEP
- `server.py` → canonical server — KEEP
- `client.py` → `u.Api.Client`
- `adapters.py` → `u.Api.Adapters`
- `serializers.py` → `u.Api.Serializers`
- `middleware.py` → `u.Api.Middleware`
- `lifecycle_manager.py` → `u.Api.LifecycleManager`
- `server_factory.py` → absorb into `server.py`
- `settings_manager.py` → absorb into `settings.py`
- `storage.py` → `u.Api.Storage`
- `webhook.py` → `u.Api.Webhook`
- `registry.py` → `u.Api.Registry`
- `plugins.py` → `p.Api.Plugins`
- `transports.py` → `p.Api.Transports`
- `exceptions.py` → rename to `errors.py`
- `app.py` → absorb into `api.py` or `server.py`
- `protocol_impls/` → scoped correctly — KEEP
- `schemas/` → scoped correctly — KEEP
- FIX MRO: `FlextApiTypes` should inherit `FlextWebTypes`, not `FlextTypes`

**flext-auth** (11 loose):

- `api.py` → entry point — KEEP
- `managers.py` → absorb into `api.py` MRO
- `mixins.py` → absorb into `api.py` MRO
- `middleware.py` → `u.Auth.Middleware`
- `provider_service.py` → `u.Auth.ProviderService`
- `quickstart.py` → `u.Auth.Quickstart`
- `registry.py` → `u.Auth.Registry`
- `session_service.py` → `u.Auth.SessionService`
- `token_service.py` → `u.Auth.TokenService`
- `user_service.py` → `u.Auth.IdentityService`
- `providers/` → scoped correctly — KEEP
- `_managers/` → scoped correctly — KEEP

**flext-web** (2 loose):

- `api.py` → entry point — KEEP
- `base.py` → MRO base — KEEP

### 4.6 Wave 6 — Core/CLI/Infra (3 projects)

**flext-core** (2 true loose, rest conformant):

- ABSORB `FlextError` → `m.Error` inner class in `_models/`
- ABSORB `FlextErrorDomain` → `c.ErrorDomain` inner class in `_constants/`
- FIX MRO: if needed after absorption
- All other files → conformant (aliased or MRO bases)

**flext-cli** (2 loose):

- `api.py` → entry point — KEEP
- `base.py` → MRO base — KEEP
- `services/` → scoped correctly

**flext-infra** (0 loose, 1 MRO cleanup):

- FIX: Remove `FlextInfraProtocolsBase` from `t.Infra` MRO bases (protocol in wrong facade)

## 5. Execution Protocol (Per Project)

```
1. Read ALL loose .py files in src/
2. For each file:
   a. Identify all module-level classes
   b. Determine target facade per §2.1 table
   c. Move class body into target facade as inner class
   d. Update facade MRO if adding new submodule file
3. sg --pattern 'from <pkg>.<old_module> import <ClassName>' → rewrite to facade import
4. sg --pattern '<ClassName>(' → rewrite to '<namespace>.<Project>.<ClassName>('
5. Archive original file: mv <file>.py <file>.py.bak
6. make gen (regenerate __init__.py)
7. ruff check */ (MUST be 0 for affected project)
8. pyrefly check */ (MUST be 0 workspace-wide)
9. If errors → fix forward, NEVER rollback
```

## 6. Quality Gates

| Gate        | Check                              | Required           |
| ----------- | ---------------------------------- | ------------------ |
| Per-file    | ruff check on modified file        | 0 errors           |
| Per-project | pyrefly check on project src/      | 0 errors           |
| Per-wave    | ruff check */                      | 0 new errors       |
| Per-wave    | pyrefly check */                   | 0 errors workspace |
| Per-wave    | sg search for old import patterns  | 0 matches          |
| Final       | ruff + pyrefly + pyright workspace | 0 errors           |

## 7. Wave Execution Order

| Wave      | Projects               | Est. Loose | Parallelism |
| --------- | ---------------------- | ---------- | ----------- |
| 1         | 10 leaf integration L3 | ~66        | 3-4 agents  |
| 2         | 6 tap/target L3        | ~83        | 3 agents    |
| 3         | 6 domain L2            | ~56        | 3 agents    |
| 4         | 4 platform L2          | ~31        | 2 agents    |
| 5         | 3 API/Auth/Web         | ~30        | 2 agents    |
| 6         | 3 Core/CLI/Infra       | ~3         | 1 agent     |
| **Total** | **32**                 | **~269**   | —           |

## 8. Out of Scope

- Test files (`tests/`) — not in this spec
- Example files (`examples/`) — not in this spec
- Pyright fixes — separate effort
- New feature development — only structural alignment
