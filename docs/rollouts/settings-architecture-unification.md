# Settings Architecture Unification — Cross‑Project Rollout

Status: Initiated (Core complete, subprojects in progress)
Authority: flext-core/docs/refactor/settings-architecture-unification-plan.md

## Goal

- Apply the flext-core unified Settings architecture (Pydantic v2.11) across all subprojects, preserving dicts at the borders and using models internally.
- Enforce flext-core standards: single top-level classes per module, extensive code reuse, and FlextResult in public operations.

## Core Principles (adopted)

- Layers: Constants → Settings (BaseSettings) → SystemConfigs (BaseModel) → Border (dict via `model_dump()`).
- Separate “Settings” (input) from “Configs” (system validation), bridged by `to_config()`.
- Use StrEnums from `FlextConstants` and Pydantic validators; no scattered manual checks.
- Dict compatibility only at the API border; internal traffic uses models.

## Current Status Snapshot

- flext-core: Phases 1–4 implemented; Phase 5 docs in `flext-core/docs/guides/configuration.md`.
- Subprojects: rollout started; see Tasks below.

## Rollout Tasks by Project

- flext-core (reference implementation)
  - Settings base, loader, registry, dynamic fields, and SystemConfigs complete
  - Action: None (used as reference)

- flext-web
  - Validate core env/log fields via `FlextModels.SystemConfigs.BaseSystemConfig` inside `configure_web_configs_system()` while preserving dict output
  - Next: consider adding `WebSettings(FlextConfig.Settings)` + `to_config()` mapping to `FlextWebConfigs.WebConfig` for full bridge

- flext-api
  - TODO: Add `ApiSettings(FlextConfig.Settings)` and map to existing API config model(s); update `configure_*` to use Settings → Configs → `model_dump()`

- flext-auth
  - TODO: Add `AuthSettings(FlextConfig.Settings)` bridging auth models; adopt in `configure_*` facades

- flext-ldap / flext-ldif
  - TODO: Identify `configure_*` façades or equivalent entry-points
  - TODO: Validate core env/log via `BaseSystemConfig` or create dedicated `*Settings` + `to_config()` if domain models exist

- flext-cli / targets (tap/target)
  - TODO: For any `configure_*` functions, validate core fields and migrate to Settings bridge with minimal disruption

- flext-db-oracle / flext-meltano / flext-grpc
  - TODO: Same pattern; validate core env/log via `BaseSystemConfig` and gradually introduce module‑specific `*Settings`

## Acceptance Criteria

- Every `configure_*` façade in subprojects validates env/log/validation using flext-core models (either `BaseSystemConfig` or dedicated `*Config`).
- Dicts remain at the border; internal validation/modeling uses Pydantic models.
- Single top-level class per module; reuse through helpers/factories as in flext-core.

## Execution Log

- 2025‑09‑07: Initiated rollout. Updated flext-web `configure_web_configs_system()` and `configure_web_services_system()` to validate core fields via `FlextModels.SystemConfigs.BaseSystemConfig` (keeps dict compatibility). Next: add `WebSettings` bridge.
- 2025‑09‑07: Applied LDAP exceptions configuration facade `FlextLDAPExceptions.configure_exceptions_system()` with core validation via `BaseSystemConfig` and derived defaults; output remains a dict for compatibility.
- 2025‑09‑07: Validated CLI core configuration via `FlextModels.SystemConfigs.BaseSystemConfig` in `FlextCliService.configure()`; preserves dict border, adds environment default.
- 2025‑09‑07: Added `flext_web.settings.FlextWebSettings` and wired `configure_web_configs_system()` to use full Settings → WebConfig bridge with backward-compatible fallback.
