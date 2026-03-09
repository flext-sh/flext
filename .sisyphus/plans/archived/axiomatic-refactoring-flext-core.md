# ARCHIVED — Subsumed by modernization-reorg-execution.md

# Axiomatic Rules Refactoring — flext-core

## TL;DR

> **Quick Summary**: Apply ALL 15+ AXIOMATIC rules from CLAUDE.md §3 Code Law to flext-core codebase. Rule-by-rule sweeps across all files, not file-by-file. Annotation/type changes ONLY — zero behavioral changes.
> 
> **Deliverables**:
> - flext-core src/ passing ALL 4 linters (ruff, mypy, pyright, pyrefly) with ZERO errors
> - ZERO `Any`/`object`/`dict[str,Any]` in type annotations
> - ALL Pydantic models using `Field()` with rich metadata
> - ALL internal state using `PrivateAttr`
> - ALL suppression comments audited (justified or removed)
> - ALL consumer projects passing `make check` after changes
> 
> **Estimated Effort**: XL (100+ files, ~50k lines)
> **Parallel Execution**: YES — 8 waves
> **Critical Path**: Wave 0 → Wave 1 → Wave 2 → Wave 3 → Wave 4 → Wave 5 → Wave 6 → Wave 7 → Wave FINAL

---

## Context

### Original Request
Apply ALL axiomatic rules refactoring the current code of all FLEXT projects, starting with flext-core.

### Interview Summary
**Key Discussions**:
- 15+ AXIOMATIC rules already codified in CLAUDE.md §3 and all skills
- Rules cover: typing purity, Pydantic v2 way, FlextResult mandatory, no legacy/wrappers, MRO inheritance, 4 linters clean, no suppressions without justification
- flext-core is the foundation — changes cascade to all 33 consumer projects

**Research Findings**:
- **114 files** use `Any`/`object`/`dict[str,Any]` — major violation targets
- **58 files** define BaseModel classes — need Pydantic v2 way enforcement
- **65 files** have bare `self._x` assignments — need `PrivateAttr` migration
- **23 files** use raw `json.loads()`/`json.dumps()` — need Pydantic JSON
- **190 files** have `# type: ignore`/`# noqa` — need audit
- **100+ files** in src/ totaling ~50k lines across flext_core, flext_tests, flext_infra

### Metis Review
**Identified Gaps** (addressed):
- **CRITICAL BLOCKER**: `t.ConfigMapValue`, `t.ConfigMap`, `t.Dict`, `t.GeneralValueType` referenced in rules but DON'T EXIST in `typings.py` — resolved as Wave 0 task (move phantom aliases to typings.py)
- **Wave order**: `runtime.py` must come before `result.py` (inheritance dependency) — fixed
- **FROZEN files conflict**: §10 marks settings.py, _utilities/*, context.py as FROZEN — resolved: amend §10 ownership for this refactoring
- **Tests per-wave**: Tests must be updated alongside each wave, not deferred — incorporated
- **Behavioral freeze**: Annotation/type changes ONLY, zero logic changes — set as guardrail
- **Third-party Any**: returns/structlog/dependency_injector inject `Any` — resolved: justified per-line suppressions with citations
- **Rule-by-rule sweeps**: One rule category per pass across all files (reviewable diffs) — adopted

---

## Work Objectives

### Core Objective
Enforce ALL AXIOMATIC rules from CLAUDE.md §3 across every Python file in flext-core, making it the fully-compliant foundation for all 33 consumer projects.

### Concrete Deliverables
- `flext-core/src/flext_core/` — ZERO violations of any AXIOMATIC rule
- `flext-core/src/flext_tests/` — ZERO violations (same discipline as production)
- `flext-core/src/flext_infra/` — ZERO violations (same discipline as production)
- `flext-core/tests/` — annotation updates matching source changes
- `.reports/pre-refactor-baseline.txt` — linter baseline before changes
- `.reports/suppression-audit.csv` — justified/removed suppression inventory

### Definition of Done
- [ ] `cd flext-core && make check` exits 0
- [ ] `cd flext-core && pytest tests/ -x -q` — 0 failures
- [ ] `grep -rn '\bAny\b' src/flext_core/ --include='*.py' | grep -v TYPE_CHECKING | wc -l` — 0 unjustified matches
- [ ] `grep -rn '# type: ignore' src/flext_core/ --include='*.py'` — each line has documented justification
- [ ] `cd flext-ldap && make check` exits 0 (consumer smoke test)
- [ ] `cd flext-meltano && make check` exits 0 (consumer smoke test)
- [ ] `cd flext-tap-oracle && make check` exits 0 (consumer smoke test)

### Must Have
- ALL `Any`/`object`/`dict[str,Any]` replaced with `t.*` contracts
- ALL Pydantic model fields using `Field()` with `description` at minimum
- ALL internal state using `PrivateAttr` (no bare `self._x`)
- ALL `json.loads()`/`json.dumps()` replaced with Pydantic JSON functions or `TypeAdapter`
- ALL suppression comments audited and justified or removed
- ALL 4 linters passing clean after every wave

### Must NOT Have (Guardrails)
- **BEHAVIORAL FREEZE**: No logic changes, no algorithm changes, no control flow changes. If a test passes before and fails after, the change is WRONG.
- **NO "while I'm here" syndrome**: Do NOT fix unrelated issues discovered during refactoring
- **NO MRO restructuring**: Flag non-conforming module structures as issues, do NOT restructure in this plan
- **NO new features**: Do NOT add new methods, classes, or capabilities during refactoring
- **NO new type aliases outside typings.py**: All new types go in `typings.py` only
- **NO blanket suppression deletion**: Audit each suppression individually — some are genuinely justified (third-party library types)
- **NO docstring rewriting**: Update type references in docstrings only, not prose
- **NO consumer project refactoring**: flext-core ONLY in this plan; consumer projects are Phase 2
- **DO NOT delete `_utilities/deprecation.py`**: It is infrastructure tooling, not legacy code. Exempt from "legacy exterminated on contact" rule.

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES (pytest, conftest.py, `make test`)
- **Automated tests**: YES (tests-alongside — update annotations per wave)
- **Framework**: pytest + make check (ruff + pyrefly + bandit)

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Typing changes**: Use Bash (ruff/mypy/pyright/pyrefly) — run all 4 linters, assert ZERO errors
- **Import sanity**: Use Bash — `python -c "import flext_core"` — assert no ImportError
- **Test suite**: Use Bash — `pytest tests/ -x -q` — assert 0 failures
- **Consumer smoke**: Use Bash — `cd <project> && make check` — assert exit 0

### Linter Commands (EXACT)
```bash
cd flext-core && ruff check src/ --select ALL 2>&1 | tail -5
cd flext-core && ruff format --check src/ 2>&1 | tail -5
cd flext-core && python -m pyrefly check src/flext_core/ 2>&1 | tail -10
cd flext-core && make check 2>&1 | tail -20
```

---

## Execution Strategy

### Strategy: Rule-by-Rule Sweeps (NOT file-by-file)

Per Metis recommendation: "One rule category per pass across all files" produces reviewable, testable, bisectable diffs. Each wave applies ONE category of changes across all files, not all changes to one file.

### Parallel Execution Waves

```
Wave 0 (Sequential — baseline + foundation):
├── Task 1: Baseline measurement + linter state capture [quick]
├── Task 2: Type alias completeness audit + move phantoms to typings.py [deep]
└── Task 3: Amend §10 FROZEN policy for this refactoring [quick]

Wave 1 (Parallel — Any/object purge, max parallel by directory):
├── Task 4: Replace Any/object in flext_core/ facade files [deep]
├── Task 5: Replace Any/object in _models/ directory [deep]
├── Task 6: Replace Any/object in _utilities/ directory [deep]
├── Task 7: Replace Any/object in _decorators/ + _dispatcher/ [unspecified-high]
├── Task 8: Replace Any/object in flext_tests/ package [deep]
└── Task 9: Replace Any/object in flext_infra/ package [unspecified-high]

Wave 2 (Parallel — inline types + None cleanup):
├── Task 10: Replace inline composed types with t.* references [deep]
├── Task 11: Audit | None usage — remove gratuitous, keep business-required [deep]
└── Task 12: Replace json.loads/dumps with Pydantic JSON functions [unspecified-high]

Wave 3 (Parallel — Pydantic v2 internal state):
├── Task 13: Migrate bare self._x to PrivateAttr in _models/ [deep]
├── Task 14: Migrate bare self._x to PrivateAttr in facade files [deep]
└── Task 15: Remove *Config classes → ConfigDict/BaseSettings [unspecified-high]

Wave 4 (Parallel — Pydantic v2 enrichment):
├── Task 16: Add Field() metadata to _models/ (description/title/examples) [deep]
├── Task 17: Add Field() metadata to facade models + flext_tests models [deep]
├── Task 18: Minimize custom validators — prefer built-in constraints [deep]
└── Task 19: Replace unnecessary @property with @computed_field [unspecified-high]

Wave 5 (Parallel — cleanup + enforcement):
├── Task 20: Remove init helpers, getters/setters, wrappers in models [deep]
├── Task 21: Suppression audit — justify or remove # type: ignore/# noqa [deep]
└── Task 22: Ensure Enum/Mapping/Literal from constants.py only [unspecified-high]

Wave 6 (Sequential — integration verification):
├── Task 23: Full 4-linter clean verification on flext-core [deep]
├── Task 24: Full test suite pass verification [deep]
└── Task 25: Consumer project smoke tests (flext-ldap, flext-meltano, flext-tap-oracle) [unspecified-high]

Wave 7 (Sequential — compliance audit):
└── Task 26: MRO/structural compliance audit — flag non-conforming modules as issues [deep]

Wave FINAL (After ALL tasks — independent review, 4 parallel):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real QA — run all linters + tests + consumer smoke (unspecified-high)
└── Task F4: Scope fidelity check (deep)

Critical Path: T1 → T2 → T4-T9 → T10-T12 → T13-T15 → T16-T19 → T20-T22 → T23 → T24 → T25 → F1-F4
Parallel Speedup: ~65% faster than sequential
Max Concurrent: 6 (Waves 1 & 4)
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|-----------|--------|
| 1 | — | 2, 3, 4-9 |
| 2 | 1 | 4-9 |
| 3 | 1 | 4-9 |
| 4-9 | 2, 3 | 10-12 |
| 10-12 | 4-9 | 13-15 |
| 13-15 | 10-12 | 16-19 |
| 16-19 | 13-15 | 20-22 |
| 20-22 | 16-19 | 23 |
| 23 | 20-22 | 24 |
| 24 | 23 | 25 |
| 25 | 24 | 26, F1-F4 |
| 26 | 25 | F1-F4 |
| F1-F4 | 26 | — |

### Agent Dispatch Summary

| Wave | Tasks | Categories |
|------|-------|-----------|
| 0 | 3 | T1 → `quick`, T2 → `deep`, T3 → `quick` |
| 1 | 6 | T4-T6 → `deep`, T7 → `unspecified-high`, T8 → `deep`, T9 → `unspecified-high` |
| 2 | 3 | T10-T11 → `deep`, T12 → `unspecified-high` |
| 3 | 3 | T13-T14 → `deep`, T15 → `unspecified-high` |
| 4 | 4 | T16-T18 → `deep`, T19 → `unspecified-high` |
| 5 | 3 | T20-T21 → `deep`, T22 → `unspecified-high` |
| 6 | 3 | T23-T24 → `deep`, T25 → `unspecified-high` |
| 7 | 1 | T26 → `deep` |
| FINAL | 4 | F1 → `oracle`, F2-F3 → `unspecified-high`, F4 → `deep` |

---

## Pre-Execution: Beads Tracking Setup — ✅ COMPLETED 2026-03-03

> **STATUS: ALL 31 issues created, 75 dependencies wired. DO NOT re-run.**
> Parent epic: `mro-b4b`
> Start work: `bd update mro-q6f --status in_progress` then execute T1.

### Beads ID Map (Authoritative)

```
PARENT  mro-b4b   Axiomatic Rules Refactoring — flext-core

Wave 0 (Sequential):
  T1  mro-q6f   Baseline Measurement + Linter State Capture
  T2  mro-1xw   Type Alias Completeness — Move Phantoms to typings.py
  T3  mro-26y   Amend §10 FROZEN Policy for Axiomatic Refactoring

Wave 1 (Parallel — all depend on T2+T3):
  T4  mro-i4z   Replace Any/object in flext_core/ Facade Files
  T5  mro-6k5   Replace Any/object in _models/ Directory
  T6  mro-dda   Replace Any/object in _utilities/ Directory
  T7  mro-17j   Replace Any/object in _decorators/ + _dispatcher/
  T8  mro-29n   Replace Any/object in flext_tests/ Package
  T9  mro-bv9   Replace Any/object in flext_infra/ Package

Wave 2 (Parallel — all depend on T4-T9):
  T10 mro-bbs   Replace Inline Composed Types with t.* References
  T11 mro-b5m   Audit | None Usage — Remove Gratuitous, Keep Business-Required
  T12 mro-bae   Replace json.loads/dumps with Pydantic JSON Functions

Wave 3 (Parallel — all depend on T10-T12):
  T13 mro-qbi   Migrate Bare self._x to PrivateAttr in _models/
  T14 mro-89q   Migrate Bare self._x to PrivateAttr in Facade Files
  T15 mro-s2w   Verify ConfigDict Usage — No Old-Style class Config

Wave 4 (Parallel — all depend on T13-T15):
  T16 mro-97v   Add Field() Metadata to _models/
  T17 mro-g6x   Add Field() Metadata to Facade + flext_tests Models
  T18 mro-xja   Minimize Custom Validators — Prefer Built-in Constraints
  T19 mro-e4u   Replace Unnecessary @property with @computed_field

Wave 5 (Parallel — all depend on T16-T19):
  T20 mro-7pe   Remove Init Helpers, Getters/Setters, Wrappers in Models
  T21 mro-q7m   Suppression Audit — Justify or Remove type:ignore/noqa
  T22 mro-vgx   Ensure Enum/Mapping/Literal from constants.py Only

Wave 6 (Sequential — T23 depends on T20-T22):
  T23 mro-dsk   Full 4-Linter Clean Verification on flext-core
  T24 mro-18i   Full Test Suite Pass Verification
  T25 mro-71y   Consumer Project Smoke Tests (ldap/meltano/tap-oracle)

Wave 7 (Sequential — depends on T25):
  T26 mro-jwp   MRO/Structural Compliance Audit — Flag Non-Conforming Modules

Wave FINAL (Parallel — all depend on T26):
  F1  mro-3dw   Plan Compliance Audit (oracle agent)
  F2  mro-w3o   Code Quality Review (unspecified-high agent)
  F3  mro-bnh   Real QA — Linters + Tests + Consumer Smoke
  F4  mro-mr7   Scope Fidelity Check (deep agent)
```

### Step 1: Create Parent Epic

```bash
PARENT=$(bd create "Axiomatic Rules Refactoring — flext-core" -t feature -p 0 --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
```

### Step 2: Create All 30 Task Issues (Sequential — capture IDs)

```bash
# Wave 0: Baseline + Foundation
T1=$(bd create "T1: Baseline Measurement + Linter State Capture" -t task -p 0 --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
T2=$(bd create "T2: Type Alias Completeness — Move Phantoms to typings.py" -t task -p 0 --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
T3=$(bd create "T3: Amend §10 FROZEN Policy for Axiomatic Refactoring" -t task -p 0 --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Wave 1: Any/object Purge (6 parallel tasks)
T4=$(bd create "T4: Replace Any/object in flext_core/ Facade Files" -t task -p 0 --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
T5=$(bd create "T5: Replace Any/object in _models/ Directory" -t task -p 0 --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
T6=$(bd create "T6: Replace Any/object in _utilities/ Directory" -t task -p 0 --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
T7=$(bd create "T7: Replace Any/object in _decorators/ + _dispatcher/" -t task -p 0 --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
T8=$(bd create "T8: Replace Any/object in flext_tests/ Package" -t task -p 0 --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
T9=$(bd create "T9: Replace Any/object in flext_infra/ Package" -t task -p 0 --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Wave 2: Inline Types + None + JSON (3 parallel tasks)
T10=$(bd create "T10: Replace Inline Composed Types with t.* References" -t task -p 0 --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
T11=$(bd create "T11: Audit | None Usage — Remove Gratuitous, Keep Business-Required" -t task -p 0 --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
T12=$(bd create "T12: Replace json.loads/dumps with Pydantic JSON Functions" -t task -p 0 --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Wave 3: Pydantic v2 Internal State (3 parallel tasks)
T13=$(bd create "T13: Migrate Bare self._x to PrivateAttr in _models/" -t task -p 0 --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
T14=$(bd create "T14: Migrate Bare self._x to PrivateAttr in Facade Files" -t task -p 0 --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
T15=$(bd create "T15: Verify ConfigDict Usage — No Old-Style class Config" -t task -p 0 --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Wave 4: Field Enrichment (4 parallel tasks)
T16=$(bd create "T16: Add Field() Metadata to _models/" -t task -p 0 --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
T17=$(bd create "T17: Add Field() Metadata to Facade + flext_tests Models" -t task -p 0 --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
T18=$(bd create "T18: Minimize Custom Validators — Prefer Built-in Constraints" -t task -p 0 --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
T19=$(bd create "T19: Replace Unnecessary @property with @computed_field" -t task -p 0 --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Wave 5: Cleanup + Enforcement (3 parallel tasks)
T20=$(bd create "T20: Remove Init Helpers, Getters/Setters, Wrappers in Models" -t task -p 0 --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
T21=$(bd create "T21: Suppression Audit — Justify or Remove # type: ignore / # noqa" -t task -p 0 --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
T22=$(bd create "T22: Ensure Enum/Mapping/Literal from constants.py Only" -t task -p 0 --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Wave 6: Integration Verification (3 sequential tasks)
T23=$(bd create "T23: Full 4-Linter Clean Verification on flext-core" -t task -p 0 --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
T24=$(bd create "T24: Full Test Suite Pass Verification" -t task -p 0 --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
T25=$(bd create "T25: Consumer Project Smoke Tests (ldap/meltano/tap-oracle)" -t task -p 0 --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Wave 7: MRO Compliance Audit
T26=$(bd create "T26: MRO/Structural Compliance Audit — Flag Non-Conforming Modules" -t task -p 0 --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Wave FINAL: Review (4 parallel tasks)
F1=$(bd create "F1: Plan Compliance Audit (oracle agent)" -t task -p 0 --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
F2=$(bd create "F2: Code Quality Review" -t task -p 0 --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
F3=$(bd create "F3: Real QA — Linters + Tests + Consumer Smoke" -t task -p 0 --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
F4=$(bd create "F4: Scope Fidelity Check" -t task -p 0 --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
```

### Step 3: Wire All 75 Dependencies (Wave Transitions)

```bash
# Wave 0 internal: T2→T1, T3→T1
bd dep add $T2 $T1 && bd dep add $T3 $T1

# Wave 0 → Wave 1: each of T4-T9 depends on T2 AND T3
for t in $T4 $T5 $T6 $T7 $T8 $T9; do
  bd dep add $t $T2 && bd dep add $t $T3
done

# Wave 1 → Wave 2: each of T10-T12 depends on ALL of T4-T9
for t in $T10 $T11 $T12; do
  for dep in $T4 $T5 $T6 $T7 $T8 $T9; do bd dep add $t $dep; done
done

# Wave 2 → Wave 3: each of T13-T15 depends on ALL of T10-T12
for t in $T13 $T14 $T15; do
  for dep in $T10 $T11 $T12; do bd dep add $t $dep; done
done

# Wave 3 → Wave 4: each of T16-T19 depends on ALL of T13-T15
for t in $T16 $T17 $T18 $T19; do
  for dep in $T13 $T14 $T15; do bd dep add $t $dep; done
done

# Wave 4 → Wave 5: each of T20-T22 depends on ALL of T16-T19
for t in $T20 $T21 $T22; do
  for dep in $T16 $T17 $T18 $T19; do bd dep add $t $dep; done
done

# Wave 5 → Wave 6: T23 depends on ALL of T20-T22, then sequential
for dep in $T20 $T21 $T22; do bd dep add $T23 $dep; done
bd dep add $T24 $T23 && bd dep add $T25 $T24

# Wave 6 → Wave 7: T26 depends on T25
bd dep add $T26 $T25

# Wave 7 → Final: F1-F4 each depend on T26
for t in $F1 $F2 $F3 $F4; do bd dep add $t $T26; done
```

### Step 4: Verify Setup

```bash
bd stats           # Should show 30 open + 1 epic
bd ready           # Should show ONLY T1 (only task with no blockers)
bd blocked         # Should show T2-T26 + F1-F4 (all blocked by deps)
```

### Dependency Map (Visual)

```
T1 ─┬─→ T2 ─┬─→ T4 ─┐
     │        │       │
     └─→ T3 ─┤→ T5 ─┤
              │→ T6 ─┤→ T10 ─┐
              │→ T7 ─┤→ T11 ─┤→ T13 ─┐
              │→ T8 ─┤→ T12 ─┤→ T14 ─┤→ T16 ─┐
              └→ T9 ─┘       └→ T15 ─┤→ T17 ─┤→ T20 ─┐
                                     │→ T18 ─┤→ T21 ─┤→ T23 → T24 → T25 → T26 ─┬→ F1
                                     └→ T19 ─┘→ T22 ─┘                           ├→ F2
                                                                                  ├→ F3
                                                                                  └→ F4
```

### Execution Rules (ZERO TOLERANCE)

1. **NO task starts until ALL its blockers are `bd close`d** — `bd ready` is the ONLY source of truth
2. **NO wave advances with ANY task incomplete** — partial wave = blocked downstream
3. **EVERY task must produce evidence** in `.sisyphus/evidence/task-{N}-*.{ext}` before closing
4. **EVERY wave must pass `make check`** before committing — failed linter = task NOT done
5. **`bd close <id>` ONLY after ALL acceptance criteria pass** — premature close = corrupted tracking
6. **Behavioral freeze** — if a test passes before and fails after annotation change, the change is WRONG
7. **`bd sync` after EVERY wave commit** — sync state to remote for recovery

### Recovery Protocol

If a session is interrupted mid-wave:
1. `bd list --status in_progress` — see what was being worked on
2. `bd ready` — see what can be picked up next
3. `bd blocked` — verify nothing was prematurely unblocked
4. Resume from the incomplete task, NOT from scratch

---

## TODOs


### Wave 0: Baseline + Foundation (Sequential)

- [ ] 1. Baseline Measurement + Linter State Capture

  **What to do**:
  - Run `cd flext-core && make check 2>&1 | tee .reports/pre-refactor-baseline.txt && echo "EXIT: $?"`
  - Run `cd flext-core && pytest tests/ -x -q 2>&1 | tee .reports/pre-refactor-tests.txt && echo "EXIT: $?"`
  - Count current violations: `grep -rn '\bAny\b' src/ --include='*.py' | wc -l`
  - Count suppressions: `grep -rn '# type: ignore\|# noqa' src/ --include='*.py' | wc -l`
  - Count bare self._x: `grep -rn 'self\._[a-z].*=' src/ --include='*.py' | wc -l`
  - Count raw json: `grep -rn 'json\.loads\|json\.dumps' src/ --include='*.py' | wc -l`
  - Save all counts to `.reports/pre-refactor-violation-counts.txt`

  **Must NOT do**: Change any code. This is measurement only.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 0 (sequential)
  - **Blocks**: Tasks 2, 3, 4-9
  - **Blocked By**: None

  **References**:
  - `flext-core/Makefile` — `make check` and `make test` targets
  - `flext-core/pyproject.toml` — pytest and ruff configuration

  **Acceptance Criteria**:
  - [ ] `.reports/pre-refactor-baseline.txt` exists and contains `make check` output
  - [ ] `.reports/pre-refactor-tests.txt` exists and contains pytest output
  - [ ] `.reports/pre-refactor-violation-counts.txt` exists with all 4 counts

  ```
  Scenario: Baseline captured
    Tool: Bash
    Steps:
      1. Run `cat .reports/pre-refactor-baseline.txt | tail -5`
      2. Run `cat .reports/pre-refactor-violation-counts.txt`
    Expected Result: All 3 files exist with content
    Evidence: .sisyphus/evidence/task-1-baseline.txt
  ```

  **Commit**: YES (group with T2, T3)
  - Message: `chore(flext-core): establish refactoring baseline and type alias completeness`

- [ ] 2. Type Alias Completeness — Move Phantom Aliases to typings.py

  **What to do**:
  - Audit every `t.*` reference across ALL source files in flext-core
  - Identify phantom aliases: types referenced as `t.X` but NOT defined in `flext-core/src/flext_core/typings.py`
  - Known phantoms from Metis review: `t.ConfigMapValue` (46 refs), `t.ConfigMap`, `t.Dict`, `t.GeneralValueType`
  - For each phantom: locate actual definition (likely in `_models/containers.py` as RootModel classes)
  - Move type alias definitions to `typings.py` OR add re-exports so `t.X` resolves correctly
  - Verify: `python -c "from flext_core import FlextTypes as t; print(t.ConfigMap, t.Dict, t.GeneralValueType)"`
  - Run `make check` to verify no regressions

  **Must NOT do**: Create NEW type aliases that don't already exist somewhere. Only MOVE existing ones.

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`flext-type-system`, `flext-strict-typing`]

  **Parallelization**:
  - **Can Run In Parallel**: NO (foundation for all subsequent tasks)
  - **Parallel Group**: Wave 0 (sequential after T1)
  - **Blocks**: Tasks 4-9 (all Wave 1 tasks)
  - **Blocked By**: Task 1

  **References**:
  - `flext-core/src/flext_core/typings.py` — type system source of truth (currently 160 lines)
  - `flext-core/src/flext_core/_models/containers.py` — where `ConfigMap`, `Dict` live as RootModel classes (205 lines)
  - `flext-core/src/flext_core/_models/collections.py` — collection models (840 lines)
  - `CLAUDE.md` §3 line 65 — `t.*` contract references

  **Acceptance Criteria**:
  - [ ] `python -c "from flext_core import FlextTypes as t; print(t.ConfigMap)"` — no AttributeError
  - [ ] `python -c "from flext_core import FlextTypes as t; print(t.GeneralValueType)"` — no AttributeError
  - [ ] `cd flext-core && make check` — exit 0 (or same baseline)
  - [ ] `cd flext-core && pytest tests/ -x -q` — 0 failures

  ```
  Scenario: All t.* aliases resolve
    Tool: Bash
    Steps:
      1. Run `python -c "from flext_core import FlextTypes as t; attrs = ['ConfigMap', 'Dict', 'GeneralValueType', 'ScalarValue', 'JsonValue', 'ConfigMapValue']; [print(f't.{a} = {getattr(t, a)}') for a in attrs]"`
      2. Run `cd flext-core && make check`
    Expected Result: All attributes resolve. make check exit 0.
    Evidence: .sisyphus/evidence/task-2-type-aliases.txt
  ```

  **Commit**: YES (group with T1, T3)

- [ ] 3. Amend §10 FROZEN Policy for Axiomatic Refactoring

  **What to do**:
  - Read CLAUDE.md §10 and identify files marked FROZEN: `settings.py`, `_utilities/*`, `context.py`, `models.py`, `utilities.py`, `_runtime_metadata.py`, `__version__.py`
  - Add a scoped exception in §10 for AXIOMATIC rule enforcement: "FROZEN files are unfrozen for annotation-only changes required by AXIOMATIC rules. Behavioral changes remain FROZEN."
  - This allows typing/annotation changes in frozen files without violating §10

  **Must NOT do**: Remove the FROZEN policy entirely. Only add an AXIOMATIC exception.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T2)
  - **Parallel Group**: Wave 0
  - **Blocks**: Tasks 4-9
  - **Blocked By**: Task 1

  **References**:
  - `CLAUDE.md` §10 — Agent ownership and FROZEN file policy

  **Acceptance Criteria**:
  - [ ] CLAUDE.md §10 contains AXIOMATIC exception clause for frozen files
  - [ ] grep `AXIOMATIC.*FROZEN\|FROZEN.*AXIOMATIC` in CLAUDE.md returns at least 1 match

  ```
  Scenario: §10 amended
    Tool: Bash
    Steps:
      1. Run `grep -n 'AXIOMATIC' /home/marlonsc/flext/CLAUDE.md | grep -i frozen`
    Expected Result: At least 1 line with AXIOMATIC + FROZEN amendment
    Evidence: .sisyphus/evidence/task-3-frozen-amendment.txt
  ```

  **Commit**: YES (group with T1, T2)

### Wave 1: Any/object Purge (Parallel — 6 tasks)

- [ ] 4. Replace Any/object in flext_core/ Facade Files

  **What to do**:
  - Target files: `typings.py`, `constants.py`, `models.py`, `protocols.py`, `result.py`, `runtime.py`, `service.py`, `container.py`, `dispatcher.py`, `context.py`, `decorators.py`, `mixins.py`, `handlers.py`, `exceptions.py`, `loggings.py`, `registry.py`, `utilities.py`, `settings.py`, `__init__.py`
  - Use ast-grep to find ALL `Any` in type annotations: `sg -p 'Any' -l python --json flext-core/src/flext_core/*.py`
  - Replace each `Any` with the appropriate `t.*` contract from the replacement table in `flext-strict-typing` Rule 1
  - Replace each `object` in type position with `t.GeneralValueType` or specific `t.*` type
  - Replace each `dict[str, Any]` with `t.ConfigMap`, `t.Dict`, or `Mapping[str, t.GeneralValueType]`
  - For third-party library boundaries (`returns`, `structlog`, `dependency_injector`): add per-line `# type: ignore[...]  # JUSTIFIED: <library> exposes Any — see <URL>`
  - Update corresponding test files that assert on changed signatures
  - Run `make check` after all replacements

  **Must NOT do**: Change function logic. Annotation-only changes.

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`flext-strict-typing`, `flext-type-system`, `flext-agent-strict-rules`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T5-T9)
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 10-12
  - **Blocked By**: Tasks 2, 3

  **References**:
  - `.claude/skills/flext-strict-typing/SKILL.md` Rule 1 — Complete replacement table (`Any` → `t.*`)
  - `flext-core/src/flext_core/typings.py` — Source of truth for `t.*` aliases
  - `flext-core/src/flext_core/result.py` — `FlextResult` inherits from `FlextRuntime.RuntimeResult`; `returns` library injects `Any` at boundary
  - `flext-core/src/flext_core/container.py` — `dependency_injector` injects `Any`
  - `flext-core/src/flext_core/loggings.py` — `structlog` injects `Any` via `BoundLogger`

  **Acceptance Criteria**:
  - [ ] `grep -rn '\bAny\b' flext-core/src/flext_core/*.py | grep -v 'TYPE_CHECKING\|JUSTIFIED\|__all__' | wc -l` — 0
  - [ ] `cd flext-core && make check` — exit 0
  - [ ] `cd flext-core && pytest tests/ -x -q` — 0 failures

  ```
  Scenario: Zero Any in facade files
    Tool: Bash
    Steps:
      1. Run `grep -rn '\bAny\b' flext-core/src/flext_core/*.py | grep -v 'TYPE_CHECKING\|JUSTIFIED\|__all__'`
      2. Assert output is empty
      3. Run `cd flext-core && make check`
    Expected Result: 0 violations. make check exit 0.
    Evidence: .sisyphus/evidence/task-4-facade-any-purge.txt

  Scenario: Third-party boundaries justified
    Tool: Bash
    Steps:
      1. Run `grep -rn 'JUSTIFIED' flext-core/src/flext_core/*.py`
      2. Each line MUST have: library name, URL citation, and `# type: ignore[...]`
    Expected Result: All JUSTIFIED lines have proper citations
    Evidence: .sisyphus/evidence/task-4-justified-suppressions.txt
  ```

  **Commit**: YES (group with T5-T9 as Wave 1 commit)
  - Message: `refactor(flext-core): purge Any/object/dict[str,Any] across all modules`

- [ ] 5. Replace Any/object in _models/ Directory

  **What to do**:
  - Target: ALL 16 files in `flext-core/src/flext_core/_models/` (~4,100 lines total)
  - Files: `base.py` (560), `collections.py` (840), `container.py` (333), `containers.py` (205), `context.py` (791), `cqrs.py` (434), `decorators.py` (45), `domain_event.py` (131), `entity.py` (260), `generic.py` (366), `handler.py` (444), `mixin.py` (67), `service.py` (274), `settings.py` (1048), `__init__.py` (16)
  - Same replacement rules as T4 — use `t.*` contracts from replacement table
  - `_models/settings.py` (1048 lines) is the largest — handle carefully, annotation-only
  - Update corresponding test files
  - Run `make check` after all replacements

  **Must NOT do**: Change model behavior, add/remove fields, modify validators.

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`flext-strict-typing`, `pydantic-v2-patterns`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T4, T6-T9)
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 10-12
  - **Blocked By**: Tasks 2, 3

  **References**:
  - `flext-core/src/flext_core/_models/base.py` — Base Pydantic models (560 lines)
  - `flext-core/src/flext_core/_models/settings.py` — Settings models (1048 lines, largest file)
  - `.claude/skills/flext-strict-typing/SKILL.md` Rule 1 — Replacement table

  **Acceptance Criteria**:
  - [ ] `grep -rn '\bAny\b' flext-core/src/flext_core/_models/ --include='*.py' | grep -v 'TYPE_CHECKING\|JUSTIFIED' | wc -l` — 0
  - [ ] `cd flext-core && make check` — exit 0

  ```
  Scenario: Zero Any in _models/
    Tool: Bash
    Steps:
      1. Run `grep -rn '\bAny\b' flext-core/src/flext_core/_models/ --include='*.py' | grep -v 'TYPE_CHECKING\|JUSTIFIED'`
      2. Assert empty
      3. Run `cd flext-core && make check`
    Expected Result: 0 violations. make check exit 0.
    Evidence: .sisyphus/evidence/task-5-models-any-purge.txt
  ```

  **Commit**: YES (group with Wave 1)

- [ ] 6. Replace Any/object in _utilities/ Directory

  **What to do**:
  - Target ALL 21 files in `flext-core/src/flext_core/_utilities/` (~13k lines)
  - Prioritize files with highest `object` counts: `mapper.py`, `parser.py`, `configuration.py`, `checker.py`, `domain.py`, `guards.py`
  - Replace each `object` in type position with `t.GeneralValueType` or specific `t.*` alias
  - Keep replacements annotation-only with zero behavioral changes
  - Preserve `_utilities/deprecation.py` as-is for infrastructure tooling (do NOT delete)

  **Must NOT do**: Delete or refactor `_utilities/deprecation.py`; this task is typing-only replacement.

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`flext-strict-typing`, `flext-type-system`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 10-12
  - **Blocked By**: Tasks 2, 3

  **References**:
  - `flext-core/src/flext_core/_utilities/mapper.py` — largest `_utilities` file, highest `object` count
  - `flext-core/src/flext_core/_utilities/parser.py` — secondary concentration of `object` usage
  - `flext-core/src/flext_core/_utilities/deprecation.py` — exempt infrastructure tooling

  **Acceptance Criteria**:
  - [ ] `grep -rn '\bobject\b' flext-core/src/flext_core/_utilities/ --include='*.py' | grep -v 'TYPE_CHECKING\|JUSTIFIED\|__all__\|# ' | wc -l` returns `0`
  - [ ] `cd flext-core && make check` exits `0` (or matches approved baseline)

  ```
  Scenario: _utilities object purge complete
    Tool: Bash
    Steps:
      1. Run `grep -rn '\bobject\b' flext-core/src/flext_core/_utilities/ --include='*.py' | grep -v 'TYPE_CHECKING\|JUSTIFIED\|__all__\|# '`
      2. Assert output is empty
    Expected Result: No remaining non-justified `object` annotations in `_utilities/`
    Evidence: .sisyphus/evidence/task-6-utilities-object-purge.txt
  ```

  **Commit**: YES (group with Wave 1)

- [ ] 7. Replace Any/object in _decorators/ + _dispatcher/

  **What to do**:
  - Target `flext-core/src/flext_core/_decorators/` (2 files) and `flext-core/src/flext_core/_dispatcher/` (4 files)
  - Replace the 3 known `object` violations (2 in `_decorators`, 1 in `_dispatcher`)
  - Keep scope minimal and annotation-only

  **Must NOT do**: Expand scope beyond the 6 specified files unless required by direct type dependency.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: [`flext-strict-typing`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 10-12
  - **Blocked By**: Tasks 2, 3

  **References**:
  - `flext-core/src/flext_core/_decorators/discovery.py` — decorator typing cleanup
  - `flext-core/src/flext_core/_dispatcher/reliability.py` — dispatcher typing cleanup

  **Acceptance Criteria**:
  - [ ] `grep -rn '\bobject\b' flext-core/src/flext_core/_decorators/ flext-core/src/flext_core/_dispatcher/ --include='*.py' | grep -v 'TYPE_CHECKING\|JUSTIFIED' | wc -l` returns `0`
  - [ ] `cd flext-core && make check` exits `0` (or matches approved baseline)

  ```
  Scenario: decorators and dispatcher object purge complete
    Tool: Bash
    Steps:
      1. Run `grep -rn '\bobject\b' flext-core/src/flext_core/_decorators/ flext-core/src/flext_core/_dispatcher/ --include='*.py' | grep -v 'TYPE_CHECKING\|JUSTIFIED'`
      2. Assert output is empty
    Expected Result: No remaining non-justified `object` annotations in both directories
    Evidence: .sisyphus/evidence/task-7-decorators-dispatcher-object-purge.txt
  ```

  **Commit**: YES (group with Wave 1)

- [ ] 8. Replace Any/object in flext_tests/ Package

  **What to do**:
  - Target ALL files in `flext-core/src/flext_tests/` with strict typing parity to production code
  - Replace 19 known `Any` violations using `t.*` contracts or specific concrete types
  - Apply AXIOMATIC Rule 13: tests follow the same typing discipline as production
  - Update test annotations only, without changing test behavior

  **Must NOT do**: Treat tests as exceptions to typing rules; no relaxed typing in test modules.

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`flext-strict-typing`, `testing-patterns`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 10-12
  - **Blocked By**: Tasks 2, 3

  **References**:
  - `flext-core/src/flext_tests/utilities.py` — highest `Any` concentration in tests
  - `flext-core/src/flext_tests/constants.py` — shared test constants typing
  - `CLAUDE.md` — AXIOMATIC Rule 13 (tests same discipline as production)

  **Acceptance Criteria**:
  - [ ] `grep -rn '\bAny\b' flext-core/src/flext_tests/ --include='*.py' | grep -v 'TYPE_CHECKING\|JUSTIFIED' | wc -l` returns `0`
  - [ ] `cd flext-core && pytest tests/ -x -q` exits `0` (or failures documented as pre-existing)

  ```
  Scenario: flext_tests Any purge complete
    Tool: Bash
    Steps:
      1. Run `grep -rn '\bAny\b' flext-core/src/flext_tests/ --include='*.py' | grep -v 'TYPE_CHECKING\|JUSTIFIED'`
      2. Assert output is empty
    Expected Result: No remaining non-justified `Any` annotations in `flext_tests/`
    Evidence: .sisyphus/evidence/task-8-flext-tests-any-purge.txt
  ```

  **Commit**: YES (group with Wave 1)

- [ ] 9. Replace Any/object in flext_infra/ Package

  **What to do**:
  - Target ALL files in `flext-core/src/flext_infra/` across 10 subdirectories
  - Replace 24 `Any` and 4 `object` violations with strict typed contracts
  - Apply the same typing discipline used in production modules to build tooling
  - Keep changes annotation-only without changing infrastructure behavior

  **Must NOT do**: Skip infra modules because they are tooling; they are in-scope for strict typing.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: [`flext-strict-typing`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 10-12
  - **Blocked By**: Tasks 2, 3

  **References**:
  - `flext-core/src/flext_infra/` — full infra package scope
  - `flext-core/src/flext_infra/codegen/` — representative subdirectory with typing debt

  **Acceptance Criteria**:
  - [ ] `grep -rn '\bAny\b' flext-core/src/flext_infra/ --include='*.py' | grep -v 'TYPE_CHECKING\|JUSTIFIED' | wc -l` returns `0`
  - [ ] `cd flext-core && make check` exits `0` (or matches approved baseline)

  ```
  Scenario: flext_infra Any purge complete
    Tool: Bash
    Steps:
      1. Run `grep -rn '\bAny\b' flext-core/src/flext_infra/ --include='*.py' | grep -v 'TYPE_CHECKING\|JUSTIFIED'`
      2. Assert output is empty
    Expected Result: No remaining non-justified `Any` annotations in `flext_infra/`
    Evidence: .sisyphus/evidence/task-9-flext-infra-any-purge.txt
  ```

  **Commit**: YES (group with Wave 1)

### Wave 2: Inline Types + None Cleanup + JSON Migration (Parallel — 3 tasks)

- [ ] 10. Replace Inline Composed Types with t.* References

  **What to do**:
  - Sweep all source for inline composed unions `X | Y` that are not simple `| None`
  - Extract each composed type into `typings.py` as named aliases, then reference as `t.NewAlias`
  - Keep simple nullable forms (for example `str | None`) inline for Task 11 review
  - Prioritize multi-type unions such as `str | int`, `dict | list`, `BaseModel | None | dict`

  **Must NOT do**: Move `| None` patterns into `typings.py`; this task handles non-None composed unions only.

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`flext-strict-typing`, `flext-type-system`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Tasks 13-15
  - **Blocked By**: Tasks 4-9

  **References**:
  - `flext-core/src/flext_core/typings.py` — destination for extracted composed aliases
  - `flext-core/src/flext_core/_models/context.py` — heavy `| None` usage to avoid misclassification

  **Acceptance Criteria**:
  - [ ] `grep -rn ' | ' src/ --include='*.py' | grep -v typings.py | grep -v '| None' | grep -v '# ' | grep -v 'or' | wc -l` returns `0`
  - [ ] `cd flext-core && make check` exits `0`

  ```
  Scenario: inline non-None composed unions extracted
    Tool: Bash
    Steps:
      1. Run `grep -rn ' | ' src/ --include='*.py' | grep -v typings.py | grep -v '| None' | grep -v '# ' | grep -v 'or'`
      2. Assert output is empty
    Expected Result: No non-None inline composed unions remain outside `typings.py`
    Evidence: .sisyphus/evidence/task-10-inline-composed-types.txt
  ```

  **Commit**: YES (group with Wave 2)
  - Message: `refactor(flext-core): replace inline types and json operations with t.*/Pydantic`

- [ ] 11. Audit | None Usage — Remove Gratuitous, Keep Business-Required

  **What to do**:
  - Review each `| None` usage and classify as business-justified or gratuitous
  - Keep justified nullable usage inline in code files
  - Replace gratuitous nullable flows with `FlextResult`-based patterns where applicable
  - Enforce rule: no `| None` aliases in `typings.py`

  **Must NOT do**: Blanket-remove all nullable types; preserve business-required nullable semantics.

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`flext-strict-typing`, `flext-type-system`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Tasks 13-15
  - **Blocked By**: Tasks 4-9

  **References**:
  - `flext-core/src/flext_core/typings.py` — forbidden location for `| None` aliases
  - `flext-core/src/flext_core/_models/context.py` — nullable-heavy business model fields

  **Acceptance Criteria**:
  - [ ] `grep -rn '\| None' flext-core/src/flext_core/typings.py --include='*.py' | wc -l` returns `0`
  - [ ] All remaining `| None` usages outside `typings.py` are business-justified

  ```
  Scenario: nullable usage policy enforced
    Tool: Bash
    Steps:
      1. Run `grep -rn '\| None' flext-core/src/flext_core/typings.py --include='*.py'`
      2. Assert output is empty
    Expected Result: No `| None` usage in `typings.py`
    Evidence: .sisyphus/evidence/task-11-none-audit.txt
  ```

  **Commit**: YES (group with Wave 2)

- [ ] 12. Replace json.loads/dumps with Pydantic JSON Functions

  **What to do**:
  - Replace raw `json.loads`/`json.dumps` with `TypeAdapter.validate_json()`, `model_validate_json()`, and `model_dump_json()` where applicable
  - Cover all listed locations in `runtime.py`, `flext_tests`, and `flext_infra`
  - For non-model JSON parsing in tooling, allow `json.loads` only when followed by immediate model validation with no raw dict propagation

  **Must NOT do**: Leave raw JSON operations that produce untyped dict intermediaries.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: [`pydantic-v2-patterns`, `flext-strict-typing`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Tasks 13-15
  - **Blocked By**: Tasks 4-9

  **References**:
  - `flext-core/src/flext_core/runtime.py` — multiple JSON operations in runtime path
  - `flext-core/src/flext_infra/json_io.py` — infra JSON I/O helpers
  - `flext-core/src/flext_tests/files.py` — JSON use in test utilities

  **Acceptance Criteria**:
  - [ ] `grep -rn 'json\.loads\|json\.dumps' src/ --include='*.py' | grep -v '# Pydantic\|model_validate\|model_dump' | wc -l` returns `0`
  - [ ] `cd flext-core && make check` exits `0`

  ```
  Scenario: raw json operations migrated
    Tool: Bash
    Steps:
      1. Run `grep -rn 'json\.loads\|json\.dumps' src/ --include='*.py' | grep -v '# Pydantic\|model_validate\|model_dump'`
      2. Assert output is empty
    Expected Result: No unjustified raw `json.loads`/`json.dumps` remain
    Evidence: .sisyphus/evidence/task-12-json-migration.txt
  ```

  **Commit**: YES (group with Wave 2)

### Wave 3: Pydantic v2 Internal State (Parallel — 3 tasks)

- [ ] 13. Migrate Bare self._x to PrivateAttr in _models/

  **What to do**:
  - Find all bare `self._x = value` assignments in BaseModel subclasses under `_models/`
  - Declare each internal attribute as `_x: type = PrivateAttr(default=...)` at class level
  - Move initialization logic to `model_post_init` where needed
  - Preserve runtime behavior while changing only internal state declaration pattern

  **Must NOT do**: Keep bare private assignments in BaseModel subclasses without `PrivateAttr` declaration.

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`pydantic-v2-patterns`, `flext-strict-typing`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: Tasks 16-19
  - **Blocked By**: Tasks 10-12

  **References**:
  - `flext-core/src/flext_core/_models/` — target directory for PrivateAttr migration
  - `pydantic.PrivateAttr` documentation — required internal state pattern

  **Acceptance Criteria**:
  - [ ] `grep -rn 'self\._[a-z].*=' flext-core/src/flext_core/_models/ --include='*.py' | grep -v PrivateAttr | grep -v model_post_init | wc -l` returns `0`
  - [ ] `cd flext-core && make check` exits `0`

  ```
  Scenario: _models private state migrated
    Tool: Bash
    Steps:
      1. Run `grep -rn 'self\._[a-z].*=' flext-core/src/flext_core/_models/ --include='*.py' | grep -v PrivateAttr | grep -v model_post_init`
      2. Assert output is empty
    Expected Result: No bare private assignments remain in `_models/` BaseModel classes
    Evidence: .sisyphus/evidence/task-13-models-privateattr.txt
  ```

  **Commit**: YES (group with Wave 3)
  - Message: `refactor(flext-core): migrate bare self._x to PrivateAttr, remove *Config classes`

- [ ] 14. Migrate Bare self._x to PrivateAttr in Facade Files

  **What to do**:
  - Audit facade files and `_dispatcher/` for bare `self._x` assignments
  - Migrate BaseModel subclasses to class-level `PrivateAttr` plus `model_post_init` initialization
  - Leave non-BaseModel plain Python classes unchanged where private `__init__` state is valid

  **Must NOT do**: Force `PrivateAttr` into non-BaseModel classes.

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`pydantic-v2-patterns`, `flext-strict-typing`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: Tasks 16-19
  - **Blocked By**: Tasks 10-12

  **References**:
  - `flext-core/src/flext_core/container.py` — high volume of private assignments
  - `flext-core/src/flext_core/runtime.py` — runtime private state
  - `flext-core/src/flext_core/_dispatcher/` — include dispatcher private state in scope

  **Acceptance Criteria**:
  - [ ] `grep -rn 'self\._[a-z].*=' flext-core/src/flext_core/*.py flext-core/src/flext_core/_dispatcher/ --include='*.py' | grep -v PrivateAttr | grep -v model_post_init | grep -v '__init__.*# non-model' | wc -l` returns `0` for BaseModel subclasses
  - [ ] `cd flext-core && make check` exits `0`

  ```
  Scenario: facade private state migrated
    Tool: Bash
    Steps:
      1. Run `grep -rn 'self\._[a-z].*=' flext-core/src/flext_core/*.py flext-core/src/flext_core/_dispatcher/ --include='*.py' | grep -v PrivateAttr | grep -v model_post_init | grep -v '__init__.*# non-model'`
      2. Assert output is empty or documented as non-model class usage
    Expected Result: All BaseModel private state uses `PrivateAttr`
    Evidence: .sisyphus/evidence/task-14-facade-privateattr.txt
  ```

  **Commit**: YES (group with Wave 3)

- [ ] 15. Verify ConfigDict Usage — No Old-Style class Config

  **What to do**:
  - Verify that no BaseModel subclasses use legacy `class Config:`
  - If any are found, migrate to `model_config = ConfigDict(...)`
  - Confirm settings classes use `BaseSettings` with `SettingsConfigDict`

  **Must NOT do**: Leave legacy `class Config` declarations in Pydantic models.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`pydantic-v2-patterns`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: Tasks 16-19
  - **Blocked By**: Tasks 10-12

  **References**:
  - `flext-core/src/` — verification scope for legacy Pydantic config pattern

  **Acceptance Criteria**:
  - [ ] `grep -rn 'class Config:' flext-core/src/ --include='*.py' | wc -l` returns `0`
  - [ ] Settings classes use `BaseSettings` + `SettingsConfigDict`

  ```
  Scenario: no legacy class Config remains
    Tool: Bash
    Steps:
      1. Run `grep -rn 'class Config:' flext-core/src/ --include='*.py'`
      2. Assert output is empty
    Expected Result: Zero `class Config:` declarations in src
    Evidence: .sisyphus/evidence/task-15-configdict-verification.txt
  ```

  **Commit**: YES (group with Wave 3)

### Wave 4: Pydantic v2 Field Enrichment (Parallel — 4 tasks)

- [ ] 16. Add Field() Metadata to _models/ (description/title/examples)

  **What to do**:
  - Add `description=` to every `Field()` call in `flext-core/src/flext_core/_models/`
  - Wrap defaulted model attributes lacking `Field()` as `Field(default=..., description=...)`
  - Add `title=` and `examples=` for non-obvious or complex fields

  **Must NOT do**: Leave `Field()` in `_models/` without `description=` metadata.

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`pydantic-v2-patterns`, `flext-strict-typing`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4
  - **Blocks**: Tasks 20-22
  - **Blocked By**: Tasks 13-15

  **References**:
  - `flext-core/src/flext_core/_models/` — target scope for metadata enrichment
  - `AXIOMATIC Rule 12` — mandatory use of Pydantic feature set

  **Acceptance Criteria**:
  - [ ] `grep -rn 'Field(' flext-core/src/flext_core/_models/ --include='*.py' | grep -v 'description=' | wc -l` returns `0`
  - [ ] `cd flext-core && make check` exits `0`

  ```
  Scenario: _models field metadata enriched
    Tool: Bash
    Steps:
      1. Run `grep -rn 'Field(' flext-core/src/flext_core/_models/ --include='*.py' | grep -v 'description='`
      2. Assert output is empty
    Expected Result: All `_models` Field declarations include `description=`
    Evidence: .sisyphus/evidence/task-16-models-field-metadata.txt
  ```

  **Commit**: YES (group with Wave 4)
  - Message: `refactor(flext-core): enrich Field() metadata and minimize custom validators`

- [ ] 17. Add Field() Metadata to Facade Models + flext_tests Models

  **What to do**:
  - Enrich remaining `Field()` calls outside `_models/` in `flext_core` facade modules and `flext_tests`
  - Add `description=` universally and add `title=`/`examples=` where clarity requires it
  - Keep all changes annotation/schema metadata only

  **Must NOT do**: Modify model behavior while adding schema metadata.

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`pydantic-v2-patterns`, `testing-patterns`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4
  - **Blocks**: Tasks 20-22
  - **Blocked By**: Tasks 13-15

  **References**:
  - `flext-core/src/flext_core/` — facade model files in scope
  - `flext-core/src/flext_tests/` — test models in scope

  **Acceptance Criteria**:
  - [ ] `grep -rn 'Field(' flext-core/src/ --include='*.py' | grep -v 'description=' | wc -l` returns `0`
  - [ ] `cd flext-core && make check` exits `0`

  ```
  Scenario: global field metadata enriched
    Tool: Bash
    Steps:
      1. Run `grep -rn 'Field(' flext-core/src/ --include='*.py' | grep -v 'description='`
      2. Assert output is empty
    Expected Result: All Field declarations in src include `description=`
    Evidence: .sisyphus/evidence/task-17-global-field-metadata.txt
  ```

  **Commit**: YES (group with Wave 4)

- [ ] 18. Minimize Custom Validators — Prefer Built-in Constraints

  **What to do**:
  - Audit all `@field_validator`, `@model_validator`, and legacy `@validator` usage
  - Replace simple checks with built-in constraints (`ge`, `le`, `min_length`, `max_length`, `pattern`, `gt`, `lt`)
  - Convert remaining v1 `@validator` decorators to v2 `@field_validator`
  - Keep complex business validators when built-in constraints cannot express logic

  **Must NOT do**: Remove complex business-rule validators that cannot be represented safely with Field constraints.

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`pydantic-v2-patterns`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4
  - **Blocks**: Tasks 20-22
  - **Blocked By**: Tasks 13-15

  **References**:
  - `flext-core/src/` — validator migration and simplification scope

  **Acceptance Criteria**:
  - [ ] `grep -rn '@validator' flext-core/src/ --include='*.py' | wc -l` returns `0`
  - [ ] Remaining validators are v2-compliant and business-justified

  ```
  Scenario: validator migration complete
    Tool: Bash
    Steps:
      1. Run `grep -rn '@validator' flext-core/src/ --include='*.py'`
      2. Assert output is empty
    Expected Result: No legacy v1 `@validator` decorators remain
    Evidence: .sisyphus/evidence/task-18-validator-migration.txt
  ```

  **Commit**: YES (group with Wave 4)

- [ ] 19. Replace Unnecessary @property with @computed_field

  **What to do**:
  - Review `@property` usage in BaseModel subclasses only
  - Replace computed-from-fields properties with `@computed_field`
  - Keep `@property` for Protocol declarations and stateful/external access patterns

  **Must NOT do**: Convert Protocol `@property` declarations to `@computed_field`.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: [`pydantic-v2-patterns`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4
  - **Blocks**: Tasks 20-22
  - **Blocked By**: Tasks 13-15

  **References**:
  - `flext-core/src/flext_core/protocols.py` — Protocol `@property` patterns (not candidates)
  - `flext-core/src/flext_core/_models/` — BaseModel property candidates

  **Acceptance Criteria**:
  - [ ] Zero BaseModel `@property` members remain that should be `@computed_field`
  - [ ] Protocol property definitions remain intact

  ```
  Scenario: computed field conversion complete
    Tool: Bash
    Steps:
      1. Run `grep -rn '@property' flext-core/src/flext_core/ --include='*.py'`
      2. Manually verify remaining matches are Protocol definitions or justified stateful properties
    Expected Result: No missed `@computed_field` candidates in BaseModel subclasses
    Evidence: .sisyphus/evidence/task-19-computed-field-audit.txt
  ```

  **Commit**: YES (group with Wave 4)

### Wave 5: Cleanup + Enforcement (Parallel — 3 tasks)

- [ ] 20. Remove Init Helpers, Getters/Setters, Wrappers in Models

  **What to do**:
  - Replace `to_dict` wrappers with `model_dump()` and `from_dict` wrappers with `model_validate()`
  - Remove trivial getter/setter wrappers in model layers where direct field access is sufficient
  - Eliminate non-business helper wrappers across listed files
  - If Protocols define wrapper interfaces, update contract names consistently (for example `to_dict` to `model_dump`)

  **Must NOT do**: Remove wrappers that contain real business logic.

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`pydantic-v2-patterns`, `flext-strict-typing`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 5
  - **Blocks**: Task 23
  - **Blocked By**: Tasks 16-19

  **References**:
  - `flext-core/src/flext_core/_models/collections.py` — helper/wrapper concentration
  - `flext-core/src/flext_core/protocols.py` — interface contract alignment for dump/validate naming
  - `flext-core/src/flext_core/_utilities/model.py` — legacy dict wrapper methods

  **Acceptance Criteria**:
  - [ ] `grep -rn 'def to_dict\|def from_dict\|def get_\|def set_\|def _get_\|def _set_' flext-core/src/flext_core/ --include='*.py' | grep -v 'test\|# JUSTIFIED' | wc -l` returns `0`
  - [ ] `cd flext-core && make check` exits `0`

  ```
  Scenario: wrappers/helpers removed
    Tool: Bash
    Steps:
      1. Run `grep -rn 'def to_dict\|def from_dict\|def get_\|def set_\|def _get_\|def _set_' flext-core/src/flext_core/ --include='*.py' | grep -v 'test\|# JUSTIFIED'`
      2. Assert output is empty
    Expected Result: Legacy wrapper/helper methods are removed or justified
    Evidence: .sisyphus/evidence/task-20-wrapper-cleanup.txt
  ```

  **Commit**: YES (group with Wave 5)
  - Message: `refactor(flext-core): remove wrappers/helpers, audit suppressions, enforce constants`

- [ ] 21. Suppression Audit — Justify or Remove # type: ignore / # noqa

  **What to do**:
  - Audit every `# type: ignore` and `# noqa` suppression in scope
  - Remove suppressions when underlying issues can be fixed safely
  - Narrow and justify unavoidable suppressions with `# JUSTIFIED: <library> — <URL citation>`
  - Generate `.reports/suppression-audit.csv` with file, line, code, justification, action

  **Must NOT do**: Leave broad or unexplained suppression directives.

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`flext-quality-gates`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 5
  - **Blocks**: Task 23
  - **Blocked By**: Tasks 16-19

  **References**:
  - `flext-core/src/flext_infra/codegen/` — high suppression density area
  - `.reports/suppression-audit.csv` — required audit output

  **Acceptance Criteria**:
  - [ ] Every remaining `# type: ignore` includes `# JUSTIFIED` with URL citation
  - [ ] `.reports/suppression-audit.csv` exists and is complete

  ```
  Scenario: suppression audit complete
    Tool: Bash
    Steps:
      1. Run `grep -rn '# type: ignore\|# noqa' flext-core/src/ --include='*.py'`
      2. Verify each remaining suppression has `# JUSTIFIED: ... <URL>` and corresponding CSV entry
    Expected Result: All suppressions removed or justified with traceable evidence
    Evidence: .sisyphus/evidence/task-21-suppression-audit.txt
  ```

  **Commit**: YES (group with Wave 5)

- [ ] 22. Ensure Enum/Mapping/Literal from constants.py Only

  **What to do**:
  - Verify enum definitions are centralized in `constants.py` (or `_utilities/enum.py` when utility-specific)
  - Move misplaced enum declarations outside approved locations
  - Ensure `Literal` declarations reference constants instead of inline string lists where applicable
  - Inspect `_utilities/enum.py` before moving anything; treat as legitimate utility module unless duplication is confirmed

  **Must NOT do**: Move utility enum helpers from `_utilities/enum.py` without confirming they are duplicated enum definitions.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: [`flext-strict-typing`, `rules-src`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 5
  - **Blocks**: Task 23
  - **Blocked By**: Tasks 16-19

  **References**:
  - `flext-core/src/flext_core/constants.py` — canonical enum home
  - `flext-core/src/flext_core/_utilities/enum.py` — approved utility enum module

  **Acceptance Criteria**:
  - [ ] `grep -rn 'class.*StrEnum\|class.*IntEnum' flext-core/src/flext_core/ --include='*.py' | grep -v constants.py | grep -v '_utilities/enum.py' | wc -l` returns `0`
  - [ ] Enum/Literal definitions align with constants centralization rule

  ```
  Scenario: enum centralization enforced
    Tool: Bash
    Steps:
      1. Run `grep -rn 'class.*StrEnum\|class.*IntEnum' flext-core/src/flext_core/ --include='*.py' | grep -v constants.py | grep -v '_utilities/enum.py'`
      2. Assert output is empty
    Expected Result: No stray enum class definitions outside approved modules
    Evidence: .sisyphus/evidence/task-22-enum-centralization.txt
  ```

  **Commit**: YES (group with Wave 5)

### Wave 6: Integration Verification (Sequential — 3 tasks)

- [ ] 23. Full 4-Linter Clean Verification on flext-core

  **What to do**:
  - Run full linter stack on `flext-core/src/`: `ruff check`, `ruff format --check`, `pyrefly check`, `make check`
  - Fix any errors surfaced by cross-wave integration
  - Use this task as the mandatory integration gate before tests and consumer validation

  **Must NOT do**: Proceed to test/consumer verification with unresolved linter failures.

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`flext-quality-gates`]

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 6 (sequential)
  - **Blocks**: Task 24
  - **Blocked By**: Tasks 20-22

  **References**:
  - `flext-core/Makefile` — integrated quality gates
  - `flext-core/src/` — full linter target scope

  **Acceptance Criteria**:
  - [ ] `ruff check`, `ruff format --check`, `python -m pyrefly check`, and `make check` all exit `0`
  - [ ] Zero remaining linter errors across flext-core scope

  ```
  Scenario: full linter gate passes
    Tool: Bash
    Steps:
      1. Run `cd flext-core && ruff check src/`
      2. Run `cd flext-core && ruff format --check src/`
      3. Run `cd flext-core && python -m pyrefly check src/flext_core/`
      4. Run `cd flext-core && make check`
    Expected Result: All four commands exit 0
    Evidence: .sisyphus/evidence/task-23-full-linter-verification.txt
  ```

  **Commit**: YES (group with Wave 6)
  - Message: `test(flext-core): verify full 4-linter compliance and consumer project compatibility`

- [ ] 24. Full Test Suite Pass Verification

  **What to do**:
  - Run `cd flext-core && pytest tests/ -x -q`
  - If failures appear, classify as pre-existing or introduced by refactor
  - Fix only annotation-caused regressions; do not make behavioral changes
  - Document confirmed pre-existing failures in `.reports/pre-existing-test-failures.txt`

  **Must NOT do**: Hide test failures without classification and documentation.

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`testing-patterns`]

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 6 (sequential)
  - **Blocks**: Task 25
  - **Blocked By**: Task 23

  **References**:
  - `flext-core/tests/` — primary verification suite
  - `.reports/pre-existing-test-failures.txt` — required if baseline failures remain

  **Acceptance Criteria**:
  - [ ] `cd flext-core && pytest tests/ -x -q` exits `0`, or all failures are documented as pre-existing
  - [ ] Any remediation preserves behavioral freeze

  ```
  Scenario: full test gate passes or is documented
    Tool: Bash
    Steps:
      1. Run `cd flext-core && pytest tests/ -x -q`
      2. If failing, append confirmed pre-existing failures to `.reports/pre-existing-test-failures.txt`
    Expected Result: Tests pass, or every failure is classified and documented
    Evidence: .sisyphus/evidence/task-24-test-suite-verification.txt
  ```

  **Commit**: YES (group with Wave 6)

- [ ] 25. Consumer Project Smoke Tests

  **What to do**:
  - Run `make check` in `flext-ldap/`, `flext-meltano/`, and `flext-tap-oracle/`
  - Diagnose failures for compatibility impact from flext-core type/interface changes
  - Fix consumer import/annotation breakages introduced by refactoring
  - Document pre-existing consumer failures if unrelated to this refactor

  **Must NOT do**: Close compatibility gate without running all three consumer checks.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: [`flext-strict-typing`]

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 6 (sequential)
  - **Blocks**: Task 26, F1-F4
  - **Blocked By**: Task 24

  **References**:
  - `flext-ldap/` — consumer compatibility target
  - `flext-meltano/` — consumer compatibility target
  - `flext-tap-oracle/` — consumer compatibility target

  **Acceptance Criteria**:
  - [ ] `make check` exits `0` in all 3 consumer projects
  - [ ] Any remaining failures are documented as pre-existing and not caused by flext-core refactor

  ```
  Scenario: consumer smoke tests pass
    Tool: Bash
    Steps:
      1. Run `cd flext-ldap && make check`
      2. Run `cd flext-meltano && make check`
      3. Run `cd flext-tap-oracle && make check`
    Expected Result: All three consumer checks exit 0
    Evidence: .sisyphus/evidence/task-25-consumer-smoke-tests.txt
  ```

  **Commit**: YES (group with Wave 6)

### Wave 7: MRO Compliance Audit (Sequential — 1 task)

- [ ] 26. MRO/Structural Compliance Audit — Flag Non-Conforming Modules

  **What to do**:
  - Audit all `flext_core` modules for AXIOMATIC Rule 11 structural compliance
  - Confirm whether each module follows single nested class with MRO + Pydantic v2 BaseModel pattern
  - For non-conforming modules, create GitHub issues with required structural change descriptions
  - Generate `.reports/mro-compliance-audit.md` covering conforming and non-conforming modules

  **Must NOT do**: Perform structural refactors in this plan; only audit and flag.

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`flext-type-system`, `flext-strict-typing`]

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 7 (sequential)
  - **Blocks**: F1-F4
  - **Blocked By**: Task 25

  **References**:
  - `flext-core/src/flext_core/` — full module audit scope
  - `.reports/mro-compliance-audit.md` — required audit output artifact

  **Acceptance Criteria**:
  - [ ] `.reports/mro-compliance-audit.md` exists with assessment for every module
  - [ ] Non-conforming modules are tracked with linked issue IDs

  ```
  Scenario: mro structural audit completed
    Tool: Bash
    Steps:
      1. Run module inventory audit across `flext-core/src/flext_core/`
      2. Verify `.reports/mro-compliance-audit.md` includes conforming and non-conforming module lists
    Expected Result: Complete Rule 11 compliance map and issue-backed gaps
    Evidence: .sisyphus/evidence/task-26-mro-compliance-audit.txt
  ```

  **Commit**: YES (group with Wave 7)
  - Message: `docs(flext-core): MRO compliance audit — flag non-conforming modules`

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Rejection → fix → re-run.

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, run command). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run `make check` + `pytest tests/`. Review all changed files for: `Any`, `object`, `dict[str, Any]`, bare `self._x`, raw `json.loads`, inner `class Config`. Check AI slop: excessive comments, over-abstraction, generic names.
  Output: `Build [PASS/FAIL] | Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [ ] F3. **Real QA** — `unspecified-high`
  Start from clean state. Run ALL 4 linters on flext-core. Run full test suite. Run `make check` on 3 consumer projects. Verify ZERO errors across all.
  Output: `Linters [4/4 pass] | Tests [N/N pass] | Consumers [3/3 pass] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  For each task: verify annotation-only changes (no behavioral changes). Check "Must NOT do" compliance. Detect scope creep: logic changes, new features, MRO restructuring that shouldn't have happened.
  Output: `Tasks [N/N compliant] | Behavioral Changes [CLEAN/N issues] | VERDICT`

---

## Commit Strategy

Each wave produces ONE atomic commit after all its tasks pass linters:

| Wave | Commit Message | Pre-commit |
|------|---------------|------------|
| 0 | `chore(flext-core): establish refactoring baseline and type alias completeness` | `make check` |
| 1 | `refactor(flext-core): purge Any/object/dict[str,Any] across all modules` | `make check` |
| 2 | `refactor(flext-core): replace inline types and json operations with t.*/Pydantic` | `make check` |
| 3 | `refactor(flext-core): migrate bare self._x to PrivateAttr, remove *Config classes` | `make check` |
| 4 | `refactor(flext-core): enrich Field() metadata and minimize custom validators` | `make check` |
| 5 | `refactor(flext-core): remove wrappers/helpers, audit suppressions, enforce constants` | `make check` |
| 6 | `test(flext-core): verify full 4-linter compliance and consumer project compatibility` | `make check && make test` |
| 7 | `docs(flext-core): MRO compliance audit — flag non-conforming modules` | — |

---

## Success Criteria

### Verification Commands
```bash
# All 4 linters clean
cd flext-core && make check                    # Expected: exit 0
cd flext-core && pytest tests/ -x -q           # Expected: 0 failures

# Zero Any/object violations
grep -rn '\bAny\b' src/flext_core/ --include='*.py' | grep -v 'TYPE_CHECKING\|__all__\|# JUSTIFIED' | wc -l
# Expected: 0

# Zero bare self._x (not PrivateAttr)
grep -rn 'self\._[a-z].*=' src/flext_core/ --include='*.py' | grep -v 'PrivateAttr\|model_post_init\|__init_subclass__' | wc -l
# Expected: 0 (or all justified)

# Zero raw json operations
grep -rn 'json\.loads\|json\.dumps' src/flext_core/ --include='*.py' | wc -l
# Expected: 0

# Consumer smoke tests
cd flext-ldap && make check                    # Expected: exit 0
cd flext-meltano && make check                 # Expected: exit 0
cd flext-tap-oracle && make check              # Expected: exit 0
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All 4 linters pass clean
- [ ] All tests pass
- [ ] All consumer projects pass
- [ ] Suppression audit report generated
- [ ] MRO compliance audit report generated
