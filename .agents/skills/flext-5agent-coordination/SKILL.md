---
name: flext-5agent-coordination
description: "Use when coordinating 5 parallel agents on flext-core or consumer project work. Covers execution ritual (11 Commandments), ownership matrix, phase sequencing, lint scoping, and git hygiene for zero-conflict parallel delivery. Authoritative source: AGENTS.md §10."
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

## Rules

### The 11 Commandments (Unbreakable Law)

1. **Organize libs first** — Domain monopoly: each module owns its domain exclusively
2. **Minimal skeleton** — Start with interfaces/protocols, optimize structure before implementation
3. **Reconnect one-by-one** — Fix ONE integration at a time, verify before next
4. **Tests last per module** — Update tests AFTER implementation passes static checks
5. **4 linters zero tolerance** — ruff, mypy, pyright, pyrefly MUST all pass, no `# type: ignore`
6. **Stay in lane** — Only touch files in your ownership, READ-ONLY for others
7. **Never rollback** — Fix forward ONLY (`AGENTS.md` §3.5). `git revert`, `git reset`, `git checkout <file>`, `git stash pop/apply` to discard any agent's work are forbidden. Every change by every agent is accepted, improved, and fixed forward.
8. **Commit frequently** — Every task completion = separate commit + push
9. **.new/.old owned-only** — Use .new/.old pattern ONLY for files you own exclusively
10. **No automation scripts** — Manual changes only, no shell scripts for mass edits
11. **Never rush/ULW** — No ultrawork mode, no batching, perfection over speed

### File Ownership (flext-core)

| File                                                                                       | Owner                            | Others Allowed                                                                                            |
| ------------------------------------------------------------------------------------------ | -------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `dispatcher.py`                                                                            | Agent 1                          | READ only                                                                                                 |
| `constants.py`                                                                             | Agent 1                          | READ only                                                                                                 |
| `models/cqrs.py`                                                                          | Agent 1                          | READ only                                                                                                 |
| `registry.py`                                                                              | Agent 2                          | READ only                                                                                                 |
| `typings.py`                                                                               | Agent 2                          | READ only                                                                                                 |
| `service.py`                                                                               | Agent 3                          | READ only                                                                                                 |
| `models/base.py`                                                                          | Agent 3                          | READ only                                                                                                 |
| `result.py`                                                                                | Agent 4                          | READ only                                                                                                 |
| `exceptions.py`                                                                            | Agent 4                          | READ only (exception: Agent 4 may modify exceptions.py in ANY consumer project for e.BaseError hierarchy) |
| `runtime.py`                                                                               | Agent 4                          | Agent 5 READ only (MRO chain reference)                                                                   |
| `loggings.py`                                                                              | Agent 4                          | READ only                                                                                                 |
| `container.py`                                                                             | Agent 5 (primary)                | Agent 1: dispatcher singleton ADD only; Agent 4: return types only                                        |
| `decorators.py`                                                                            | Agent 5                          | READ only                                                                                                 |
| `handlers.py`                                                                              | Agent 5                          | READ only                                                                                                 |
| `mixins.py`                                                                                | Agent 5                          | READ only                                                                                                 |
| `protocols.py`                                                                             | SECTION-OWNED (see matrix below) | Each agent: own section ONLY, append at END, NEVER reorder, NEVER auto-format globally                    |
| `__init__.py`                                                                              | ❄️ FROZEN                        | Each agent appends own new exports only                                                                   |
| `context.py`, `settings.py`, `models.py`, `utilities.py`, `_utilities/*`, `__version__.py` | ❄️ FROZEN                        | No agent modifies                                                                                         |

### protocols.py Section Ownership Matrix

| Section                              | A1 (Dispatcher) | A2 (Registry) | A3 (Service) | A4 (Result/Exceptions) | A5 (CDH/Mixins) |
| ------------------------------------ | --------------- | ------------- | ------------ | ---------------------- | --------------- |
| L1-236 (infra)                       | ❄️              | ❄️            | ❄️           | ❄️                     | ❄️              |
| Context, RuntimeBootstrapOptions, DI | —               | —             | —            | —                      | ✅               |
| Result, Result                       | —               | —             | —            | ✅                      | —               |
| Model, Config, Service, Validation   | —               | —             | ✅            | —                      | —               |
| CommandBus, Middleware, Processor    | ✅               | —             | —            | —                      | —               |
| Handler                              | —               | —             | —            | —                      | ✅               |
| Registry                             | —               | ✅             | —            | —                      | —               |
| VariadicCallable, ResourceFactory    | —               | —             | —            | ✅                      | —               |
| RegisterableService, ServiceFactory  | —               | —             | —            | —                      | ✅               |
| Log, Logger, Metadata                | —               | —             | —            | ✅                      | —               |
| ValidatorSpec                        | —               | —             | ✅            | —                      | —               |
| L1289+ (metaclass infra)             | ❄️              | ❄️            | ❄️           | ❄️                     | ❄️              |
| ALL other sections                   | ❄️              | ❄️            | ❄️           | ❄️                     | ❄️              |

### Execution Phases (Dependency-Ordered)

Agents MUST execute in this order:

- **Phase 0 (SOLO)**: Agent 4 completes Wave 0 (RuntimeResult.**slots** + `r[T].fail()` + `p.Result`) and PUSHES. ALL other agents BLOCKED until Phase 0 complete.
- **Phase 1**: Agent 4 continues (exception propagation, safe(), chaining) + Agent 5 starts (containers/decorators/handlers/mixins). Agent 5 must `git pull --rebase` before starting.
- **Phase 2**: Agent 1 (Dispatcher) + Agent 3 (Service) start. Both must `git pull --rebase` before starting.
- **Phase 3**: Agent 2 (Registry) starts. Must `git pull --rebase` before starting.
- **Phase 4 (Consumer Projects)**: All agents work on their assigned consumer projects IN PARALLEL.

### Consumer Project Partition (31 projects, zero overlap)

| Agent   | Projects                                                                                                                                                                                                                                                                                                 | Count |
| ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----- |
| Agent 1 | `algar-oud-mig`, `flexcore`, `flext-api`                                                                                                                                                                                                                                                                 | 3     |
| Agent 2 | `flext-auth`, `flext-cli`, `flext-db-oracle`                                                                                                                                                                                                                                                             | 3     |
| Agent 3 | `flext-grpc`, `flext-ldap`, `flext-ldif`, `flext-meltano`                                                                                                                                                                                                                                                | 4     |
| Agent 4 | `flext-observability`, `flext-oracle-oic`, `flext-oracle-wms`, `flext-plugin`, `flext-quality`, `flext-tap-oracle-wms`, `flext-target-ldif`                                                                                                                                                              | 7     |
| Agent 5 | `flext-tap-ldap`, `flext-tap-ldif`, `flext-tap-oracle`, `flext-tap-oracle-oic`, `flext-target-ldap`, `flext-target-oracle`, `flext-target-oracle-oic`, `flext-target-oracle-wms`, `flext-web`, `flext-dbt-ldap`, `flext-dbt-ldif`, `flext-dbt-oracle`, `flext-dbt-oracle-wms`, `gruponos-meltano-native` | 14    |

### Lint Scoping

- **During parallel work**: Each agent runs linters (ruff, mypy, pyright, pyrefly) ONLY on files they modified
- **At phase boundaries**: Agent completing a phase runs FULL project lint (`cd flext-core && make check`) before pushing
- **Before Phase 4**: ALL agents run full flext-core lint and verify ZERO errors before touching consumer projects
- **Zero tolerance**: NO `# type: ignore`, NO warnings, NO errors. Fix until clean.

### Git Discipline

- **Always rebase**: `git pull --rebase` before EVERY push. NEVER `git pull` without `--rebase`.
- **Never force push**: NEVER `git push --force` to main/master.
- **Never rollback**: NO `git revert`, NO `git reset`, NO `git checkout <file>` to discard work, NO `git stash pop` to overwrite committed changes. Fix forward only (`AGENTS.md` §3.5). If a previous agent's change is wrong, push a NEW fix commit.
- **Conflict resolution**: If conflict in YOUR file → resolve manually. If conflict in ANOTHER agent's file → `git checkout --theirs <file>` (accept their version — the only permitted use of `git checkout <file>`, and only to accept).
- **Commit frequency**: Every task completion = separate commit. Small commits, frequent pushes.
- **Commit after validation**: Immediately after ANY validation passes (linters, tests, `make check`), ALL pending changes across ALL touched projects must be committed and pushed. Sequence: validation passes → `git add -A` per project → `git commit` → `git pull --rebase` → `git push` → confirm clean `git status`. Unpushed work is lost work.
- **Full context before every change**: Before ANY code change, (1) read and understand all existing code in the affected module — patterns, MRO chain, dependencies, base classes, contracts; (2) maximize reuse of existing library code, base classes, utilities, and type contracts; (3) apply changes uniformly across `src/`, `tests/`, and `examples/`; (4) produce the most complete, lint-free implementation. Simplifications, bypasses, mocks, fallbacks, stubs, TODOs, and placeholder logic are forbidden in committed code (`AGENTS.md` §3.5).

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
7. **Never rollback**: Fix forward (`AGENTS.md` §3.5). No `git revert`, no `git reset`, no `git checkout <file>` to discard work. Every change by every agent is accepted, improved, and fixed forward.
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
2. Agent 1 works on: dispatcher.py, constants.py, models/cqrs.py
3. Agent 3 works on: service.py, models/base.py
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
from __future__ import annotations

from flext_core import m, p, r


# Agent 4 working on result.py (owned file) — uses r[T] contracts
def process_item(item: m.Value) -> p.Result[bool]:
    """Process using r[T].ok / r[T].fail pattern."""
    if item is None:
        return r[bool].fail("item required")
    return r[bool].ok(True)
```

Why good: Agent 4 owns result.py and their protocols.py section. No conflicts.

### Bad: Crossing Lanes

```python
from __future__ import annotations

from flext_core import m, p, r


# Agent 1 consuming result.py (NOT owned) — Agent 1 must read-only
def agent1_handler(item: m.Value) -> p.Result[bool]:
    # Agent 1 NEVER modifies result.py; only uses r[T] from it
    return r[bool].ok(True)
```

Why bad: Agent 1 does not own result.py. This violates Commandment 6 (Stay in lane).

### Good: protocols.py Append-Only

```python
from __future__ import annotations

from typing import Protocol


# Agent 4 appending to their Result section (lines 299-512)
# Agent 4 adds new protocol at END of section
class VariadicCallable(Protocol):
    def __call__(self, *args: object, **kwargs: object) -> object: ...
```

Why good: Agent 4 appends at END of their section, never reorders.

### Bad: protocols.py Reordering

```python
from __future__ import annotations

from typing import Protocol, TypeVar

T = TypeVar("T")


# Agent 4 reordering sections globally — FORBIDDEN
# Handler belongs to Agent 5's section
class Handler(Protocol):
    def handle(self, cmd: object) -> None: ...


# Result belongs to Agent 4's section — but reordering is still bad
class Result(Protocol[T]):
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
git add flext-core/src/flext_core/protocols.py
git rebase --continue

# If conflict in ANOTHER agent's file: accept their version
git checkout --theirs flext-core/src/flext_core/protocols.py
git add flext-core/src/flext_core/protocols.py
git rebase --continue
```
