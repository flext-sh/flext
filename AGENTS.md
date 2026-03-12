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

# AGENTS.md — Canonical Engineering Law

## §1 Identity

- FLEXT canonical governance file for all coding agents in this repository.
- Reviewed: 2026-02-22.
- Stack baseline: Python 3.13+, Pydantic v2, Ruff, Pyrefly, Poetry, Make.
- `AGENTS.md` defines mandatory law; skills hold detailed implementation guidance.
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

### 3.1 Architecture & Code Structure
- **MVI 200-LINE CAP (SUPREME LAW)**: Any module, class, method, or function >200 lines is a violation. Refactor immediately using strict OO composition and canonical MRO architecture. Decompose into explicit contracts and reusable domain components—never use compression hacks.
- **Pydantic v2 Mastery**: Every class MUST extend Pydantic v2 `BaseModel` (or FLEXT base models) via MRO. Fully utilize `Field()`, `model_config = ConfigDict(...)`, `PrivateAttr()`, and built-in constraints. Standalone `*Config` classes, unnecessary `@property`, manual `self._x` assignments, and line-reduction wrappers are FORBIDDEN.
- **MRO Inheritance Hierarchy**: Domain logic must reside in a single nested class hierarchy. Subprojects inherit from the parent project's facade class to cascade namespaces. Loose functions or standalone classes without MRO lineage are FORBIDDEN.
- **Centralize Polymorphic Code**: Dismantle polymorphic functions branching on type unions. Use centralized Pydantic v2 models with discriminated unions and validation.

### 3.2 Types & Contracts
- **Strict Contracts Only**: `Any`, bare `object`, and `dict[str, Any]` are TOTALLY FORBIDDEN across all code. Use `t.*` contracts exclusively (`t.Scalar`, `t.Container`, `t.ConfigMap`, etc.). Duplicate type definitions or compatibility aliases (`MyScalar = t.Scalar`) are FORBIDDEN. Use modern Python typing syntax (`X | Y`).
- **PEP 695 Canonical (Python 3.13+)**: ALL type aliases in `typings.py` must use `type X = ...` syntax. These create `TypeAliasType` objects—using them in `isinstance()` crashes at runtime and is FORBIDDEN. Runtime narrowing MUST use `u.Guards.is_*()` functions instead.
- **Type Narrowing**: NEVER use `type(x) is T` or `type(x) == T` to narrow types. Use `isinstance(x, T)` or `TypeGuard`. Avoid gratuitous narrowings for types that shouldn't exist. `cast()` is completely forbidden outside `flext-core` result internals.
- **Nullability and Unions**:
  - `| None` is ONLY permitted inline at usage sites when business semantics require it (e.g., "not configured"). Never bake it into aliases.
  - Inline composed type annotations (e.g., `str | int`) are FORBIDDEN in application code.
- **`t.Container` Exclusivity**: `type Container = Scalar | Path`. `BaseModel` is TOTALLY FORBIDDEN inside `t.Container`. If both are needed, use explicit `t.Container | BaseModel`.

### 3.3 Failures & Error Handling
- **`r[T]` for Fallible Operations**: Any function that can fail MUST return `r[T]`. `T | None`, bare exceptions, and ad-hoc error dicts are FORBIDDEN. The `r` alias is mandatory.
- **No Exceptions as Control Flow**: Bare `try/except` in business logic is FORBIDDEN when `r` composition (`map`/`flat_map`/`lash`) can handle the flow. Bare `except:` is universally forbidden. Catch explicit exceptions.

### 3.4 Tools, Modules & Environment
- **Imports Rules**:
  - `from __future__ import annotations` MUST be the first import in every Python module.
  - `typing.TYPE_CHECKING` is ALLOWED ONLY for type-only imports and `__init__.py` lazy loading, NEVER with Pydantic models. Autogenerated `__init__.py` files MUST preserve the lazy-export pattern.
  - `_LAZY_IMPORTS` string references MUST match real class names exactly.
  - Import parent components by CLASS NAME (e.g. `from flext_core.protocols import FlextProtocols`), never by assigned alias.
- **Command & Output Abstractions**: Bare `subprocess` calls, `sys.exit` outside `__main__.py`, direct `dependency_injector` wiring, and `print()` in production are FORBIDDEN. Use provided abstractions and `FlextLogger`.
- **Zero Hacks**: `model_rebuild()`, `exec()`, `eval()`, direct architectural `getattr()`, inline imports, and fallback `try/except ImportError` blocks are TOTALLY FORBIDDEN.

### 3.5 Integrity & Change Management
- **Context Evaluation**: Read and fully understand existing code, MRO chains, and base classes BEFORE changing code. Maximize reuse. Simplifications, TODOs, mocks, and stubs are FORBIDDEN.
- **AST-Grep Required**: Structural code changes/renames across the codebase MUST use `ast-grep` (`sg`). Ad-hoc python/shell scripts, `sed`, and `awk` for code transformations are TOTALLY FORBIDDEN.
- **Integral Changes**: After any type, model, or signature change, you MUST update all references across all 33 projects to maintain global consistency.
- **Tests Are Not Exempt**: Tests MUST demonstrate the exact same strict typing, Pydantic v2, `r`, and architectural discipline as production code. NO "test-only" relaxation.
- **Linter Zero Tolerance**: Code must pass ALL 4 linters (ruff, mypy, pyright, pyrefly) with ZERO errors/warnings. Suppressions (`# type: ignore`) are FORBIDDEN unless accompanied by a verifiable technical explanation and business necessity, restricted to a single line.
- **Evidence Required**: Never claim checks passed without executable evidence.
- **Stay In Scope**: Execute ONLY the assigned task. Out-of-scope cleanups or "obvious improvements" are FORBIDDEN. If found, file a new `beads` issue.
- **Legacy Extermination**: Legacy maintenance, non-business validation fallbacks, compatibility wrappers (`def old(): return new()`), and deprecation shims are ABOMINABLE. Delete and replace immediately. Fix forward.
- **Git is IMMUTABLE**: Rolling back is FORBIDDEN. `git checkout <file>`, `git reset`, `git revert`, and `git stash pop/apply` to OVERWRITE/DISCARD work is forbidden. Fix issues forward.

### 3.6 Associated Skills
- **Type Law & Result Patterns**: `flext-strict-typing`
- **Result/Logging/DI Patterns**: `flext-patterns`

## §4 Import Law

- Canonical alias imports are mandatory at usage sites: `r,t,c,m,p,u,d,e,h,s,x`. You only ever import the local facade explicitly; parent facades are inherited seamlessly.
- **Dependency Order**: Future, stdlib, third-party, first-party, local.
- **`flext-core` Imports**: Import concrete submodules (`flext_core.<module>`), NOT the package root.
- **Subproject Imports**: Consume public API/facade exports; NEVER import private `_` internals.
- **Forced Patterns**: Wildcard imports and relative imports are FORBIDDEN in governed code.
- **Aliases**: No double-assignment of facade aliases (`c/m/p/t/u` are assigned once at module bottom).
- **Direction**: Cross-tier imports violating architecture direction are FORBIDDEN.
- *Detailed matrix & exceptions*: See skill `flext-import-rules`.

## §5 Make Contract

- **Primary Entrypoint**: Automation entrypoint is always `make`. Raw scripts are implementation details.
- **Workspace Verbs**: `setup check security format docs test validate typings clean`.
- **Project Verbs** (`base.mk`): `setup check security format docs test validate clean`.
- **Selectors**: `PROJECT`, `PROJECTS`, `CHECK_GATES`, `VALIDATE_GATES`, `PYTEST_ARGS`, `FIX`, `JOBS`, `FAIL_FAST`.
- **Scope Controls** (Workspace): `VALIDATE_SCOPE=project|workspace`, optional `DEPS_REPORT=0`.
- **No Bypasses**: Strictness is mandatory. `SKIP_*` bypass toggles in the contract are FORBIDDEN.
- **Exit Codes**: `0` pass, `1` policy failure, `2` usage/config error, `3` infra/runtime error.
- **Validation**: Policy/automation edits MUST run `make validate VALIDATE_SCOPE=workspace` before claiming completion.
- **Reports**: Must be factual, machine-readable when produced, and include explicit executable next actions.
- *Verb semantics & thresholds*: See skill `flext-quality-gates`.

## §6 Quality Gates

- **Environments**: Workspace `.venv` is mandatory. System Python/pip usage is FORBIDDEN. Project-local `.venv` is fallback-only when workspace `.venv` is missing.
- **Preflight**: Before workspace loops, ensure root `.venv` exists and remove project `.venv` drift. In fallback mode, run `make setup` before loops.
- **`pyproject.toml`**: `make setup` and `make upgrade` must modernize/format before lock/install. Files must follow Poetry 2.x + PEP 621/639 constraints.
- **Coverage**: Source of truth is purely `[tool.coverage.report] fail_under` in each project's `pyproject.toml`. No Makefile constants, no `--cov-fail-under` flags.
- **No Silent Failures**: Constructs like `2>/dev/null` or `|| true` on mandatory gates are FORBIDDEN.
- *Gate details & matrix*: See skill `flext-quality-gates`.

## §7 Skill System

- **Authority**: Skills are authoritative detail documents. This file (`AGENTS.md`) is the supreme law surface framing them.
- **Load Order**: Touched-path `rules-*` skill first, supporting skills second. Afterwards, load only minimal skills needed for the change.
- **Mandatory Usage**: Do not implement rules from memory. Do not claim skill usage without reading the `SKILL.md`.
- **Mapping**: Baseline maps must be respected (`flext-core->rules-flext-core`, `src->rules-src`, `tests->rules-tests`, etc.).
- **Rule Definitions**: `rules.yml` schema uses flat fix keys only. Prefer `type: ast-grep`; use `type: custom` only when AST matching is completely unviable. `fix_auto: true` must map to an executable real fix mechanism.
- *Skill format policies*: See skills `skill-format-universal`, `flext-docs-pointer-policy`.

## §8 Change Management

- **Policy Workflow**: Policy changes land in `AGENTS.md` first, then propagate to skill documents.
- **Complete Work**: Never ship incomplete work as complete. Each claim REQUIRES command evidence. Changes must be minimal, explicit, root-cause oriented, and verifiable.
- **No Unapproved Bypass**: Altering lint/gate semantics or deferring/skipping a violation is FORBIDDEN without explicit in-session user approval.
- **Correct Governance**: If governance corrections arise during work, update this file immediately before further implementation.
- **Commit-After-Validation**: Every passing validation MUST be immediately accompanied by a `git add -A` → `git commit` → `git pull --rebase` → `git push` sequence. Uncommitted or unpushed work is LOST WORK.

## §9 Agent Execution Pre-requisites

- **Verify Before Implement**: Check recent commits (`git log --oneline -20`) and active task trackers to prevent duplication. Cross-session deduplication is critical.
- **Scope Discipline**: DO NOT modify files outside the specific task boundary. If blocked, escalate instead of silently rewriting external dependencies.
- **Scale and Parallelism**: Refactoring many call sites or modules across the portfolio should utilize multiple batched passes to retain focus and verifiability.
- **`.new/.old` Swap Protocol**: For massive file modifications (>50 lines changed), create a `.new` file, verify changes, then execute `mv file.py file.py.old && mv file.py.new file.py`. Commit both in one transaction.

### 9.1 Coding Directives for Agents
- **Runtime Aliases**: Subprojects MUST use their own namespace aliases ONLY (e.g., `x` for FlextMixins / runtime helpers: `x.ok`, `x.is_base_model`, etc.). Do NOT subdivide namespaces or introduce extra wrapper layers.
- **No Loose Aliases**: Remove compatibility aliases entirely.
- **Narrowing Enforced**: No `type(x) == T`. Use `isinstance(x, T)` or `TypeGuard` properly. Prefer Pydantic validation functions where structured data is involved.
- **Evidence Requirement**: "Tests pass", "linters clean" claims MUST include command output proof (with exit code and UTC timestamp) so the audit logic can replay the claim. Store evidence in `.sisyphus/evidence/`.

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
| `context.py`, `settings.py`, `models.py`, `utilities.py`, `_utilities/*`, `__version__.py` | ❄️ FROZEN | No agent modifies |

**AXIOMATIC Exception**: FROZEN files are unfrozen for annotation-only changes required by AXIOMATIC rules (§3 Code Law). Type annotations, Field() metadata, PrivateAttr declarations, and import additions are permitted. Behavioral changes (logic, algorithms, control flow) remain FROZEN.

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

- **Phase 0 (SOLO)**: Agent 4 completes Wave 0 (RuntimeResult.**slots** + r.fail() + p.Result) and PUSHES. ALL other agents BLOCKED until Phase 0 complete.
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
- **Never rollback**: NO `git revert`, NO `git reset`, NO `git checkout <file>` to discard work, NO `git stash pop` to overwrite committed changes. Fix forward ONLY. If you break something, push a fix commit. Every change by every agent is accepted, improved, and fixed forward — never discarded.
- **Conflict resolution**: If conflict in YOUR file → resolve manually. If conflict in ANOTHER agent's file → `git checkout --theirs <file>` (accept their version, work around it).
- **Commit frequency**: Every task completion = separate commit. Small commits, frequent pushes.
- **AXIOMATIC Commit-After-Validation**: Immediately after ANY validation passes (linters, tests, `make check`, or any quality gate), the agent MUST commit ALL pending changes across ALL touched projects and push — without delay, without waiting for the next task, without asking permission. The sequence is MANDATORY and NON-NEGOTIABLE: (1) validation passes → (2) `git add -A` in every project with pending changes → (3) `git commit -m "<conventional message>"` → (4) `git pull --rebase` → (5) `git push` → (6) verify `git status` shows clean. This applies to ALL agents, ALL sessions, ALL projects simultaneously. Pending uncommitted work after a passing validation is a VIOLATION. Work that exists only locally and has not been pushed is LOST WORK — it does not exist. There is no "I'll commit later". There is no "commit at the end". Every stable state MUST be immediately persisted to remote.

### §10.6 Plan and Session Hygiene

- **Plan hygiene**: Consolidate overlapping plans before creating new ones. Check `.sisyphus/plans/` for existing plans covering the same scope. Merge tasks into existing plan rather than creating duplicates.
- **Cross-session deduplication protocol**: Before spawning new agents, verify no other agent is working on the same task. Use `git log --oneline -20` and check `.sisyphus/plans/` for active work. If found, coordinate or defer.
