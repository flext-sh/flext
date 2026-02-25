---
description: 
alwaysApply: true
---

# CLAUDE.md — Canonical Engineering Law

## §1 Identity

- FLEXT canonical governance file for all coding agents in this repository.
- Reviewed: 2026-02-22.
- Stack baseline: Python 3.13+, Pydantic v2, Ruff, Pyrefly, Poetry, Make.
- `CLAUDE.md` defines mandatory law; skills hold detailed implementation guidance.
- Agent-specific configs are pointers only; no policy duplication outside this file.

## §2 Architecture Law

- Dependency flow is inward only: `L3 -> L2 -> L1 -> L0`; reverse imports are forbidden.
- Layer ownership: `L3` orchestration, `L2` domain/infrastructure, `L1` foundation/bridge, `L0` contracts.
- Bridge external infra through runtime/container boundaries, not direct framework imports.
- Public contracts must be consumed from package facades and root exports.
- Namespace aliases are canonical public API surfaces: `m`, `c`, `t`, `u`, `p`, `r`, `d`, `e`, `h`, `s`, `x`. Use simple runtime aliases only (e.g. `c = FlextConstants`, `m = FlextModels` in **init**). Do not use FlextRuntime.Aliases or any alias registry; MRO protocol only.
- Cross-project composition must use inheritance via MRO, never assignment mirroring or alias duplication. Subprojects expose flat namespace via class-level aliases on the facade (e.g. `ExecuteResult = TargetOracle.ExecuteResult` so usage is `m.ExecuteResult`).
- Integration projects (`tap|target|dbt`) must include `FlextMeltano*` plus the correct domain mixin.
- Domain boundaries are strict: `oracle-wms != db-oracle`, `ldap != ldif`.
- Each public facade module defines exactly one primary facade class plus one canonical alias.
- No backward-compat alias layers (`LegacyX = NewX`) and no namespace shadowing.
- `__init__.py` files are exports-only: imports/re-exports and `__all__`, no runtime logic.
- For architecture details and composition matrix -> see skill: `flext-architecture-layers`.
- For namespace inheritance and anti-patterns -> see skill: `flext-patterns`.
- For path-level architectural enforcement -> see skills: `rules-flext-core`, `rules-src`.

## §3 Code Law

- **NEW** Fallible operations MUST use `FlextResult` (`r[T].ok(...)` / `r.fail(...)`), never ad-hoc dict envelopes.
- **NEW** `sys.exit` is forbidden outside `__main__.py` entrypoint boundaries.
- **NEW** Bare subprocess calls are forbidden; use standardized command runner abstractions.
- **NEW** `typing.TYPE_CHECKING` blocks are forbidden; resolve layering via protocols/architecture.
- **NEW** `print()` is forbidden in production paths; use structured logging with `FlextLogger`/structlog.
- `from __future__ import annotations` is mandatory in Python modules.
- Bare `except:` is forbidden; catch explicit exceptions and preserve typed failure boundaries.
- Direct `structlog.get_logger()` usage is forbidden where `FlextLogger` wrappers exist.
- Direct `dependency_injector` wiring in domain/orchestration code is forbidden; use runtime/container bridges.
- Keep contracts typed and explicit; avoid `Any`/`object` when a `t.*` contract exists.
- Use modern Python typing syntax (`X | Y`, built-in generics, `collections.abc` contracts).
- Use Pydantic v2 patterns (`ConfigDict`, `Field`, validators) for model state and validation.
- Root-cause fixes only: no bypasses, no hidden suppressions, no fake-green reports.
- Never claim checks passed without executable evidence.
- For typing law and `FlextResult` details -> see skill: `flext-strict-typing`.
- **Type narrowing**: use `isinstance` or `TypeGuard` only; `type(x) is T` for narrowing is forbidden.
- **Polymorphic code**: dismantle into centralized Pydantic v2 models (single contract, validation in model).
- For result/logging/DI coding patterns -> see skill: `flext-patterns`.

## §4 Import Law

- Canonical alias imports are mandatory at usage sites: `r,t,c,m,p,u,d,e,h,s,x`.
- Keep import order: future, stdlib, third-party, first-party, local.
- Within `flext-core`, import concrete submodules (`flext_core.<module>`) not package root.
- From subprojects, consume public API/facade exports; never import private `_` internals.
- Wildcard imports and relative imports are forbidden in governed code.
- No double-assignment of facade aliases (`c/m/p/t/u` assigned once at module bottom).
- Cross-tier imports violating architecture direction are forbidden.
- For full import matrix, exceptions, and enforcement checks -> see skill: `flext-import-rules`.

## §5 Make Contract

- Automation entrypoint is `make`; scripts are implementation details, not primary UX.
- Workspace verbs: `setup check security format docs test validate typings clean`.
- Project verbs (`base.mk`): `setup check security format docs test validate clean`.
- Standard selectors: `PROJECT`, `PROJECTS`, `CHECK_GATES`, `VALIDATE_GATES`, `PYTEST_ARGS`, `FIX`, `JOBS`, `FAIL_FAST`.
- Workspace-only scope controls: `VALIDATE_SCOPE=project|workspace`, optional `DEPS_REPORT=0`.
- Strictness is mandatory: no `SKIP_*` bypass toggles in the contract.
- Exit code contract: `0` pass, `1` policy failure, `2` usage/config error, `3` infra/runtime error.
- Policy/automation/governance edits must run `make validate VALIDATE_SCOPE=workspace` before completion claims.
- Reports must be factual, machine-readable when produced, and include executable next actions for failures.
- For complete verb semantics and thresholds -> see skill: `flext-quality-gates`.

## §6 Quality Gates

- Workspace `.venv` is mandatory when present; system Python/pip usage is forbidden.
- Project-local `.venv` is fallback-only for project-scoped runs when workspace `.venv` is missing.
- Preflight before workspace loops: ensure root `.venv` exists and remove project `.venv` drift.
- In fallback mode, run project `make setup` before check/validate/test loops.
- `make setup` and `make upgrade` must modernize/format `pyproject.toml` before lock/install.
- `pyproject.toml` must follow Poetry 2.x + PEP 621/639 constraints.
- Coverage source of truth is `[tool.coverage.report] fail_under` in each project `pyproject.toml`.
- Forbidden threshold drift: no Makefile threshold constants and no `--cov-fail-under` flags in pytest addopts.
- No silent failure patterns (`2>/dev/null`, `|| true`) on mandatory gates.
- For gate details and verification matrix -> see skill: `flext-quality-gates`.

## §7 Skill System

- Skills are authoritative detail documents; this file is the law surface.
- Load order is mandatory: touched-path `rules-*` skill first, supporting skills second.
- Do not implement from memory when a relevant skill exists.
- Do not claim skill usage without reading the corresponding `SKILL.md`.
- `rules.yml` schema uses flat fix keys only (`fix_auto`, `fix_type`, `fix_file`, `fix_script`, `fix_instruction`, `fix_description`).
- Prefer `type: ast-grep`; use `type: custom` only when AST matching is not viable.
- `fix_auto: true` must point to an executable, real fix mechanism.
- Mandatory mapping baseline: `flext-core->rules-flext-core`, `src->rules-src`, `docs->rules-docs`, `scripts->rules-scripts`, `typings->rules-typings`, `.github->rules-github`, `docker->rules-docker`, `pkg->rules-pkg`, `cmd->rules-cmd`, `examples->rules-examples`.
- After rules skill, load only minimal supporting skills needed for the change.
- For skill format and pointer governance -> see skills: `skill-format-universal`, `flext-docs-pointer-policy`.

## §8 Change Management

- Policy changes land in `CLAUDE.md` first, then propagate to skill documents.
- Never ship incomplete work as complete; each claim requires command evidence.
- Keep changes minimal, explicit, root-cause oriented, and verifiable.
- Never alter lint/gate semantics without explicit in-session user approval.
- If governance corrections arise during work, update this file immediately before further implementation.
- **CRITICAL** Deferring, skipping, or exempting any known violation is forbidden without explicit operator authorization in-session. Hiding scope exclusions inside plans or guardrails without operator approval is an extreme fault. When a violation cannot be fixed immediately, the agent must present the violation, explain why, and obtain explicit written approval before marking it deferred.

## §9 Agent Instructions (Mandatory for All Coding Agents)

- **Runtime aliases (subprojects)**  
  In subprojects, all runtime access MUST use the project namespace only. Use the canonical runtime alias `x` (FlextMixins) for runtime helpers: `x.create_instance`, `x.is_dict_like`, `x.is_list_like`, `x.is_valid_json`, `x.is_valid_identifier`, `x.is_base_model`, `x.normalize_to_general_value`, `x.normalize_to_metadata_value`, `x.is_sequence_type`, `x.safe_get_attribute`, `x.extract_generic_args`, `x.ok`, `x.fail`. Do NOT subdivide namespaces (e.g. avoid `FlextRuntime.Bootstrap.*` or ad-hoc wrappers). Subprojects MUST NOT introduce extra alias layers; use `c`, `m`, `t`, `u`, `p`, `r`, `d`, `e`, `h`, `s`, `x` from the project/facade exports only.

- **No loose aliases or pass-through methods**  
  Remove compatibility aliases (e.g. `LegacyX = NewX`, `.data` for `.value`, `.and_then` for `.flat_map`). Use direct methods and single canonical names. No free-function wrappers that only call a class method; call the class/method directly.

- **Type narrowing (strict)**  
  Use correct typing for type narrowing. Do NOT use `type(x) is T` or `type(x) == T` for narrowing; use `isinstance(x, T)` or `TypeGuard` so the type checker can narrow. Replacing `isinstance` with `type()` is forbidden. Prefer Pydantic `model_validate` / `model_validate_json` for input validation and structured data.

- **Polymorphic code → centralized Pydantic models**  
  Dismantle polymorphic functions and methods: replace multiple branches on type/union with a single contract. Use centralized Pydantic v2 models with validation (discriminated unions, `Field`, `model_validator`, `field_validator`) so that one model (or a small set of models) defines the shape and validation; avoid ad-hoc `if isinstance(...)` chains over many types. Prefer overloads or discriminated unions over loose `Union` handling in function bodies.

- **Scale and parallelism**  
  When refactoring many call sites or modules, use multiple agents or batch passes in parallel (e.g. by package or by rule) to apply these rules consistently and quickly. Each change must remain minimal and verifiable.

- **Skill (mandatory)**  
  For detailed enforcement: see skill **flext-agent-strict-rules** (runtime aliases only, no type() for narrowing, no loose methods, polymorphic code → centralized Pydantic v2 models).
