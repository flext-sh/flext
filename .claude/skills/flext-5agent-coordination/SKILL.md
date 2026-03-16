---
name: flext-5agent-coordination
description: 5-Agent Parallel Execution Protocol for flext-core and consumer projects. Authoritative source AGENTS.md §10.
---

# 5-Agent Parallel Execution Protocol

**Category**: Governance  
**Status**: Active  
**Agent Scope**: All 5 parallel agents  
**Authoritative Source**: AGENTS.md §10 Multi-Agent Parallel Execution Law

## Scope

- flext-core file ownership and section-level protocols.py control
- Execution phases and dependency ordering
- Consumer project partition (31 projects, zero overlap)
- Lint scoping and git discipline during parallel work
- Conflict resolution for protocols.py and multi-agent file access

## References

- `AGENTS.md` §10 (canonical law)
- `AGENTS.md` (agent roster and delegation)
- `flext-core/src/flext_core/protocols.py` (section ownership matrix)
- `.claude/skills/multi-agent-coordination/SKILL.md` (quick reference)

## Rules

### The 11 Commandments (Unbreakable Law)

1. **Organize libs first** — Domain monopoly: each module owns its domain exclusively
2. **Minimal skeleton** — Start with interfaces/protocols, optimize structure before implementation
3. **Reconnect one-by-one** — Fix ONE integration at a time, verify before next
4. **Tests last per module** — Update tests AFTER implementation passes static checks
5. **4 linters zero tolerance** — ruff, mypy, pyright, pyrefly MUST all pass, no `# type: ignore`
6. **Stay in lane** — Only touch files in your ownership, READ-ONLY for others
7. **Never rollback — AXIOMATIC** — Fix forward ONLY. `git revert`, `git reset`, `git checkout <file>`, `git stash pop/apply` to discard any agent's work are TOTALLY FORBIDDEN. Every change by every agent is accepted, improved, and fixed forward. Violation = extreme fault.
8. **Commit frequently** — Every task completion = separate commit + push
9. **.new/.old owned-only** — Use .new/.old pattern ONLY for files you own exclusively
10. **No automation scripts** — Manual changes only, no shell scripts for mass edits
11. **Never rush/ULW** — No ultrawork mode, no batching, perfection over speed

### File Ownership (flext-core)

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

### protocols.py Section Ownership Matrix

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
| Log, Logger, Metadata | — | — | — | ✅ | — |
| ValidatorSpec | — | — | ✅ | — | — |
| L1289+ (metaclass infra) | ❄️ | ❄️ | ❄️ | ❄️ | ❄️ |
| ALL other sections | ❄️ | ❄️ | ❄️ | ❄️ | ❄️ |

### Execution Phases (Dependency-Ordered)

Agents MUST execute in this order:

- **Phase 0 (SOLO)**: Agent 4 completes Wave 0 (RuntimeResult.**slots** + `r[T].fail()` + `p.Result`) and PUSHES. ALL other agents BLOCKED until Phase 0 complete.
- **Phase 1**: Agent 4 continues (exception propagation, safe(), chaining) + Agent 5 starts (containers/decorators/handlers/mixins). Agent 5 must `git pull --rebase` before starting.
- **Phase 2**: Agent 1 (Dispatcher) + Agent 3 (Service) start. Both must `git pull --rebase` before starting.
- **Phase 3**: Agent 2 (Registry) starts. Must `git pull --rebase` before starting.
- **Phase 4 (Consumer Projects)**: All agents work on their assigned consumer projects IN PARALLEL.

### Consumer Project Partition (31 projects, zero overlap)

| Agent | Projects | Count |
|-------|----------|-------|
| Agent 1 | `algar-oud-mig`, `flexcore`, `flext-api` | 3 |
| Agent 2 | `flext-auth`, `flext-cli`, `flext-db-oracle` | 3 |
| Agent 3 | `flext-grpc`, `flext-ldap`, `flext-ldif`, `flext-meltano` | 4 |
| Agent 4 | `flext-observability`, `flext-oracle-oic`, `flext-oracle-wms`, `flext-plugin`, `flext-quality`, `flext-tap-oracle-wms`, `flext-target-ldif` | 7 |
| Agent 5 | `flext-tap-ldap`, `flext-tap-ldif`, `flext-tap-oracle`, `flext-tap-oracle-oic`, `flext-target-ldap`, `flext-target-oracle`, `flext-target-oracle-oic`, `flext-target-oracle-wms`, `flext-web`, `flext-dbt-ldap`, `flext-dbt-ldif`, `flext-dbt-oracle`, `flext-dbt-oracle-wms`, `gruponos-meltano-native` | 14 |

### Lint Scoping

- **During parallel work**: Each agent runs linters (ruff, mypy, pyright, pyrefly) ONLY on files they modified
- **At phase boundaries**: Agent completing a phase runs FULL project lint (`cd flext-core && make check`) before pushing
- **Before Phase 4**: ALL agents run full flext-core lint and verify ZERO errors before touching consumer projects
- **Zero tolerance**: NO `# type: ignore`, NO warnings, NO errors. Fix until clean.

### Git Discipline

- **Always rebase**: `git pull --rebase` before EVERY push. NEVER `git pull` without `--rebase`.
- **Never force push**: NEVER `git push --force` to main/master.
- **Never rollback (AXIOMATIC)**: NO `git revert`, NO `git reset`, NO `git checkout <file>` to discard work, NO `git stash pop` to overwrite committed changes. Fix forward ONLY. Every change by every agent MUST be accepted, improved, standardized, and fixed forward. If a previous agent's change is wrong, push a NEW fix commit. There is no rollback. There is no undo. There is only forward.
- **Conflict resolution**: If conflict in YOUR file → resolve manually. If conflict in ANOTHER agent's file → `git checkout --theirs <file>` (accept their version — this is the ONLY permitted use of `git checkout <file>`, and ONLY to accept, never to discard).
- **Commit frequency**: Every task completion = separate commit. Small commits, frequent pushes.
- **Commit-After-Validation (AXIOMATIC)**: Immediately after ANY validation passes (linters, tests, `make check`, any quality gate), ALL pending changes across ALL touched projects MUST be committed and pushed — without delay, without waiting, without asking permission. Sequence: validation passes → `git add -A` (every project with changes) → `git commit` → `git pull --rebase` → `git push` → confirm clean `git status`. Uncommitted work after a passing validation is a VIOLATION. Unpushed work is LOST WORK — it does not exist.
- **Full Context Evaluation Before Every Change (AXIOMATIC)**: Before ANY code change, the agent MUST: (1) read and fully understand ALL existing code in the affected module — its patterns, MRO chain, dependencies, base classes, and existing contracts; (2) maximize reuse of existing library code, base classes, utilities, and type contracts — never reinvent, duplicate, or shadow what already exists; (3) apply changes uniformly across ALL namespaces — `src/`, `tests/`, AND `examples/` — every namespace is in scope, no namespace is exempt; (4) produce the most correct, complete, lint-free implementation using advanced code patterns, strong typing, full Pydantic v2 discipline, and the full power of the existing architecture. Simplifications, bypasses, mocks, fallbacks, stubs, TODOs, hardcoded values, and placeholder logic are TOTALLY FORBIDDEN in any committed code. Every change is final, complete, and production-grade from the first commit.

## Instructions

### Before Starting Any Phase

1. Read AGENTS.md §10 in full
2. Identify your agent number (1-5) and assigned files/projects
3. Verify file ownership: you own ONLY the files listed in your row
4. For protocols.py: identify your section lines and NEVER touch other sections
5. Run `git pull --rebase` to sync with latest main

### During Implementation

1. **Organize libs first**: Define interfaces/protocols before implementation
2. **Minimal skeleton**: Create structure, then fill in logic
3. **Reconnect one-by-one**: Fix ONE integration point at a time
4. **Tests last**: Update tests AFTER static checks pass
5. **4 linters**: Run ruff, mypy, pyright, pyrefly on YOUR files only
6. **Stay in lane**: READ-ONLY for other agents' files
7. **Never rollback (AXIOMATIC)**: Fix forward, no `git revert`, no `git reset`, no `git checkout <file>` to discard work. Every change by every agent is accepted, improved, and fixed forward.
8. **Commit frequently**: Every task = separate commit + push
9. **.new/.old pattern**: Use ONLY for files you own exclusively
10. **No automation**: Manual changes only
11. **Never rush**: Perfection over speed, no ultrawork mode

### At Phase Boundaries

1. Run FULL project lint: `cd flext-core && make check`
2. Verify ZERO errors, warnings, or `# type: ignore` suppressions
3. `git pull --rebase` before pushing
4. Push your phase-complete commit
5. Notify orchestrator that phase is complete

### Conflict Resolution (protocols.py)

1. Each agent appends at END of their section only
2. NEVER reorder sections
3. NEVER auto-format globally
4. If conflict in YOUR file: resolve manually
5. If conflict in ANOTHER agent's file: `git checkout --theirs <file>` (accept their version — ONLY permitted use of `git checkout <file>`)

## Workflow

### Phase 0 (Agent 4 Solo)

1. Agent 4 implements Wave 0: RuntimeResult.**slots**, `r[T].fail()`, p.Result
2. Agent 4 runs full lint: `cd flext-core && make check`
3. Agent 4 commits and pushes
4. All other agents BLOCKED until Phase 0 complete

### Phase 1 (Agent 4 + Agent 5)

1. Agent 4 pulls latest: `git pull --rebase`
2. Agent 4 continues: exception propagation, safe(), chaining
3. Agent 5 pulls latest: `git pull --rebase`
4. Agent 5 starts: containers, decorators, handlers, mixins
5. Both run linters on their files only
6. Both commit and push independently

### Phase 2 (Agent 1 + Agent 3)

1. Both pull latest: `git pull --rebase`
2. Agent 1 works on: dispatcher.py, constants.py, _models/cqrs.py
3. Agent 3 works on: service.py, _models/base.py
4. Both run linters on their files only
5. Both commit and push independently

### Phase 3 (Agent 2)

1. Agent 2 pulls latest: `git pull --rebase`
2. Agent 2 works on: registry.py, typings.py
3. Agent 2 runs linters on their files only
4. Agent 2 commits and pushes

### Phase 4 (All Agents on Consumer Projects)

1. ALL agents run full flext-core lint: `cd flext-core && make check`
2. Verify ZERO errors before touching consumer projects
3. Each agent works on their assigned projects IN PARALLEL
4. Each agent runs linters on their files only
5. Each agent commits and pushes independently

## Examples

### Good: Staying in Lane

```python
# Agent 4 working on result.py (owned file)
# Agent 4 can modify result.py freely
class r(Generic[T]):
    @classmethod
    def fail(cls, error: Exception) -> "r[T]":
        return r[T](error=error)


# Agent 4 appends to protocols.py Result section (lines 299-512)
# Agent 4 NEVER touches other sections
class Result(Protocol[T]):
    @property
    def value(self) -> T: ...
```

Why good: Agent 4 owns result.py and their protocols.py section. No conflicts.

### Bad: Crossing Lanes

```python
# Agent 1 modifying result.py (NOT owned)
# Agent 1 should NOT touch this file
class r(Generic[T]):
    def fail(self, error: Exception) -> "r[T]":
        return r(error=error)
```

Why bad: Agent 1 does not own result.py. This violates Commandment 6 (Stay in lane).

### Good: protocols.py Append-Only

```python
# Agent 4 appending to their Result section (lines 299-512)
# Agent 4 adds new protocol at END of section
class VariadicCallable(Protocol):
    def __call__(self, *args, **kwargs): ...
```

Why good: Agent 4 appends at END of their section, never reorders.

### Bad: protocols.py Reordering

```python
# Agent 4 reordering sections globally
# This breaks other agents' section boundaries
class Handler(Protocol):  # This is Agent 5's section!
    def handle(self, cmd): ...  # FORBIDDEN was here


class Result(Protocol[T]):  # Agent 4's section
    @property
    def value(self) -> T: ...
```

Why bad: Reordering breaks section ownership. Each agent appends at END only.

## Verification

### Before Starting Phase

```bash
# Verify you own the files you're about to modify
grep -A 20 "File Ownership Table" AGENTS.md | grep "Agent X"

# Verify your protocols.py section lines
grep -n "^class Result\|^class CommandBus\|^class Registry" flext-core/src/flext_core/protocols.py

# Verify git is clean
git status
```

### During Implementation

```bash
# Run linters on YOUR files only
ruff check flext-core/src/flext_core/result.py
mypy flext-core/src/flext_core/result.py
pyright flext-core/src/flext_core/result.py
pyrefly flext-core/src/flext_core/result.py

# Verify no type: ignore suppressions
grep -n "# type: ignore" flext-core/src/flext_core/result.py
```

### At Phase Boundaries

```bash
# Run FULL project lint
cd flext-core && make check

# Verify ZERO errors
echo $?  # Must be 0

# Verify no uncommitted changes
git status

# Rebase and push
git pull --rebase
git push
```

### Conflict Resolution

```bash
# If conflict in YOUR file: resolve manually
git status  # See conflicted files
# Edit file, resolve conflict
git add <file>
git rebase --continue

# If conflict in ANOTHER agent's file: accept their version
git checkout --theirs <file>
git add <file>
git rebase --continue
```
