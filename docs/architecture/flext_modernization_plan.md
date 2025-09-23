# FLEXT Core Modernization Plan

This document outlines the phased approach for consolidating FLEXT around domain services, a unified dispatcher, and context-first observability.

## Phase 0 — Baseline Assessment (Week 1)

- Inventory all domain services, handlers, bus registrations, and custom dispatch mechanisms across the ecosystem.
- Document current configuration flows and context initialisation patterns.
- Identify key stakeholders and assign owners per sub-project.
- Produce tracking dashboard (spreadsheet or issue board) summarising findings.

### Phase 0 Findings (2025-09-17)

**Domain & Handler Inventory**

- `flext-cli` exposes 12 domain services and seven command handlers (e.g. `flext-cli/src/flext_cli/api.py:34`, `flext-cli/src/flext_cli/handlers.py:50`) while the `OperationDispatcher` remains a bespoke match-case dispatcher (`flext-cli/src/flext_cli/api.py:69`) bound to a local command bus registered in `flext-cli/src/flext_cli/cli_bus.py:40`.
- `flext-target-oracle` consolidates eight domain services plus a single `FlextHandlers` implementation (`flext-target-oracle/src/flext_target_oracle/target_commands.py:255`) with command-bus wiring in `flext-target-oracle/src/flext_target_oracle/target_refactored.py:47` and separate Singer message dispatch in `flext-target-oracle/src/flext_target_oracle/target_client.py:210`.
- Connector packages (`flext-db-oracle/src/flext_db_oracle/services.py:58`, `flext-ldif/src/flext_ldif/services.py:97`, `flext-ldap/src/flext_ldap/domain.py:400`) and platform utilities (`src/flext/application_handlers.py:58`) each define their own domain services yet depend on local helper stacks and ad-hoc dispatch helpers (`src/flext/application_handlers.py:214`).
- Observability, plugin, and quality tooling provide focused domain services (`flext-observability/src/flext_observability/factories.py:46`, `flext-plugin/src/flext_plugin/flext_plugin_services.py:30`, `flext-quality/src/flext_quality/cli.py:44`) but remain isolated from the shared bus/dispatcher pathway.
- Several ecosystem packages consciously skip `FlextService` adoption (for example `flext-auth/src/flext_auth/quickstart.py:17`), signalling migration candidates that will require targeted change management.

**Configuration & Context Observations**

- `FlextConfig` still acts as the global source of truth with layered loading (`flext-core/src/flext_core/config.py:926`) and permissive merge APIs (`flext-core/src/flext_core/config.py:1640`), yet downstream projects frequently fork configuration logic instead of reusing these hooks.
- The dependency container defers to `FlextConfig` while keeping shadow copies of database/security/logging payloads (`flext-core/src/flext_core/container.py:636`), creating parallel configuration surfaces that must be rationalised.
- CLI tooling extends `FlextConfig` (`flext-cli/src/flext_cli/config.py:17`) but the primary service lazily hydrates settings on demand (`flext-cli/src/flext_cli/core.py:52`), leading to divergent lifecycle expectations across command handlers and formatters.
- `FlextContext` offers comprehensive correlation/request scoping (`flext-core/src/flext_core/context.py:19`), yet packages such as the target connector still log context manually (“Without FlextContext” in `flext-target-oracle/src/flext_target_oracle/target_observability.py:319`) and the CLI relies on a bespoke context object (`flext-cli/src/flext_cli/context.py:14`).

**Stakeholders & Ownership**

- Core Platform (flext-core, shared `src/flext_*` utilities) – proposed owner for dispatcher, context, and configuration consolidation work.
- Developer Experience (flext-cli, flext_cli tooling) – primary stakeholders for dispatcher integration and handler ergonomics.
- Data Connectors (flext-target-\*, flext-db-oracle, flext-ldif, flext-ldap, flext-meltano) – require guided migrations off custom dispatch and config stacks.
- Platform Extensions & APIs (flext-api, flext-plugin, flext-observability) – need alignment on shared dispatcher/context contracts.
- Quality & Safeguards (flext-quality, test harnesses) – should govern regression coverage as migrations proceed.

### Tracking Dashboard (2025-09-17)

| Workstream                 | Status                                                              | Owner                                | Notes                                                                 |
| -------------------------- | ------------------------------------------------------------------- | ------------------------------------ | --------------------------------------------------------------------- |
| Domain services & handlers | Baseline captured; gaps flagged in non-adopters                     | Core Platform                        | Consolidate service list and publish importable registry.             |
| Dispatcher & bus usage     | Fragmented between CLI/targets and local helpers                    | Core Platform × Developer Experience | Prototype unified dispatcher that replaces bespoke match-case blocks. |
| Configuration lifecycle    | Global `FlextConfig` vs package-specific models needs harmonisation | Core Platform                        | Draft integration guide + container refactor plan.                    |
| Context & observability    | Core context unused outside tests/connectors                        | Observability Team                   | Define adoption checklist + implement shim for CLI and connectors.    |
| Connector migrations       | High domain-service count with bespoke pipelines                    | Data Connectors Guild                | Prioritise Oracle + LDAP for early pilot once dispatcher stabilises.  |
| QA coverage & tooling      | Tests depend on legacy patterns; monitoring needed                  | Quality & Safeguards                 | Map coverage expectations to migration milestones.                    |

### Phase 0 Immediate Actions (2025-09-17)

- **Owner map confirmation:** Core Platform to circulate the stakeholder list above via architecture sync notes and request named delegates from each group by 2025-09-19. Capture confirmations in the programme tracker and flag gaps to programme management.
- **Cross-team broadcast:** Developer Experience to publish a short Loom/Slack update summarising the inventory hotspots (CLI dispatcher, target command routing, connector pipelines) and invite feedback ahead of Phase 1.
- **QA alignment:** Quality & Safeguards to review the tracking dashboard and propose regression coverage expectations for early dispatcher pilots before end of week.

### Phase 1 Design Session Prep (2025-09-17)

- **Session charter:** Draft agenda covering unified dispatcher goals, adoption constraints from CLI (`flext-cli/src/flext_cli/api.py:69`) and target connector flows (`flext-target-oracle/src/flext_target_oracle/target_client.py:210`), plus configuration/context alignment checkpoints.
- **Participants:** Core Platform leads, Developer Experience leads, and representatives from Data Connectors (Oracle, LDAP) to validate migration feasibility.
- **Pre-reads:** Share Phase 0 findings section and proposed charter 48 hours in advance; include links to current dispatcher implementations and configuration lifecycle code (`flext-core/src/flext_core/config.py:926`, `flext-core/src/flext_core/context.py:19`).
- **Logistics:** Schedule 90-minute working session during Week 2 kickoff; capture decisions and opening actions directly in the modernization dashboard for traceability.

### Project Participant Snapshot (2025-09-17)

Repository scan results mapping each package to current dispatcher/context adoption. Counts are derived from class inheritance and usage references gathered on 2025-09-17.

| Group                      | Project                 | Domain Services                                                            | Handlers                                                                   | Bus | Context | Config | Notes                         |
| -------------------------- | ----------------------- | -------------------------------------------------------------------------- | -------------------------------------------------------------------------- | --- | ------- | ------ | ----------------------------- |
| Core Platform              | core-root               | Yes (`src/flext/dev.py:26`)                                                | No                                                                         | Yes | No      | No     | Bus used without handlers     |
| Core Platform              | flext-core              | No                                                                         | Yes (`flext-core/src/flext_core/bus.py:93`)                                | Yes | Yes     | Yes    | No domain services registered |
| Developer Experience       | flext-cli               | Yes (`flext-cli/src/flext_cli/service.py:33`)                      | Yes (`flext-cli/src/flext_cli/handlers.py:50`)                             | Yes | No      | Yes    | Context not adopted           |
| Platform Extensions & APIs | flext-api               | Yes (`flext-api/src/flext_api/client.py:35`)                               | No                                                                         | No  | No      | Yes    | Context not adopted           |
| Platform Extensions & APIs | flext-auth              | No                                                                         | No                                                                         | No  | No      | Yes    | No domain services registered |
| Platform Extensions & APIs | flext-grpc              | No                                                                         | No                                                                         | No  | No      | No     | No domain services registered |
| Platform Extensions & APIs | flext-observability     | Yes (`flext-observability/src/flext_observability/factories.py:46`)        | No                                                                         | No  | No      | No     | Context not adopted           |
| Platform Extensions & APIs | flext-plugin            | Yes (`flext-plugin/src/flext_plugin/flext_plugin_services.py:30`)          | No                                                                         | No  | No      | No     | Context not adopted           |
| Platform Extensions & APIs | flext-web               | No                                                                         | No                                                                         | No  | No      | Yes    | No domain services registered |
| Quality & Safeguards       | flext-quality           | Yes (`flext-quality/src/flext_quality/cli.py:44`)                          | No                                                                         | No  | No      | No     | Context not adopted           |
| Data Connectors            | flext-db-oracle         | Yes (`flext-db-oracle/src/flext_db_oracle/cli.py:38`)                      | No                                                                         | No  | No      | No     | Context not adopted           |
| Data Connectors            | flext-dbt-ldap          | No                                                                         | No                                                                         | No  | No      | Yes    | No domain services registered |
| Data Connectors            | flext-dbt-ldif          | No                                                                         | No                                                                         | No  | No      | Yes    | No domain services registered |
| Data Connectors            | flext-dbt-oracle        | No                                                                         | No                                                                         | No  | No      | Yes    | No domain services registered |
| Data Connectors            | flext-dbt-oracle-wms    | No                                                                         | No                                                                         | No  | No      | Yes    | No domain services registered |
| Data Connectors            | flext-ldap              | Yes (`flext-ldap/src/flext_ldap/adapters.py:35`)                           | Yes (`flext-ldap/src/flext_ldap/domain.py:1284`)                           | No  | No      | Yes    | Context not adopted           |
| Data Connectors            | flext-ldif              | Yes (`flext-ldif/src/flext_ldif/cli.py:16`)                                | No                                                                         | No  | No      | Yes    | Context not adopted           |
| Data Connectors            | flext-meltano           | Yes (`flext-meltano/src/flext_meltano/executors.py:39`)                    | No                                                                         | No  | No      | Yes    | Context not adopted           |
| Data Connectors            | flext-oracle-oic-ext    | Yes (`flext-oracle-oic-ext/src/flext_oracle_oic_ext/ext_services.py:58`)   | No                                                                         | No  | No      | Yes    | Context not adopted           |
| Data Connectors            | flext-oracle-wms        | No                                                                         | No                                                                         | No  | No      | Yes    | No domain services registered |
| Data Connectors            | flext-tap-ldap          | No                                                                         | No                                                                         | No  | No      | Yes    | No domain services registered |
| Data Connectors            | flext-tap-ldif          | No                                                                         | No                                                                         | No  | No      | Yes    | No domain services registered |
| Data Connectors            | flext-tap-oracle        | No                                                                         | No                                                                         | No  | No      | Yes    | No domain services registered |
| Data Connectors            | flext-tap-oracle-oic    | No                                                                         | No                                                                         | No  | No      | Yes    | No domain services registered |
| Data Connectors            | flext-tap-oracle-wms    | No                                                                         | No                                                                         | No  | No      | No     | No domain services registered |
| Data Connectors            | flext-target-ldap       | No                                                                         | No                                                                         | No  | No      | Yes    | No domain services registered |
| Data Connectors            | flext-target-ldif       | No                                                                         | No                                                                         | No  | No      | Yes    | No domain services registered |
| Data Connectors            | flext-target-oracle     | Yes (`flext-target-oracle/src/flext_target_oracle/target_services.py:101`) | Yes (`flext-target-oracle/src/flext_target_oracle/target_commands.py:255`) | Yes | Yes     | No     |                               |
| Data Connectors            | flext-target-oracle-oic | No                                                                         | No                                                                         | No  | No      | No     | No domain services registered |
| Data Connectors            | flext-target-oracle-wms | No                                                                         | No                                                                         | No  | No      | No     | No domain services registered |

### Phase 0 Action Status (2025-09-17)

| Action                   | Status   | Notes                                                                                           |
| ------------------------ | -------- | ----------------------------------------------------------------------------------------------- |
| Owner map confirmation   | Pending  | Core Platform to send delegate request via architecture sync; scheduling for 2025-09-19.        |
| Cross-team broadcast     | Pending  | Developer Experience to record Loom/Slack update summarising dispatcher and connector hotspots. |
| QA alignment             | Pending  | Quality & Safeguards reviewing coverage expectations; awaiting response.                        |
| Participant snapshot     | Complete | Repository-wide adoption table added above for ecosystem visibility.                            |
| Dispatcher charter draft | Complete | Draft charter and initial sequence flow captured below to seed Week 2 workshop.                 |

### Action Support Details (2025-09-17)

**Owner Map Delegation Template**

Subject: FLEXT modernization delegate needed — <team name>

Body highlights:

- Recap goal: unify dispatcher/context per modernization plan.
- Request named delegate and backup by 2025-09-19.
- Link Phase 0 findings + participant snapshot section (above) for reference.
- Point to dispatcher charter draft for upcoming workshop expectations.

**Cross-Team Broadcast Outline**

- 3–4 minute Loom demo showing CLI dispatcher codepath (`flext-cli/src/flext_cli/api.py:69`) and target connector routing (`flext-target-oracle/src/flext_target_oracle/target_client.py:210`).
- Slides or Slack bullets covering top gaps (absence of `FlextContext`, package adoption counts) sourced from participant snapshot.
- Call-to-action: submit questions before Week 2 design session; share contact for follow-up.

**QA Alignment Expectations**

- Identify regression suites touching dispatcher/handlers (`flext-core/tests/unit/test_flext_commands.py`, `flext-cli/tests/test_core.py`).
- Define minimum coverage for pilot migrations (CLI + Oracle) and note dependencies on legacy utilities (`flext-core/src/flext_core/utilities.py`).
- Confirm reporting cadence and exit criteria before greenlighting dispatcher prototype roll-out.

**Workshop Prep Notes**

- Pre-read package links: dispatcher charter draft, participant snapshot, `flext-core/src/flext_core/bus.py:93`, `flext-core/src/flext_core/context.py:19`, `flext-cli/src/flext_cli/cli_bus.py:23`.
- Sequence diagram TODO: map command origin → dispatcher → domain service → context logging.
- Logistics: collect availability poll responses, schedule 90-minute slot, assign scribe to capture decisions in dashboard.

### Phase 1 Dispatcher Charter Draft (2025-09-17)

- **Goal:** Define a unified dispatcher that replaces bespoke match-case routing in CLI (`flext-cli/src/flext_cli/api.py:69`) and connector pipelines (`flext-target-oracle/src/flext_target_oracle/target_client.py:210`) while reusing `FlextBus` semantics (`flext-core/src/flext_core/bus.py:93`).
- **Scope:** Align handler registration across `FlextCliCommandBusService` (`flext-cli/src/flext_cli/cli_bus.py:23`) and target command orchestration to ensure single registration surface for domain services.
- **Deliverables:** Dispatcher API proposal, reference implementation sketch within flext-core, migration checklist for CLI and Oracle/LDAP connectors, and updated handler lifecycle documentation.
- **Constraints:** Maintain compatibility with existing `FlextHandlers` signature (`flext-core/src/flext_core/handlers.py:16`) and preserve Pydantic validation patterns in command models.
- **Context integration:** Decide on required `FlextContext` integration steps so downstream services stop emitting manual context logs (`flext-target-oracle/src/flext_target_oracle/target_observability.py:319`) and align with core context API (`flext-core/src/flext_core/context.py:19`).
- **Open questions:** How to expose dispatcher configuration through `FlextConfig` without duplicating CLI overrides (`flext-cli/src/flext_cli/config.py:17`); what telemetry hooks are required for Observability adoption.
- **Next milestones:** Circulate charter for feedback (T+2 days), iterate on the draft sequence flow below ahead of Week 2 kickoff, and identify pilot services for prototype integration.

```text
User CLI command
  │
  ▼
FlextCliCommandBusService (flext-cli/src/flext_cli/cli_bus.py:23)
  │  register -> unified dispatcher
  ▼
Flext Dispatcher (proposed flext-core module)
  │  resolve handler via registry + context
  ▼
FlextHandlers implementation (e.g. flext-target-oracle/src/flext_target_oracle/target_commands.py:255)
  │  invoke domain service
  ▼
FlextService (e.g. flext-target-oracle/src/flext_target_oracle/target_services.py:101)
  │  emits FlextResult + context metadata
  ▼
FlextContext / Observability sinks (flext-core/src/flext_core/context.py:19)
  │  propagate result
  ▼
Caller (CLI, API, connector)
```

## Phase 1 — Core Design Validation (Weeks 2-3)

- Finalise dispatcher API that routes commands/queries (Pydantic models) to domain service methods.
- Draft reference architecture diagram covering domain services, dispatcher, context, logging, and configuration.
- Build proof-of-concept within flext-core: implement dispatcher, adapt two representative services, and expose CLI/API samples.
- Validate via automated tests (pytest + coverage) and manual walkthroughs with stakeholders.

#### Phase 1 Dispatcher Design Brief (2025-09-17)

- **Dispatcher core:** Introduce a `FlextDispatcher` facade inside flext-core that wraps `FlextBus` (`flext-core/src/flext_core/bus.py:93`) and exposes explicit `register_command`, `register_query`, and `dispatch` methods. The dispatcher should accept Pydantic command/query models, resolve handlers defined via `FlextHandlers` (`flext-core/src/flext_core/handlers.py:16`), and automatically wrap handler execution inside a `FlextContext` scope (`flext-core/src/flext_core/context.py:19`).
- **Registration contract:** Align CLI and connector registration by extracting the logic currently embedded in `FlextCliCommandBusService` (`flext-cli/src/flext_cli/cli_bus.py:23`) and `OracleTargetCommandHandler` (`flext-target-oracle/src/flext_target_oracle/target_commands.py:255`) into dispatcher-aware factories. Registration should accept domain services or handler instances and handle idempotent re-registrations.
- **Configuration integration:** Surface dispatcher configuration via `FlextConfig` extension points (`flext-core/src/flext_core/config.py:926`), enabling packages like `flext-cli` and `flext-target-oracle` to opt into centralized handler discovery without duplicating settings.
- **Context & logging:** Ensure dispatcher enforces correlation/trace propagation by default and plugs into observability tooling so connectors stop logging context manually (see `flext-target-oracle/src/flext_target_oracle/target_observability.py:319`).
- **Pilot implementation status:** `flext-cli` and `flext-target-oracle` route through `FlextDispatcher` via environment flags (`FLEXT_CLI_ENABLE_DISPATCHER`, `FLEXT_TARGET_ORACLE_ENABLE_DISPATCHER`).
- **Backward compatibility:** Maintain compatibility with existing `FlextBus.create_command_bus()` entry points while marking bespoke dispatchers (e.g. `flext-cli/src/flext_cli/api.py:69`) for deprecation once migrations complete.
- **Pilot implementation status:** `flext-cli` command bus now routes through `FlextDispatcher` behind the `FLEXT_CLI_ENABLE_DISPATCHER` flag to validate migration path.

#### Phase 1 Pilot Scope (2025-09-17)

- **Primary pilot:**
  - `flext-cli` command handlers (ShowConfig/SetConfig/Auth flows in `flext-cli/src/flext_cli/handlers.py`).
  - `flext-target-oracle` command orchestration (`flext-target-oracle/src/flext_target_oracle/target_refactored.py:46` and `target_commands.py:255`).
  - Deliverable: both packages delegate to shared dispatcher APIs while preserving CLI UX and target loading behaviour.
    - Status: CLI and Oracle target services now dispatch via the shared facade guarded by env flags (`FLEXT_CLI_ENABLE_DISPATCHER`, `FLEXT_TARGET_ORACLE_ENABLE_DISPATCHER`).
- **Secondary observation:** Track readiness for `flext-ldap` services (`flext-ldap/src/flext_ldap/domain.py:400`) to migrate once pilot patterns stabilise.
- **Migration steps:**
  1. Wrap existing handler registration inside dispatcher adapters.
  2. Inject dispatcher via dependency container (`flext-core/src/flext_core/container.py:605`) or package-specific factories.
  3. Update tests to assert dispatcher path usage (CLI tests in `flext-cli/tests/test_core.py`, target tests in `flext-core/tests/unit/test_flext_commands.py`).
  4. Document upgrade notes for downstream connectors.
- **Risk controls:** Feature-flag dispatcher adoption per package, retain legacy bus pathways for one release cycle, and add rollback instructions to modernization dashboard.

#### Phase 1 Validation Strategy (2025-09-17)

- **Automated tests:** Extend flext-core command bus suites (`flext-core/tests/unit/test_flext_commands.py`, `flext-core/tests/unit/test_commands_comprehensive_coverage.py`) to exercise dispatcher registration/dispatch flows. Mirror scenarios in CLI (`flext-cli/tests/test_core.py`) and Oracle target tests.
- **End-to-end checks:** Execute CLI smoke commands and Oracle target dry runs using dispatcher feature flag enabled; capture metrics for handler latency and error propagation.
- **Observability:** Verify correlation IDs appear in logs when dispatcher is enabled and inspect instrumentation coverage via `flext-observability` tooling.
- **Acceptance criteria:** Dispatcher drives 100% of pilot commands, regression suite remains green, and QA sign-off (per alignment plan) is granted before expanding to other packages.

#### Phase 1 Implementation Update (2025-09-17)

- **Shared registry helper:** Added `FlextRegistry` to `flext-core/src/flext_core/registry.py`, enabling idempotent bulk registration with summary reporting and re-exported via `flext-core/src/flext_core/__init__.py`.
- **CLI adoption:** `flext-cli/src/flext_cli/cli_bus.py` now relies on the registry for handler setup, falling back to the bus only when dispatcher registration fails while preserving feature flag `FLEXT_CLI_ENABLE_DISPATCHER` semantics.
- **Connector feature flags:** Introduced dispatcher bridges guarded by environment toggles for `flext-ldap` (`FLEXT_LDAP_ENABLE_DISPATCHER`), `flext-ldif` (`FLEXT_LDIF_ENABLE_DISPATCHER`), and `client-a-oud-mig` (`client-a_OUD_MIG_ENABLE_DISPATCHER`), wiring domain factories / APIs through the shared dispatcher while retaining legacy code paths.
- **Documentation of new flow:** `flext-ldap/src/flext_ldap/domain.py`, `flext-ldif/src/flext_ldif/api.py`, and `client-a-oud-mig/src/client-a_oud_mig/commands.py` now route command execution through `FlextDispatcher` when the respective flags are enabled, with fallbacks and structured logging on dispatcher failure.
- **Service-level adoption:** `FlextLdapServices.create_user` now consults the shared dispatcher before falling back to direct entity construction, keeping repository persistence intact while centralising validation logic.
- **Database connector integration:** `flext-db-oracle` exposes dispatcher-backed API/service flows via the `FLEXT_DB_ORACLE_ENABLE_DISPATCHER` flag, covering connection lifecycle and query execution through `flext_db_oracle/dispatcher.py`.
- **Test harness reliability:** Project-local conftests were updated to prepend `flext-core/src` (plus required sibling packages) to `sys.path` and to gracefully tolerate missing `docker`/`flext_tests` dependencies. Targeted dispatcher scenarios in `flext-ldap`, `flext-ldif`, and `client-a-oud-mig` now run under `pytest` with explicit commands (`PYTHONPATH=src pytest …`, `pytest -c /dev/null …`) without external fixtures.
- **Verification status:** Targeted unit/integration tests exercised the dispatcher paths (`flext-core/tests/unit/test_dispatcher.py`, `flext-ldap/tests/unit/test_domain_functional.py`, `flext-ldap/tests/unit/test_services.py`, `flext-ldif/tests/integration/test_api.py`, `flext-db-oracle/tests/unit/test_api_comprehensive.py`, `client-a-oud-mig/tests/unit/test_main.py`). Runs succeeded with explicit commands (`PYTHONPATH=src …`, `pytest -c /dev/null …`) after injecting the shared `flext-core/src` path; remaining full-suite coverage still depends on packaging the `flext_tests` helpers for general availability.
- **Next focus:** Extend dispatcher coverage to remaining connectors (`flext-meltano`, `flext-target-*`) and unblock automated test execution by packaging `flext_tests` into the workspace tooling layer.

## Phase 2 — Tooling & Templates (Weeks 4-5)

- Publish updated documentation: service contract, dispatcher usage, context lifecycle, configuration guidelines.
- Ship template repository (or Cookiecutter) reflecting the new architecture.
- Create linting/check tooling: Ruff rules, mypy plugin, or custom scripts to flag direct service invocations, missing dispatcher usage, and absent context seeding.
- Add CI jobs to enforce tooling across flext-core and one pilot downstream project.

#### Phase 2 Tooling & Enablement Plan (2025-09-17)

- **Documentation uplift:**
  - Update `flext-core/docs/api-reference.md` and `docs/api/flext-core.md` to include dispatcher usage examples and context lifecycle steps once the pilot lands.
  - Add modernization FAQ and upgrade notes to `docs/architecture/flext_modernization_plan.md` and cross-link from package READMEs (`flext-cli/README.md`, `flext-target-oracle/docs/README.md`).
- **Template repository:**
  - Base skeleton on current CLI + target pilots with dispatcher integration stubs.
  - Include sample handler registration and context instrumentation along with pytest scaffolding referencing `flext-core/tests/unit/test_flext_commands.py`.
- **Static analysis & linting:**
  - Extend shared Ruff config (`ruff-shared.toml`) with rules detecting direct `FlextService.execute` calls and missing dispatcher usage.
  - Prototype mypy plugin enforcing dispatcher type contracts against `FlextHandlers` annotations.
  - Provide opt-in pre-commit hook updates across packages.
- **CI enforcement:**
  - Add dispatcher smoke tests to existing GitHub Actions workflows (reference `.github/workflows`, once updated) ensuring feature flag coverage.
  - Capture coverage deltas in `ecosystem_coverage.csv` once new suites run.
- **Timeline:** Complete documentation drafts and lint rules by end of Week 4; template repository and CI pipeline updates by Week 5.

## Phase 3 — Ecosystem Migration (Weeks 6-10)

- Define migration playbook (sequence, acceptance criteria, rollback steps).
- Pilot migration in two projects (e.g. flext-target-oracle, flext-cli); iterate on tooling/documentation based on feedback.
- Roll out to remaining packages prioritised by usage/criticality.
- Track progress weekly, reporting blockers and required platform changes.

#### Phase 3 Migration Playbook (2025-09-17)

- **Sequencing:**
  1. Confirm pilot completion (CLI + Oracle target) with QA sign-off.
  2. Migrate remaining Data Connectors with high usage: `flext-ldap`, `flext-ldif`, `flext-meltano` (see participant snapshot above for adoption gaps).
  3. Transition Platform Extensions (`flext-api`, `flext-plugin`, `flext-observability`) once dispatcher APIs stabilise.
  4. Clean up remaining tap/target packages and platform utilities.
- **Acceptance criteria per package:**
  - All command/query flows route through `FlextDispatcher`.
  - `FlextContext` instrumentation present for emitted logs.
  - CI checks (lint + dispatcher smoke suite) green with feature flag enabled.
  - Decision log entry created in modernization dashboard summarising migration.
- **Rollback strategy:**
  - Maintain legacy bus dispatch path protected by feature flag for one release cycle.
  - Document revert steps in package README (e.g. `flext-cli/README.md`, `flext-target-oracle/docs/README.md`).
  - Track flag status in central configuration sheet to avoid drift.
- **Risk management:**
  - Monitor performance metrics via `flext-observability` dashboards; alert on latency regressions.
  - Schedule weekly migration stand-up to triage blockers across connector teams.
  - Align release cadence with QA to avoid overlapping high-risk deployments.
- **Reporting:**
  - Use participant snapshot as baseline; update table after each package migrates.
  - Publish weekly status in architecture sync referencing this playbook.

## Phase 4 — Deprecation & Cleanup (Weeks 11-12)

- Deprecate legacy modules/aliases (FlextProcessing, FlextBus, FlextCqrs, unused mixins) with clear timelines and messaging.
- Remove obsolete documentation/examples/tests once downstream adoption reaches threshold.
- Simplify utility surface (drop unused mixins, consolidate serialization helpers) and update type exports.
- Finalise long-term maintenance plan (ownership, release cadence, quality gates).

#### Phase 4 Deprecation Checklist (2025-09-17)

- **Module sunset plan:**
  - Announce deprecation of `flext_core.processing.FlextProcessing` (`flext-core/src/flext_core/processing.py:13`) and related aliases once dispatcher adoption reaches >80% of packages.
  - Replace wildcard exports in `flext-core/src/flext_core/__init__.py` with curated dispatcher/context surfaces; schedule warning releases one sprint ahead.
  - Retire legacy CQRS helpers (`flext-core/src/flext_core/cqrs.py`) after providing dispatcher parity samples.
- **Documentation cleanup:**
  - Archive outdated examples (e.g. `flext-core/examples/03_cqrs_commands.py`, `20_boilerplate_reduction.py`) or update them to the dispatcher pattern.
  - Purge deprecated guidance from `FLEXT_REFACTORING_PROMPT.md` and `docs/quick-reference.md` once new templates are published.
- **Test & tooling updates:**
  - Remove tests targeting legacy pathways (`flext-core/tests/unit/test_processing_comprehensive.py`) after confirming dispatcher coverage.
  - Ensure lint rules flag usage of deprecated symbols one release before removal.
- **Communication timeline:**
  - T-6 weeks: Publish deprecation notice and migration checklist.
  - T-2 weeks: Issue reminder via release notes/Slack; confirm no remaining opt-outs.
  - T: Remove legacy modules, bump major/minor version, update changelog.
- **Maintenance handover:**
  - Document dispatcher ownership in governance backlog, outlining code stewardship and release cadence.
  - Establish quality gates (coverage thresholds, lint rule compliance) that must pass before accepting new domain services.

## Success Metrics

- 100% of command/ query flows routed via the dispatcher.
- All domain services returning `FlextResult` with validated configs.
- Context correlation IDs present in 100% of logged events during acceptance tests.
- Removal or deprecation of legacy orchestration modules without consumer regressions.
- CI passing across ecosystem with new lint/type rules enabled.

## Risks & Mitigations

- **Adoption lag:** Provide hands-on support, clear migration guides, and phased cut-offs.
- **Tooling false positives:** Iterate quickly on lint/type rules using pilot feedback before broad enforcement.
- **Performance regressions:** Include performance benchmarks in CI for migrated services to catch regressions early.
- **Knowledge gaps:** Host workshops, record walkthrough videos, and keep documentation up to date.

## Governance

- Establish a weekly architecture sync to review progress, risks, and tooling updates.
- Maintain a shared backlog in issue tracker; require architecture sign-off for new services/commands.
- Schedule quarterly reviews to evaluate architecture health and adjust roadmap.

#### Governance Cadence & Responsibilities (2025-09-17)

- **Weekly architecture sync:** Review action status table, participant snapshot deltas, and dispatcher adoption metrics; rotate note-taker and publish minutes in modernization dashboard.
- **Backlog triage:** Core Platform owns dispatcher tasks; Developer Experience manages CLI deliverables; Data Connectors Guild tracks migration stories; Quality & Safeguards ensures test/lint items stay prioritised.
- **Metrics reporting:** Observability team to surface context/latency metrics; QA to report regression coverage; Product/Program to monitor release readiness.
- **Quarterly review:** Validate success metrics, reassess risks, and recalibrate roadmap, including potential expansion to non-FLEXT packages.
- **Communication:** Maintain single source of truth in modernization plan; update Loom/Slack threads after each milestone.

## Roadmap Status Snapshot (2025-09-17)

- Phase 0 baseline complete; action follow-ups in progress with charter and sequence flow drafted.
- Phase 1 design brief, pilot scope, validation strategy accepted for workshop review; initial `FlextDispatcher` facade implemented in flext-core.
- Phase 2 tooling backlog defined (docs, templates, linting, CI) targeting Week 4–5 completion.
- Phase 3 migration playbook sequenced; feature flag + rollback strategy documented.
- Phase 4 deprecation checklist prepared pending dispatcher adoption thresholds.
