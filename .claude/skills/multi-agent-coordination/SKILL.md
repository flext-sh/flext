---
name: multi-agent-coordination
description: Quick reference for 5 agents executing parallel work on flext codebase with zero conflicts. Authoritative source CLAUDE.md §10.
---

# Multi-Agent Coordination

**Category**: Governance  
**Status**: Active  
**Agent Scope**: All 5 parallel agents  
**Authoritative Source**: CLAUDE.md §10 Multi-Agent Parallel Execution Law

## Purpose

Quick reference for 5 agents executing parallel work on flext codebase with zero conflicts. Load this skill when working on flext-core or consumer projects in parallel with other agents.

## The 11 Commandments (Unbreakable Law)

1. **Organize libs first** — Domain monopoly: each module owns its domain exclusively
2. **Minimal skeleton** — Start with interfaces/protocols, optimize structure before implementation
3. **Reconnect one-by-one** — Fix ONE integration at a time, verify before next
4. **Tests last per module** — Update tests AFTER implementation passes static checks
5. **4 linters zero tolerance** — ruff, mypy, pyright, pyrefly MUST all pass, no `# type: ignore`
6. **Stay in lane** — Only touch files in your ownership, READ-ONLY for others
#NP|7. **Never rollback — AXIOMATIC** — Fix forward ONLY. `git revert`, `git reset`, `git checkout <file>`, `git stash pop/apply` to discard any agent's work are TOTALLY FORBIDDEN. Every change by every agent is accepted, improved, and fixed forward. Violation = extreme fault.
8. **Commit frequently** — Every task completion = separate commit + push
9. **.new/.old owned-only** — Use .new/.old pattern ONLY for files you own exclusively
10. **No automation scripts** — Manual changes only, no shell scripts for mass edits
11. **Never rush/ULW** — No ultrawork mode, no batching, perfection over speed

## File Ownership Matrix (flext-core)

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

## protocols.py Section Ownership Matrix

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

## Execution Phases (Dependency-Ordered)

Agents MUST execute in this order:

- **Phase 0 (SOLO)**: Agent 4 completes Wave 0 (RuntimeResult.**slots** + FlextResult.fail() + p.Result) and PUSHES. ALL other agents BLOCKED until Phase 0 complete.
- **Phase 1**: Agent 4 continues (exception propagation, safe(), chaining) + Agent 5 starts (containers/decorators/handlers/mixins). Agent 5 must `git pull --rebase` before starting.
- **Phase 2**: Agent 1 (Dispatcher) + Agent 3 (Service) start. Both must `git pull --rebase` before starting.
- **Phase 3**: Agent 2 (Registry) starts. Must `git pull --rebase` before starting.
- **Phase 4 (Consumer Projects)**: All agents work on their assigned consumer projects IN PARALLEL.

## Consumer Project Partition (31 projects, zero overlap)

| Agent | Projects | Count |
|-------|----------|-------|
| Agent 1 | `algar-oud-mig`, `flexcore`, `flext-api` | 3 |
| Agent 2 | `flext-auth`, `flext-cli`, `flext-db-oracle` | 3 |
| Agent 3 | `flext-grpc`, `flext-ldap`, `flext-ldif`, `flext-meltano` | 4 |
| Agent 4 | `flext-observability`, `flext-oracle-oic`, `flext-oracle-wms`, `flext-plugin`, `flext-quality`, `flext-tap-oracle-wms`, `flext-target-ldif` | 7 |
| Agent 5 | `flext-tap-ldap`, `flext-tap-ldif`, `flext-tap-oracle`, `flext-tap-oracle-oic`, `flext-target-ldap`, `flext-target-oracle`, `flext-target-oracle-oic`, `flext-target-oracle-wms`, `flext-web`, `flext-dbt-ldap`, `flext-dbt-ldif`, `flext-dbt-oracle`, `flext-dbt-oracle-wms`, `gruponos-meltano-native` | 14 |

## Lint Scoping

- **During parallel work**: Each agent runs linters (ruff, mypy, pyright, pyrefly) ONLY on files they modified
- **At phase boundaries**: Agent completing a phase runs FULL project lint (`cd flext-core && make check`) before pushing
- **Before Phase 4**: ALL agents run full flext-core lint and verify ZERO errors before touching consumer projects
- **Zero tolerance**: NO `# type: ignore`, NO warnings, NO errors. Fix until clean.

## Git Discipline

- **Always rebase**: `git pull --rebase` before EVERY push. NEVER `git pull` without `--rebase`.
- **Never force push**: NEVER `git push --force` to main/master.
#XT|- **Never rollback (AXIOMATIC)**: NO `git revert`, NO `git reset`, NO `git checkout <file>` to discard work, NO `git stash pop` to overwrite committed changes. Fix forward ONLY. Every change by every agent MUST be accepted, improved, standardized, and fixed forward. If a previous agent's change is wrong, push a NEW fix commit. There is no rollback. There is no undo. There is only forward.
#ZX|- **Conflict resolution**: If conflict in YOUR file → resolve manually. If conflict in ANOTHER agent's file → `git checkout --theirs <file>` (accept their version — this is the ONLY permitted use of `git checkout <file>`, and ONLY to accept, never to discard).
#YH|- **Commit frequency**: Every task completion = separate commit. Small commits, frequent pushes.
#PF|- **Commit-After-Validation (AXIOMATIC)**: Immediately after ANY validation passes (linters, tests, `make check`, any quality gate), ALL pending changes across ALL touched projects MUST be committed and pushed — without delay, without waiting, without asking permission. Sequence: validation passes → `git add -A` (every project with changes) → `git commit` → `git pull --rebase` → `git push` → confirm clean `git status`. Uncommitted work after a passing validation is a VIOLATION. Unpushed work is LOST WORK — it does not exist.

## Conflict Resolution Protocol

1. **protocols.py conflicts**: Each agent appends at END of their section, never reorders, never auto-formats globally
2. **Rebase timing**: `git pull --rebase` before EVERY push
3. **File conflict resolution**:
   - YOUR file → resolve manually
   - ANOTHER agent's file → `git checkout --theirs <file>`
4. **Phase gates**: Agent completing phase runs FULL lint before pushing

## Usage

Load this skill when working on flext-core or consumer projects in parallel with other agents:

```bash
task(category="...", load_skills=["multi-agent-coordination"], ...)
```

For full details, always reference **CLAUDE.md §10 Multi-Agent Parallel Execution Law**.
