<!-- TOC START -->

- [§1 Identity](#1-identity)
- [§2 Architecture Law](#2-architecture-law)
- [§3 Code Law](#3-code-law)
- [§4 Import Law](#4-import-law)
- [§5 Make Contract](#5-make-contract)
- [§6 Quality Gates](#6-quality-gates)
- [§7 Skill System](#7-skill-system)
- [§8 Change Management](#8-change-management)
- [§9 Agent Instructions](#9-agent-instructions-mandatory-for-all-coding-agents)
- [§10 Multi-Agent Parallel Execution Law](#10-multi-agent-parallel-execution-law-mandatory)

<!-- TOC END -->

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
- Namespace aliases are canonical public API surfaces: `m`, `c`, `t`, `u`, `p`, `r`, `d`, `e`, `h`, `s`, `x`. Use simple runtime aliases only (e.g. `c = FlextConstants`, `m = FlextModels` in **init**).
- Cross-project composition MUST use inheritance via MRO across all components symmetrically (`Protocols`, `Models`, `Types`, `Utilities`, `Constants`). Subprojects define exactly ONE internal namespace class and transparently gain access to all parent namespaces via MRO.
- Integration projects (`tap|target|dbt`) MUST compose one platform and one domain via inheritance (e.g., `FlextMeltanoProtocols` + `FlextLdapProtocols`). The integration class name MUST NOT contain the "Meltano" prefix (e.g. `FlextTapLdapProtocols`).
- Domain boundaries are strict: `oracle-wms != db-oracle`, `ldap != ldif`.
- Each public facade module defines exactly one primary facade class plus one canonical alias.
- No backward-compat alias layers (`LegacyX = NewX`) and no namespace shadowing. You must never re-assign parent aliases.
- `__init__.py` files are exports-only: type hints, `__all__`, and native `__getattr__` module-level lazy load strategy.
- For architecture details and composition matrix -> see skill: `flext-architecture-layers`.
- For namespace inheritance and anti-patterns -> see skill: `flext-patterns`.
- For path-level architectural enforcement -> see skills: `rules-flext-core`, `rules-src`.
- Per-tier inheritance lookup table: see skill `flext-architecture-layers` for complete MRO matrix and composition rules by layer.
- L1 Platform Chains: Core→Cli→Meltano→Integration (orchestration), Core→Web→Api→Auth (API layer). Each chain defines clear ownership and composition boundaries.
- Clarification: "exactly ONE internal namespace class" refers to LOCAL namespace class per subproject, not single inheritance. Parent namespaces are accessed transparently via MRO.
- Integration naming: `Flext<Role><Domain><Facade>` pattern (NOT `FlextMeltano<Role>...`). Role is platform (Tap, Target, Dbt), Domain is connector (Ldap, Oracle, Wms), Facade is contract type (Protocols, Models, Types, etc.).

## §3 Code Law

- **NEW** Fallible operations MUST use `FlextResult` (`r[T].ok(...)` / `r.fail(...)`), never ad-hoc dict envelopes.
- **NEW** `sys.exit` is forbidden outside `__main__.py` entrypoint boundaries.
- **NEW** Bare subprocess calls are forbidden; use standardized command runner abstractions.
- **NEW** `typing.TYPE_CHECKING` is ALLOWED for type-only imports (IDE support, annotations not needed at runtime) and `__init__.py` lazy loading. `TYPE_CHECKING` is FORBIDDEN with Pydantic models (BaseModel subclasses need runtime access) and as a band-aid for circular imports (fix architecture instead). See `flext-import-rules` Rule 8 for full details and examples.
- **NEW** **Zero Tolerance for Hacks**: `model_rebuild()`, `eval()`, `exec()`, architectural `getattr()`, inline imports, lazy generic imports, and `try/except ImportError` blocks are TOTALLY FORBIDDEN without exception.
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
- **Type narrowing**: use `isinstance` or `TypeGuard` only; `type(x) is T` for narrowing is forbidden. `cast()` is completely forbidden outside of `flext-core` result internals.
- **Polymorphic code**: dismantle into centralized Pydantic v2 models (single contract, validation in model).
- For result/logging/DI coding patterns -> see skill: `flext-patterns`.
- `from __future__ import annotations` verification: MUST be present as first import in every Python module (after docstring/license). Verify with: `grep -n 'from __future__ import annotations' <file>`.
- `model_rebuild()` is FORBIDDEN (explicit prohibition). Use Pydantic v2 patterns instead; if you think you need it, fix the model definition or import order instead.
- `_LAZY_IMPORTS` string references MUST match actual class names exactly. Mismatch between string and runtime class causes silent failures.
- Import parent by CLASS NAME for inheritance, never by alias. Example: `from flext_core.protocols import FlextProtocols` (correct), NOT `from flext_core import p` then inherit from `p.FlextProtocols` (wrong).

## §4 Import Law

- Canonical alias imports are mandatory at usage sites: `r,t,c,m,p,u,d,e,h,s,x`. You only ever import the local facade explicitly; parent facades are inherited seamlessly.
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
- **Evidence requirements**  
  Every verification claim ("tests pass", "linters clean", "grep found X") MUST include command output proof. Store evidence in `.sisyphus/evidence/` with timestamp and command used.
- **Cross-session deduplication**  
  Check recent commits for already-completed work before starting. Use: `git log --oneline --all --grep='<task-keyword>'` to find prior work. If found, verify completion and skip.
- **.new/swap protocol**  
  For large file modifications (>50 lines changed), create `.new` file first, verify all changes, then swap: `mv file.py file.py.old && mv file.py.new file.py`. Commit both the new file and the swap in one commit.
- **Verify-before-implement**  
  Before starting ANY task, check recent commits: `git log --oneline -5` and `git show HEAD`. Verify the task is not already complete or in-progress by another agent.
- **Scope discipline**  
  Agent MUST NOT modify files outside task boundary. If a task requires changes to a file owned by another agent, STOP and escalate. READ-ONLY access is allowed; WRITE access is forbidden.

## §10 Multi-Agent Parallel Execution Law (Mandatory)

### §10.1 User's 11 Commandments (The Execution Ritual)

These are UNBREAKABLE LAW for all parallel agent work:

1. **Organize libs first** — Domain monopoly: each module owns its domain exclusively
2. **Minimal skeleton** — Start with interfaces/protocols, optimize structure before implementation
3. **Reconnect one-by-one** — Fix ONE integration at a time, verify before next
4. **Tests last per module** — Update tests AFTER implementation passes static checks
5. **4 linters zero tolerance** — ruff, mypy, pyright, pyrefly MUST all pass, no `# type: ignore`
6. **Stay in lane** — Only touch files in your ownership, READ-ONLY for others
7. **Never rollback** — Fix forward only, no `git revert`, no deprecation shims
8. **Commit frequently** — Every task completion = separate commit + push
9. **.new/.old owned-only** — Use .new/.old pattern ONLY for files you own exclusively
10. **No automation scripts** — Manual changes only, no shell scripts for mass edits
11. **Never rush/ULW** — No ultrawork mode, no batching, perfection over speed

### §10.2 File Ownership Table (flext-core)

Use EXACTLY this ownership matrix:

| File | Owner | Others Allowed |
|------|-------|----------------|
| `dispatcher.py` | Agent 1 | READ only |
| `constants.py` | Agent 1 | READ only |
| `_models/cqrs.py` | Agent 1 | READ only |
| `registry.py` | Agent 2 | READ only |
| `typings.py` | Agent 2 | READ only |
| `service.py` | Agent 3 | READ only |
| `_models/base.py` | Agent 3 | READ only |
| `result.py` | Agent 4 | READ only |
| `exceptions.py` | Agent 4 | READ only (exception: Agent 4 may modify exceptions.py in ANY consumer project for e.BaseError hierarchy) |
| `runtime.py` | Agent 4 | Agent 5 READ only (MRO chain reference) |
| `loggings.py` | Agent 4 | READ only |
| `container.py` | Agent 5 (primary) | Agent 1: dispatcher singleton ADD only; Agent 4: return types only |
| `decorators.py` | Agent 5 | READ only |
| `handlers.py` | Agent 5 | READ only |
| `mixins.py` | Agent 5 | READ only |
| `protocols.py` | SECTION-OWNED (see matrix below) | Each agent: own section ONLY, append at END, NEVER reorder, NEVER auto-format globally |
| `__init__.py` | ❄️ FROZEN | Each agent appends own new exports only |
| `context.py`, `settings.py`, `models.py`, `utilities.py`, `_utilities/*`, `_runtime_metadata.py`, `__version__.py` | ❄️ FROZEN | No agent modifies |

**protocols.py Section Ownership Matrix**:

| Section | A1 (Dispatcher) | A2 (Registry) | A3 (Service) | A4 (Result/Exceptions) | A5 (CDH/Mixins) |
|---------|-----------------|---------------|--------------|------------------------|-----------------|
| L1-236 (infra) | ❄️ | ❄️ | ❄️ | ❄️ | ❄️ |
| Context, RuntimeBootstrapOptions, DI | — | — | — | — | ✅ |
| Result, ResultLike | — | — | — | ✅ | — |
| Model, Config, Service, Validation | — | — | ✅ | — | — |
| CommandBus, Middleware, Processor | ✅ | — | — | — | — |
| Handler | — | — | — | — | ✅ |
| Registry | — | ✅ | — | — | — |
| VariadicCallable, ResourceFactory | — | — | — | ✅ | — |
| RegisterableService, ServiceFactory | — | — | — | — | ✅ |
| Log, StructlogLogger, Metadata | — | — | — | ✅ | — |
| ValidatorSpec | — | — | ✅ | — | — |
| L1289+ (metaclass infra) | ❄️ | ❄️ | ❄️ | ❄️ | ❄️ |
| ALL other sections | ❄️ | ❄️ | ❄️ | ❄️ | ❄️ |

### §10.3 Execution Phases (Dependency-Ordered)

Agents MUST execute in this order:

- **Phase 0 (SOLO)**: Agent 4 completes Wave 0 (RuntimeResult.**slots** + FlextResult.fail() + p.Result) and PUSHES. ALL other agents BLOCKED until Phase 0 complete.
- **Phase 1**: Agent 4 continues (exception propagation, safe(), chaining) + Agent 5 starts (containers/decorators/handlers/mixins). Agent 5 must `git pull --rebase` before starting.
- **Phase 2**: Agent 1 (Dispatcher) + Agent 3 (Service) start. Both must `git pull --rebase` before starting.
- **Phase 3**: Agent 2 (Registry) starts. Must `git pull --rebase` before starting.
- **Phase 4 (Consumer Projects)**: All agents work on their assigned consumer projects IN PARALLEL.

**Consumer Project Partition (31 projects, zero overlap)**:

| Agent | Projects | Count |
|-------|----------|-------|
| Agent 1 | `algar-oud-mig`, `flexcore`, `flext-api` | 3 |
| Agent 2 | `flext-auth`, `flext-cli`, `flext-db-oracle` | 3 |
| Agent 3 | `flext-grpc`, `flext-ldap`, `flext-ldif`, `flext-meltano` | 4 |
| Agent 4 | `flext-observability`, `flext-oracle-oic`, `flext-oracle-wms`, `flext-plugin`, `flext-quality`, `flext-tap-oracle-wms`, `flext-target-ldif` | 7 |
| Agent 5 | `flext-tap-ldap`, `flext-tap-ldif`, `flext-tap-oracle`, `flext-tap-oracle-oic`, `flext-target-ldap`, `flext-target-oracle`, `flext-target-oracle-oic`, `flext-target-oracle-wms`, `flext-web`, `flext-dbt-ldap`, `flext-dbt-ldif`, `flext-dbt-oracle`, `flext-dbt-oracle-wms`, `gruponos-meltano-native` | 14 |

### §10.4 Lint Scoping

- **During parallel work**: Each agent runs linters (ruff, mypy, pyright, pyrefly) ONLY on files they modified
- **At phase boundaries**: Agent completing a phase runs FULL project lint (`cd flext-core && make check`) before pushing
- **Before Phase 4**: ALL agents run full flext-core lint and verify ZERO errors before touching consumer projects
- **Zero tolerance**: NO `# type: ignore`, NO warnings, NO errors. Fix until clean.

### §10.5 Git Discipline

- **Always rebase**: `git pull --rebase` before EVERY push. NEVER `git pull` without `--rebase`.
- **Never force push**: NEVER `git push --force` to main/master.
- **Never rollback**: NO `git revert`. Fix forward only. If you break something, push a fix commit.
- **Conflict resolution**: If conflict in YOUR file → resolve manually. If conflict in ANOTHER agent's file → `git checkout --theirs <file>` (accept their version, work around it).
- **Commit frequency**: Every task completion = separate commit. Small commits, frequent pushes.

### §10.6 Plan and Session Hygiene

- **Plan hygiene**: Consolidate overlapping plans before creating new ones. Check `.sisyphus/plans/` for existing plans covering the same scope. Merge tasks into existing plan rather than creating duplicates.
- **Cross-session deduplication protocol**: Before spawning new agents, verify no other agent is working on the same task. Use `git log --oneline -20` and check `.sisyphus/plans/` for active work. If found, coordinate or defer.
