# ARCHIVED — Subsumed by modernization-reorg-execution.md

# Workspace Final Standardization — Per-Project Complete Fix

## TL;DR

> **Quick Summary**: ONE consolidated plan replaces all 45 existing plans. Each of the 33 projects gets one task that audits and fixes EVERYTHING (facades, Pydantic, typing, Make) in a single pass, organized by project dependency order.
>
> **Deliverables**:
> - CLAUDE.md updated with session learnings (§2, §3, §9, §10)
> - 3 skills fixed (4 contradictions), 1 new skill created
> - ALL 45 existing plans archived
> - ALL 33 projects fully standardized (facades, typing, pydantic, make)
>
> **Estimated Effort**: XL
> **Parallel Execution**: YES — 5 waves with sub-sequencing
> **Critical Path**: T1-T5 → T6 → T7 → T9 → Wave 3 → Wave 4 → F1-F4

---

## Context

### Original Request
Analyze all Feb 28 sessions (6 total, 2300+ messages), plans (45 files), and Sisyphus learnings (8 notepads, 2500+ lines) to:
1. Improve CLAUDE.md and project skills based on real execution findings
2. Create ONE plan to finish ALL remaining standardization — organized BY PROJECT, not by facade type

### Session Analysis (Feb 28, 2026)
- **6 sessions**: 1 Prometheus (planning), 5 Atlas (parallel execution)
- **15 commits**: 10 refactor (remove Any/object/cast), 4 chore (migration), 1 revert
- **27 submodules dirty** — fix forward (no cleanup)

### Key Findings from Learnings
1. **Scope Creep** — Subagents modify files outside boundaries (5+ occurrences)
2. **Duplicate First Tasks** — Same CLAUDE.md commit applied 3+ times across sessions
3. **Already-Complete Tasks** — Sessions wasted rediscovering committed work
4. **MRO BROKEN Everywhere** — Types worst (13/14 wrong), utilities (10+), models (5+)
5. **Naming Inconsistency** — FlextMeltanoTapXxx in 6 projects (~25-30 class renames needed)
6. **Import Violations** — Rules 4D, 7, 11 most common

### Metis Review (Critical Findings)
1. **Types facade is 93% BROKEN** — 13/14 integration projects use single inheritance instead of dual
2. **Platform chain is 20% done** — Only Protocols chained through platform parents; 4 other facades still single
3. **3 P0 broken references** — `_t` (tap-oracle-oic), `_FlextTypes` (target-oracle-wms), `ft` (web) cause ImportError
4. **Wave sub-sequencing required** — cli→meltano, ldif→ldap, web→api→auth cannot be parallel
5. **4 skill contradictions** — alias table (single vs dual), WmsConstants naming, patterns outdated example, CLAUDE.md ambiguity
6. **Pydantic v2 is 97% done** — Only model_rebuild (9 files) and 3 test Config classes remain
7. **133 files with `: object`** — Each needs context-specific replacement (22x bigger than `: Any` scope)
8. **FactoryCallable is NOT a Pydantic blocker** — Was misidentified; only used in 6 flext-core files

---

## Work Objectives

### Core Objective
Standardize ALL 33 FLEXT projects — organized per-project, one task per project, fixing EVERYTHING in a single pass.

### Concrete Deliverables
- CLAUDE.md with §2, §3, §9, §10 additions from learnings
- 3 skills fixed (flext-architecture-layers: 4 contradictions, flext-patterns, flext-import-rules)
- 1 new skill created (flext-plan-hygiene)
- 45 plans archived → this becomes the ONLY active plan
- 33 projects with correct: facades/MRO, naming, imports, typing, Pydantic v2, Make alignment

### Definition of Done
- [ ] `make check PROJECT=<name>` passes for every project
- [ ] `make test PROJECT=<name>` passes for every project
- [ ] MRO verification correct for all projects (all 5 facades)
- [ ] No `FlextMeltanoTap*` or `FlextMeltanoTarget*` class names remain
- [ ] All `__init__.py` lazy loaders match actual class names
- [ ] `make validate VALIDATE_SCOPE=workspace` passes
- [ ] CLAUDE.md reflects all learned rules
- [ ] All 45 old plans archived
- [ ] Zero broken type references (`_t`, `_FlextTypes`, `ft`)

### Must Have
- Per-project task structure (NOT per-facade-type)
- MRO: ALL 5 facades (c, m, t, u, p) inherit from ALL parent libraries to cover full namespace
- Naming: `Flext<Role><Domain><Facade>` for integration projects (no "Meltano" in name)
- Import: by CLASS NAME for inheritance, alias at module bottom only
- String references updated: `_LAZY_IMPORTS`, `__all__`, `__getattr__`
- `from __future__ import annotations` in every `.py` file
- `lsp_rename` or `lsp_find_references` for ALL class renames (no raw search-replace)

### Must NOT Have (Guardrails)
- NO touching business logic or adding new functionality
- NO organizing by facade type (everything is per-project)
- NO raw search-replace for class renames (use lsp_rename)
- NO skipping pyrefly gate (catches MRO issues that ruff/mypy miss)
- NO grouping model_rebuild removal with generic Pydantic cleanup (each is structural)
- NO starting integration Types fixes before platform parent chain is fixed
- NO modifying files outside the project boundary (scope discipline)

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed.

### Test Decision
- **Infrastructure exists**: YES (pytest + ruff + pyrefly)
- **Automated tests**: YES (tests-after) — verify existing tests still pass
- **Framework**: pytest

### QA Policy (ALL project tasks)
Every project task MUST verify:
1. `make check PROJECT=<name>` — zero exit code
2. `make test PROJECT=<name>` — zero exit code
3. MRO: `python -c "from <pkg> import m,c,t,u,p; [print(f'{a}: {[c.__name__ for c in v.__mro__]}') for a,v in [('m',m),('c',c),('t',t),('u',u),('p',p)]]"`
4. Naming: `grep -rn "class FlextMeltano" <project>/src/` — zero matches
5. Lazy loader: `python -c "from <pkg> import <NewClassName>"` — no ImportError
6. Future imports: `grep -rL "from __future__ import annotations" <project>/src/**/*.py` — zero matches

Evidence saved to `.sisyphus/evidence/task-{N}-<project>.txt`.

---

## Per-Project Templates

### Template: Integration Project (tap/target/dbt)

**Scope**: Dual inheritance (FlextMeltano*+ FlextDomain*) for ALL 5 facades.

**Steps**:
1. **Pre-flight**: Check for broken base class references (`_t`, `_FlextTypes`, alias-based). Fix immediately.
2. **For each facade** (m, c, t, u, p):
   a. Fix MRO: `class Flext<Role><Domain><Facade>(FlextMeltano<Facade>, Flext<DomainPrefix><Facade>):`
   b. Fix naming: NO "Meltano" in class name → use `lsp_rename` (maps blast radius first via `lsp_find_references`)
   c. Fix import: by CLASS NAME from parent package (not alias)
   d. Fix alias: single assignment at module bottom
   e. Fix `__all__` exports
3. **Fix `__init__.py`**: Update `_LAZY_IMPORTS` strings, `__getattr__` mappings, `TYPE_CHECKING` blocks
4. **Pydantic v2**: Fix remaining v1 patterns (class Config → ConfigDict, model_rebuild → restructure)
5. **Typing**: Replace `: Any` with proper types; replace `: object` with context-specific types (see `flext-strict-typing` Rule 1)
6. **Nuclear**: Remove fake/dead classes, unused imports
7. **Make**: Verify pyproject.toml aligns with base.mk
8. **Verify**: `make check` + `make test` + MRO verify + naming audit + lazy loader test
9. **If already correct**: Document in evidence and mark complete

**CRITICAL**: Types (t) is the heavy-lift item — 13/14 projects need structural conversion from single → dual inheritance. After dual-inheritance fix, verify no inner class name collisions via MRO inspection.

### Template: Platform/Domain/Standalone Project

**Scope**: Single inheritance from appropriate parent (not always flext-core).

**Steps**: Same 1-9 as Integration, but Step 2 uses:
- **Single inheritance**: `class Flext<Name><Facade>(Flext<Parent><Facade>):`
- **Exceptions** (chained through intermediate parent):
  - flext-meltano → FlextCli*
  - flext-api → FlextWeb*
  - flext-auth → FlextApi*
  - flext-quality → (FlextWeb*, FlextCli*) — dual platform
  - flext-ldap → FlextLdif*

### Template: Special Project

**Scope**: Case-by-case audit.
- **gruponos-meltano-native**: Verify imports match renamed integration classes (FlextTapOracle*, FlextTargetOracleWms*)
- **algar-oud-mig**: Verify facade imports from flext-ldap + flext-cli are correct
- **flexcore**: Go/Python hybrid. Verify Python facade structure only.

---

## Per-Tier Inheritance Lookup Table

> **Agents MUST consult this table** — do NOT guess inheritance chains.

### Integration Projects (tap/target/dbt) — ALL 5 Facades Dual

```
m: Flext<Role><Domain>Models(FlextMeltanoModels, Flext<Domain>Models)
c: Flext<Role><Domain>Constants(FlextMeltanoConstants, Flext<Domain>Constants)
t: Flext<Role><Domain>Types(FlextMeltanoTypes, Flext<Domain>Types)            ← BIGGEST FIX (93% broken)
u: Flext<Role><Domain>Utilities(FlextMeltanoUtilities, Flext<Domain>Utilities)
p: Flext<Role><Domain>Protocols(FlextMeltanoProtocols, Flext<Domain>Protocols)
```

### Domain Mapping

| Project suffix | Domain prefix | Import package |
|----------------|--------------|----------------|
| `-ldap` | `FlextLdap` | `flext_ldap` |
| `-ldif` | `FlextLdif` | `flext_ldif` |
| `-oracle` (no wms/oic) | `FlextDbOracle` | `flext_db_oracle` |
| `-oracle-wms` | `FlextOracleWms` | `flext_oracle_wms` |
| `-oracle-oic` | `FlextOracleOic` | `flext_oracle_oic` |

### Role Mapping

| Project type | Role prefix |
|-------------|-------------|
| `flext-tap-*` | `FlextTap` |
| `flext-target-*` | `FlextTarget` |
| `flext-dbt-*` | `FlextDbt` |

### Platform/Domain Chain Table (Non-Integration)

```
flext-cli:           FlextCli<Facade>(Flext<Facade>)              ← single from core
flext-web:           FlextWeb<Facade>(Flext<Facade>)              ← single from core
flext-meltano:       FlextMeltano<Facade>(FlextCli<Facade>)       ← chains through cli
flext-api:           FlextApi<Facade>(FlextWeb<Facade>)           ← chains through web
flext-auth:          FlextAuth<Facade>(FlextApi<Facade>)          ← chains through api
flext-quality:       FlextQuality<Facade>(FlextWeb<Facade>, FlextCli<Facade>)  ← dual platform
flext-ldif:          FlextLdif<Facade>(Flext<Facade>)             ← single from core
flext-ldap:          FlextLdap<Facade>(FlextLdif<Facade>)         ← chains through ldif
flext-db-oracle:     FlextDbOracle<Facade>(Flext<Facade>)         ← single from core
flext-oracle-wms:    FlextOracleWms<Facade>(Flext<Facade>)        ← single from core
flext-oracle-oic:    FlextOracleOic<Facade>(Flext<Facade>)        ← single from core
flext-grpc:          FlextGrpc<Facade>(Flext<Facade>)             ← single from core
flext-plugin:        FlextPlugin<Facade>(Flext<Facade>)           ← single from core
flext-observability: FlextObservability<Facade>(Flext<Facade>)    ← single from core
```

---

## Execution Strategy

### Wave Dependency Graph

```
Wave 0 (Governance — must complete before all other waves):
├── T1: Update CLAUDE.md (§2, §3, §9, §10)                                [quick]
├── T2: Fix/update skills (4 contradictions + new skill)                   [quick]
├── T3: Fix 3 P0 broken type references                                   [quick]
├── T4: Workspace infrastructure (base.mk, CI, scripts)                   [unspecified-high]
└── T5: Archive ALL 45 plans                                               [quick]

Wave 1 (Foundation — solo, after Wave 0):
└── T6: flext-core — Full standardization + model_rebuild                  [deep]

Wave 2 (L1 Projects — sub-sequenced, after Wave 1):
  Tier 1 (parallel, 9 tasks):
  ├── T7:  flext-cli                                                       [quick]
  ├── T8:  flext-web                                                       [quick]
  ├── T11: flext-ldif                                                      [quick]
  ├── T12: flext-db-oracle                                                 [quick]
  ├── T13: flext-oracle-wms                                                [quick]
  ├── T14: flext-oracle-oic                                                [quick]
  ├── T16: flext-grpc                                                      [quick]
  ├── T17: flext-plugin                                                    [quick]
  └── T18: flext-observability                                             [quick]
  Tier 2 (after dependencies, 3 tasks):
  ├── T9:  flext-meltano         (after T7: cli)                           [deep]
  ├── T10: flext-api             (after T8: web)                           [quick]
  └── T15: flext-ldap            (after T11: ldif)                         [quick]
  Tier 3 (after dependencies, 2 tasks):
  ├── T19: flext-auth            (after T10: api)                          [quick]
  └── T20: flext-quality         (after T7: cli + T8: web)                 [quick]

Wave 3 (Integration — max parallel, after Wave 2):
├── T21: flext-tap-ldap          (after T9 + T15)                          [quick]
├── T22: flext-tap-ldif          (after T9 + T11)                          [quick]
├── T23: flext-tap-oracle        (after T9 + T12)                          [quick]
├── T24: flext-tap-oracle-oic    (after T9 + T14)                          [quick]
├── T25: flext-tap-oracle-wms    (after T9 + T13)                          [quick]
├── T26: flext-target-ldap       (after T9 + T15)                          [quick]
├── T27: flext-target-ldif       (after T9 + T11)                          [quick]
├── T28: flext-target-oracle     (after T9 + T12)                          [quick]
├── T29: flext-target-oracle-oic (after T9 + T14)                          [quick]
├── T30: flext-target-oracle-wms (after T9 + T13)                          [quick]
├── T31: flext-dbt-ldap          (after T9 + T15)                          [quick]
├── T32: flext-dbt-ldif          (after T9 + T11)                          [quick]
├── T33: flext-dbt-oracle        (after T9 + T12)                          [quick]
└── T34: flext-dbt-oracle-wms    (after T9 + T13)                          [quick]

Wave 4 (Special — after Wave 3):
├── T35: gruponos-meltano-native (after T23 + T30)                        [quick]
├── T36: algar-oud-mig           (after T15 + T7)                         [quick]
└── T37: flexcore                (after T6)                                [quick]

Wave F (Final Verification — 4 parallel, after ALL):
├── F1: Plan compliance audit                                              [oracle]
├── F2: Code quality review                                                [unspecified-high]
├── F3: Full MRO workspace audit                                           [deep]
└── F4: Scope fidelity check                                               [deep]

Critical Path: T1-T5 → T6 → T7 → T9 → Wave 3 → T35 → F1-F4
Max Concurrent: 9 (Wave 2 Tier 1)
Total Tasks: 37 + 4 final = 41
```

### Dependency Matrix

| Task | Blocked By | Blocks |
|------|-----------|--------|
| T1-T5 | — | T6 |
| T6 | T1-T5 | T7-T18 |
| T7 (cli) | T6 | T9, T20 |
| T8 (web) | T6 | T10, T20 |
| T9 (meltano) | T7 | T21-T34 |
| T10 (api) | T8 | T19 |
| T11 (ldif) | T6 | T15, T22, T27, T32 |
| T12 (db-oracle) | T6 | T23, T28, T33 |
| T13 (oracle-wms) | T6 | T25, T30, T34 |
| T14 (oracle-oic) | T6 | T24, T29 |
| T15 (ldap) | T11 | T21, T26, T31 |
| T16-T18 | T6 | F1-F4 |
| T19 (auth) | T10 | F1-F4 |
| T20 (quality) | T7, T8 | F1-F4 |
| T21-T34 | T9 + domain | T35-T37 |
| T35-T37 | Wave 3 deps | F1-F4 |
| F1-F4 | ALL | — |

### Agent Dispatch Summary

| Wave | Tasks | Categories |
|------|-------|-----------|
| 0 | 5 | quick(4), unspecified-high(1) |
| 1 | 1 | deep(1) |
| 2-Tier1 | 9 | quick(9) |
| 2-Tier2 | 3 | deep(1), quick(2) |
| 2-Tier3 | 2 | quick(2) |
| 3 | 14 | quick(14) |
| 4 | 3 | quick(3) |
| F | 4 | oracle(1), unspecified-high(1), deep(2) |

### Plans to Archive (ALL 45 — this plan supersedes everything)

ci-cd-github-actions-reorg-flext, ci-cd-make-setup, code-reduction-centralization,
constants-extraction-centralization, constants-mro-centralization, deps-basemk-migration,
dispatcher-architectural-refactor, dispatcher-strict-enforcement, eliminate-any-object-types,
eliminate-object-typing, eliminate-validation-methods, fix-pyrefly-make-upgrade-pipeline,
flext-core-refactor, flext-core-startup-optimization, flext-infra-compliance-remediation,
flext-infra-namespace-migration, flext-ldif-make-test-diag-fix, flextregistry-strict-protocol-only,
flextresult-exceptions-guardians, lint-pipeline-optimization, make-feedback-remediation,
make-feedback-standardization, make-setup-editable-reconciliation, models-typing-centralization,
multi-agent-coordination-law, mypy-strict-all-projects, nuclear-fake-removal,
nuclear-fake-removal-r2, nuclear-typing-annihilation, parallel-agent-coordination,
protocols-typing-standardization, pydantic-v2-loc-annihilation, pydantic-v2-optimization,
pydantic-v2-validation-purge, pytest-optimization, release-automation-0.10.0,
scripts-refactor-config-templates, service-strict-protocol-enforcement,
strict-containers-decorators-handlers-mixins, strict-typing-ruff-cleanup,
typing-naming-standardization, typing-reorganization, utilities-typing-refactor,
workspace-green-gates-dedupe, workspace-ssot-libs-refactor

---

## TODOs

> Each task follows the Per-Project Templates defined above.
> Refer to Per-Tier Inheritance Lookup Table for expected MRO per project.
> **A task WITHOUT QA verification is INCOMPLETE.**

### Wave 0: Governance (5 tasks, parallel, must complete before Wave 1)

- [x] 1. Update CLAUDE.md — Session Learnings Integration

  **What to do**:
  - §2 Architecture Law — ADD:
    - Integration naming: `Flext<Role><Domain><Facade>` (NOT `FlextMeltano<Role>...`)
    - Clarify: "exactly ONE internal namespace class" refers to LOCAL namespace class, not single inheritance
    - L1 Platform Chains: Core→Cli→Meltano→Integration, Core→Web→Api→Auth
    - Reference per-tier inheritance lookup table in flext-architecture-layers skill
  - §3 Code Law — ADD:
    - Import parent by CLASS NAME for inheritance, never by alias
    - `_LAZY_IMPORTS` string references MUST match actual class names
    - `model_rebuild()` is FORBIDDEN (explicit prohibition, not just implied)
    - `from __future__ import annotations` verification as explicit requirement
  - §9 Agent Instructions — ADD:
    - Scope discipline: agent MUST NOT modify files outside task boundary
    - Verify-before-implement: check `git log --oneline -5` and `git show HEAD` before starting any task
    - .new/swap protocol: for large file modifications, create .new file first, verify, then swap
    - Cross-session dedup: check recent commits for already-completed work before starting
    - Evidence requirements: every verification claim needs command output proof
  - §10 Multi-Agent — ADD:
    - Plan hygiene: consolidate overlapping plans before creating new ones
    - Cross-session deduplication protocol

  **Must NOT do**: Remove existing content, change section numbering

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`flext-docs-pointer-policy`]

  **Parallelization**: Wave 0 | Blocks: T6-T37 | Blocked By: None

  **QA Scenarios**:
  ```
  Scenario: CLAUDE.md Additions Verified
    Tool: Bash
    Steps:
      1. grep -c "Flext<Role><Domain>" CLAUDE.md
      2. grep -c "_LAZY_IMPORTS" CLAUDE.md
      3. grep -c "model_rebuild" CLAUDE.md
      4. grep -c "scope discipline\|Scope discipline" CLAUDE.md
      5. grep -c ".new/swap" CLAUDE.md
    Expected: Each grep returns >= 1 match
    Evidence: .sisyphus/evidence/task-1-claude-md.txt
  ```

  **Commit**: YES — `docs(governance): update CLAUDE.md §2/§3/§9/§10 from session learnings`

- [x] 2. Fix/Update Skills — 4 Contradictions + New Skill

  **What to do**:
  - **flext-architecture-layers** — Fix 4 contradictions:
    1. Alias set table (line ~180): Change Types from `(FlextMeltanoTypes)` to dual `(FlextMeltanoTypes, Flext<Domain>Types)` — match text at line 184-185
    2. Composition matrix (line ~194): Fix `FlextWmsConstants` → `FlextOracleWmsConstants`, `FlextWmsTypes` → `FlextOracleWmsTypes`
    3. Add explicit note: "ALL 5 facades follow the SAME dual-inheritance rule for integration projects"
    4. Add Platform Chain Table (same content as this plan's Per-Tier Inheritance Lookup Table)
  - **flext-patterns** — Fix/add:
    1. Fix outdated example (line ~101): `FlextTargetOracleModels(FlextMeltanoModels)` → `FlextTargetOracleModels(FlextMeltanoModels, FlextDbOracleModels)`
    2. Add .new/swap protocol documentation
    3. Add MRO verification command: `[c.__name__ for c in cls.__mro__]`
  - **flext-import-rules** — Add:
    1. Rule 4D examples for integration projects (before/after with dual inheritance)
    2. Naming convention enforcement rule: `Flext<Role><Domain><Facade>` (no Meltano prefix)
  - **NEW: flext-plan-hygiene** — Create:
    1. Plan consolidation rules (check for overlapping scope before new plan)
    2. Overlap detection checklist
    3. Cross-session deduplication protocol (check git log before starting task)
    4. Plan archival protocol

  **Must NOT do**: Change skill format, remove existing valid content

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`skill-format-universal`, `flext-docs-pointer-policy`]

  **Parallelization**: Wave 0 | Blocks: T6-T37 | Blocked By: None

  **QA Scenarios**:
  ```
  Scenario: Skill Contradictions Fixed
    Tool: Bash
    Steps:
      1. grep -c "FlextMeltanoTypes, Flext" .claude/skills/flext-architecture-layers/SKILL.md
      2. grep -c "FlextOracleWmsConstants" .claude/skills/flext-architecture-layers/SKILL.md
      3. grep -c "FlextDbOracleModels" .claude/skills/flext-patterns/SKILL.md
      4. test -f .claude/skills/flext-plan-hygiene/SKILL.md
    Expected: Counts >= 1, new skill file exists
    Evidence: .sisyphus/evidence/task-2-skills.txt
  ```

  **Commit**: YES — `docs(skills): fix 4 contradictions + create flext-plan-hygiene`

- [x] 3. Fix 3 P0 Broken Type References

  **What to do**:
  - `flext-tap-oracle-oic/src/flext_tap_oracle_oic/typings.py`: Fix `_t` base class reference → proper `FlextMeltanoTypes` (or correct parent)
  - `flext-target-oracle-wms/src/flext_target_oracle_wms/typings.py`: Fix `_FlextTypes` → proper `FlextMeltanoTypes` (or correct parent)
  - `flext-web/src/flext_web/typings.py`: Fix `ft` → proper `FlextTypes`
  - These cause ImportError on module load — P0 priority

  **Must NOT do**: Fix other issues in these projects (only P0 references)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`flext-architecture-layers`]

  **Parallelization**: Wave 0 | Blocks: T24, T30, T8 | Blocked By: None

  **QA Scenarios**:
  ```
  Scenario: Broken References Fixed
    Tool: Bash
    Steps:
      1. python -c "from flext_tap_oracle_oic.typings import *"
      2. python -c "from flext_target_oracle_wms.typings import *"
      3. python -c "from flext_web.typings import *"
    Expected: All import successfully (no ImportError)
    Evidence: .sisyphus/evidence/task-3-p0-fixes.txt
  ```

  **Commit**: YES — `fix: resolve 3 P0 broken type base class references`

- [ ] 4. Workspace Infrastructure — base.mk, CI, Scripts

  **What to do**:
  - **base.mk**: Verify/fix Make targets align with CLAUDE.md §5 contract
  - **CI/CD**: Review `.github/workflows/` — ensure shared workflows use correct Make targets
  - **Scripts**: Audit `scripts/` directory for deprecated patterns, unused scripts
  - **pyproject.toml template**: Ensure modernize_pyproject.py produces PEP 621/639 compliant output
  - Run `make validate VALIDATE_SCOPE=workspace` and fix any failures

  **Must NOT do**: Change per-project Makefiles (those are in per-project tasks)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: [`scripts-architecture`, `scripts-maintenance`, `flext-quality-gates`]

  **Parallelization**: Wave 0 | Blocks: T6-T37 (Make alignment) | Blocked By: None

  **QA Scenarios**:
  ```
  Scenario: Workspace Validation Passes
    Tool: Bash
    Steps:
      1. make validate VALIDATE_SCOPE=workspace
    Expected: 0 exit code
    Evidence: .sisyphus/evidence/task-4-workspace-infra.txt
  ```

  **Commit**: YES — `chore(infra): align workspace base.mk, CI, and scripts`

- [x] 5. Archive ALL 45 Plans

  **What to do**:
  - Create `.sisyphus/plans/archived/` directory
  - Move ALL 45 existing `.md` plan files to `archived/`
  - Keep ONLY `workspace-final-standardization.md` in `.sisyphus/plans/`
  - Create `.sisyphus/plans/archived/ARCHIVE-INDEX.md` with:
    - List of all archived plans with original progress %
    - Note: "Superseded by workspace-final-standardization.md"
    - Date of archival

  **Must NOT do**: Delete plans (archive, don't delete)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**: Wave 0 | Blocks: None | Blocked By: None

  **QA Scenarios**:
  ```
  Scenario: Plans Archived
    Tool: Bash
    Steps:
      1. ls .sisyphus/plans/*.md | wc -l
      2. ls .sisyphus/plans/archived/*.md | wc -l
      3. test -f .sisyphus/plans/archived/ARCHIVE-INDEX.md
    Expected: Only 1 plan in plans/, 45 in archived/, index exists
    Evidence: .sisyphus/evidence/task-5-archive.txt
  ```

  **Commit**: YES — `chore: archive all 45 superseded plans`

### Wave 1: Foundation (1 task, after Wave 0)

- [ ] 6. flext-core — Full Standardization + model_rebuild Removal

  **What to do**:
  - **Facades**: Verify ALL 5 facades (FlextModels, FlextConstants, FlextTypes, FlextUtilities, FlextProtocols) are correctly defined as base classes
  - **model_rebuild()**: Remove from 9 files — each requires structural fix:
    - Understand the circular dependency each model_rebuild resolves
    - Fix via: TYPE_CHECKING + string annotations, Protocol decoupling, or import restructuring
    - Do NOT just delete model_rebuild — fix the underlying circular reference first
  - **Pydantic v2**: Fix remaining 3 test files with `class Config:` → `model_config = ConfigDict(...)`
  - **Typing**: Address `: Any` (6 files) and `: object` (assess scope in flext-core specifically)
  - **Nuclear**: Remove any fake/dead classes, unused validation methods
  - ****init**.py**: Verify all exports, lazy loaders, **all** match actual class names
  - **Make**: `make check PROJECT=flext-core` and `make test PROJECT=flext-core` must pass

  **Must NOT do**: Change public API contracts, rename FlextModels/FlextTypes/etc. (they ARE the base)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`rules-flext-core`, `flext-architecture-layers`, `flext-strict-typing`, `flext-patterns`]

  **Parallelization**: Wave 1 | Blocks: T7-T20 | Blocked By: T1-T5

  **QA Scenarios**:
  ```
  Scenario: flext-core Clean Build
    Tool: Bash
    Steps:
      1. make check PROJECT=flext-core
      2. make test PROJECT=flext-core
      3. grep -rn "model_rebuild" flext-core/src/
    Expected: Both pass (0 exit), zero model_rebuild matches
    Evidence: .sisyphus/evidence/task-6-flext-core.txt

  Scenario: MRO Verification
    Tool: Bash
    Steps:
      1. python -c "from flext_core import FlextModels, FlextConstants, FlextTypes, FlextUtilities, FlextProtocols; [print(f'{c.__name__}: {[p.__name__ for p in c.__mro__[:5]]}') for c in [FlextModels, FlextConstants, FlextTypes, FlextUtilities, FlextProtocols]]"
    Expected: Each shows clean MRO with no unexpected parents
    Evidence: .sisyphus/evidence/task-6-flext-core-mro.txt
  ```

  **Commit**: YES — `refactor(flext-core): full standardization — facades, model_rebuild, typing`

### Wave 2: L1 Projects (14 tasks, sub-sequenced, after Wave 1)

> ALL tasks follow Template: Platform/Domain/Standalone.
> Skills for ALL: `[flext-architecture-layers, flext-import-rules]`
> QA for ALL: `make check PROJECT=<name>` + `make test PROJECT=<name>` + MRO verify (see QA Policy)
> Evidence: `.sisyphus/evidence/task-{N}-<project>.txt`

**Tier 1 (parallel, 9 tasks — all depend only on T6):**

- [ ] 7. flext-cli — Full Standardization (Template: Platform)

  **Expected MRO**: `FlextCli<Facade>(Flext<Facade>)` for all 5 facades
  **Known Issues**: Platform chain currently only in Protocols — fix Models, Constants, Types, Utilities
  **Category**: `quick` | **Blocks**: T9, T20 | **Blocked By**: T6
  **Commit**: `refactor(flext-cli): full standardization — facades, typing, pydantic, make`

- [ ] 8. flext-web — Full Standardization (Template: Platform)

  **Expected MRO**: `FlextWeb<Facade>(Flext<Facade>)` for all 5 facades
  **Known Issues**: typings.py has broken `ft` reference (fixed in T3, verify here)
  **Category**: `quick` | **Blocks**: T10, T20 | **Blocked By**: T6
  **Commit**: `refactor(flext-web): full standardization — facades, typing, pydantic, make`

- [ ] 11. flext-ldif — Full Standardization (Template: Domain)

  **Expected MRO**: `FlextLdif<Facade>(Flext<Facade>)` for all 5 facades
  **Known Issues**: None identified
  **Category**: `quick` | **Blocks**: T15, T22, T27, T32 | **Blocked By**: T6
  **Commit**: `refactor(flext-ldif): full standardization — facades, typing, pydantic, make`

- [ ] 12. flext-db-oracle — Full Standardization (Template: Domain)

  **Expected MRO**: `FlextDbOracle<Facade>(Flext<Facade>)` for all 5 facades
  **Known Issues**: None identified
  **Category**: `quick` | **Blocks**: T23, T28, T33 | **Blocked By**: T6
  **Commit**: `refactor(flext-db-oracle): full standardization — facades, typing, pydantic, make`

- [ ] 13. flext-oracle-wms — Full Standardization (Template: Domain)

  **Expected MRO**: `FlextOracleWms<Facade>(Flext<Facade>)` for all 5 facades
  **Known Issues**: Skill had `FlextWmsConstants` naming — verify actual code uses `FlextOracleWmsConstants`
  **Category**: `quick` | **Blocks**: T25, T30, T34 | **Blocked By**: T6
  **Commit**: `refactor(flext-oracle-wms): full standardization — facades, typing, pydantic, make`

- [ ] 14. flext-oracle-oic — Full Standardization (Template: Domain)

  **Expected MRO**: `FlextOracleOic<Facade>(Flext<Facade>)` for all 5 facades
  **Known Issues**: None identified
  **Category**: `quick` | **Blocks**: T24, T29 | **Blocked By**: T6
  **Commit**: `refactor(flext-oracle-oic): full standardization — facades, typing, pydantic, make`

- [ ] 16. flext-grpc — Full Standardization (Template: Standalone)

  **Expected MRO**: `FlextGrpc<Facade>(Flext<Facade>)` for all 5 facades
  **Known Issues**: None identified
  **Category**: `quick` | **Blocks**: F1-F4 | **Blocked By**: T6
  **Commit**: `refactor(flext-grpc): full standardization — facades, typing, pydantic, make`

- [ ] 17. flext-plugin — Full Standardization (Template: Standalone)

  **Expected MRO**: `FlextPlugin<Facade>(Flext<Facade>)` for all 5 facades
  **Known Issues**: None identified
  **Category**: `quick` | **Blocks**: F1-F4 | **Blocked By**: T6
  **Commit**: `refactor(flext-plugin): full standardization — facades, typing, pydantic, make`

- [ ] 18. flext-observability — Full Standardization (Template: Standalone)

  **Expected MRO**: `FlextObservability<Facade>(Flext<Facade>)` for all 5 facades
  **Known Issues**: None identified
  **Category**: `quick` | **Blocks**: F1-F4 | **Blocked By**: T6
  **Commit**: `refactor(flext-observability): full standardization — facades, typing, pydantic, make`

**Tier 2 (after dependencies, 3 tasks):**

- [ ] 9. flext-meltano — Full Standardization (Template: Platform, chained)

  **Expected MRO**: `FlextMeltano<Facade>(FlextCli<Facade>)` for all 5 facades
  **Known Issues**: Currently only Protocols chains through FlextCli. Models, Constants, Types, Utilities still inherit from FlextModels/FlextConstants/etc. directly — ALL 4 need fixing.
  **CRITICAL**: This is the parent for ALL 14 integration projects. Must be correct before Wave 3.
  **Category**: `deep` | **Blocks**: T21-T34 | **Blocked By**: T7 (cli)
  **Commit**: `refactor(flext-meltano): chain all facades through FlextCli — critical for integration projects`

- [ ] 10. flext-api — Full Standardization (Template: Platform, chained)

  **Expected MRO**: `FlextApi<Facade>(FlextWeb<Facade>)` for all 5 facades
  **Known Issues**: Currently only Protocols chains through FlextWeb. Fix remaining 4 facades.
  **Category**: `quick` | **Blocks**: T19 | **Blocked By**: T8 (web)
  **Commit**: `refactor(flext-api): chain all facades through FlextWeb`

- [ ] 15. flext-ldap — Full Standardization (Template: Domain, chained through ldif)

  **Expected MRO**: `FlextLdap<Facade>(FlextLdif<Facade>)` for all 5 facades
  **Known Issues**: Protocols currently inherit FlextProtocols (skips FlextLdifProtocols) — fix to chain through ldif
  **Category**: `quick` | **Blocks**: T21, T26, T31 | **Blocked By**: T11 (ldif)
  **Commit**: `refactor(flext-ldap): chain all facades through FlextLdif`

**Tier 3 (after dependencies, 2 tasks):**

- [ ] 19. flext-auth — Full Standardization (Template: Platform, chained)

  **Expected MRO**: `FlextAuth<Facade>(FlextApi<Facade>)` for all 5 facades
  **Known Issues**: Currently some facades chain through FlextApi, others skip to FlextWeb — normalize all to FlextApi chain
  **Category**: `quick` | **Blocks**: F1-F4 | **Blocked By**: T10 (api)
  **Commit**: `refactor(flext-auth): chain all facades through FlextApi`

- [ ] 20. flext-quality — Full Standardization (Template: Standalone, dual platform)

  **Expected MRO**: `FlextQuality<Facade>(FlextWeb<Facade>, FlextCli<Facade>)` for all 5 facades
  **Known Issues**: Dual platform inheritance — verify MRO linearization is correct for all facades
  **Category**: `quick` | **Blocks**: F1-F4 | **Blocked By**: T7 (cli) + T8 (web)
  **Commit**: `refactor(flext-quality): standardize dual-platform facade inheritance`

### Wave 3: Integration Projects (14 tasks, max parallel, after Wave 2)

> ALL tasks follow Template: Integration Project.
> ALL require dual inheritance: `(FlextMeltano<Facade>, Flext<Domain><Facade>)` for ALL 5 facades.
> Skills for ALL: `[flext-architecture-layers, flext-import-rules]`
> Category for ALL: `quick`
> CRITICAL: Types (t) is the heavy-lift item — 13/14 need conversion from single → dual inheritance.
> QA: `make check` + `make test` + MRO verify for ALL 5 facades + naming audit + lazy loader test.
> Evidence: `.sisyphus/evidence/task-{N}-<project>.txt`

| # | Project | Role | Domain | Import Pkg | Blocked By | Known Issues |
|---|---------|------|--------|------------|------------|--------------|
| 21 | flext-tap-ldap | FlextTapLdap | FlextLdap | flext_ldap | T9, T15 | `FlextMeltanoTapLdap*` naming → rename ALL to `FlextTapLdap*` |
| 22 | flext-tap-ldif | FlextTapLdif | FlextLdif | flext_ldif | T9, T11 | `FlextMeltanoTapLdif*` naming → rename ALL to `FlextTapLdif*` |
| 23 | flext-tap-oracle | FlextTapOracle | FlextDbOracle | flext_db_oracle | T9, T12 | `FlextMeltanoTapOracle*` naming → rename ALL. MIXED state (utilities correct, models wrong) |
| 24 | flext-tap-oracle-oic | FlextTapOracleOic | FlextOracleOic | flext_oracle_oic | T9, T14 | `FlextMeltanoTapOracleOic*` naming. P0 `_t` reference was fixed in T3 — verify |
| 25 | flext-tap-oracle-wms | FlextTapOracleWms | FlextOracleWms | flext_oracle_wms | T9, T13 | Mixed naming state (some correct, some `FlextMeltanoTapOracleWms*`) |
| 26 | flext-target-ldap | FlextTargetLdap | FlextLdap | flext_ldap | T9, T15 | Naming already correct (`FlextTargetLdap*`). Types still single inheritance. |
| 27 | flext-target-ldif | FlextTargetLdif | FlextLdif | flext_ldif | T9, T11 | `FlextMeltanoTargetLdif*` Constants naming. Types single inheritance. |
| 28 | flext-target-oracle | FlextTargetOracle | FlextDbOracle | flext_db_oracle | T9, T12 | Naming already correct (`FlextTargetOracle*`). Types single inheritance. |
| 29 | flext-target-oracle-oic | FlextTargetOracleOic | FlextOracleOic | flext_oracle_oic | T9, T14 | Naming already correct. Types single inheritance. |
| 30 | flext-target-oracle-wms | FlextTargetOracleWms | FlextOracleWms | flext_oracle_wms | T9, T13 | P0 `_FlextTypes` reference was fixed in T3 — verify. Types single inheritance. |
| 31 | flext-dbt-ldap | FlextDbtLdap | FlextLdap | flext_ldap | T9, T15 | Types single inheritance (`FlextTypes`). |
| 32 | flext-dbt-ldif | FlextDbtLdif | FlextLdif | flext_ldif | T9, T11 | `FlextMeltanoDbtLdif*` Constants naming. Types single inheritance. |
| 33 | flext-dbt-oracle | FlextDbtOracle | FlextDbOracle | flext_db_oracle | T9, T12 | Types single inheritance (`FlextTypes`). |
| 34 | flext-dbt-oracle-wms | FlextDbtOracleWms | FlextOracleWms | flext_oracle_wms | T9, T13 | Types single inheritance (`FlextTypes`). |

**Per-task details** (each row above is a task):
- Follow Template: Integration Project (Steps 1-9)
- Expected MRO per facade: see Per-Tier Inheritance Lookup Table
- Use `lsp_rename` for ALL class renames — NEVER raw search-replace
- After rename: update `__init__.py` (_LAZY_IMPORTS strings, **getattr**, **all**)
- After Types dual-inheritance: verify no inner class name collisions via MRO inspection
- Commit message: `refactor(<project>): full standardization — facades, naming, typing, pydantic, make`

**Task Checkboxes** (for progress tracking):
- [ ] 21. flext-tap-ldap — Full Standardization (Integration Template)
- [ ] 22. flext-tap-ldif — Full Standardization (Integration Template)
- [ ] 23. flext-tap-oracle — Full Standardization (Integration Template)
- [ ] 24. flext-tap-oracle-oic — Full Standardization (Integration Template)
- [ ] 25. flext-tap-oracle-wms — Full Standardization (Integration Template)
- [ ] 26. flext-target-ldap — Full Standardization (Integration Template)
- [ ] 27. flext-target-ldif — Full Standardization (Integration Template)
- [ ] 28. flext-target-oracle — Full Standardization (Integration Template)
- [ ] 29. flext-target-oracle-oic — Full Standardization (Integration Template)
- [ ] 30. flext-target-oracle-wms — Full Standardization (Integration Template)
- [ ] 31. flext-dbt-ldap — Full Standardization (Integration Template)
- [ ] 32. flext-dbt-ldif — Full Standardization (Integration Template)
- [ ] 33. flext-dbt-oracle — Full Standardization (Integration Template)
- [ ] 34. flext-dbt-oracle-wms — Full Standardization (Integration Template)

### Wave 4: Special Projects (3 tasks, after Wave 3 dependencies)

- [ ] 35. gruponos-meltano-native — Special Standardization

  **What to do**:
  - Verify ALL imports from integration projects use RENAMED class names (FlextTapOracle*, FlextTargetOracleWms* — not FlextMeltano* prefixes)
  - Fix any broken imports from class renames in Wave 3
  - Standard facade audit: MRO, naming, imports, aliases, **all**, **init**.py
  - Pydantic v2, typing, Make alignment checks

  **Known Issues**: Depends on FlextTapOracle*+ FlextTargetOracleWms* which were renamed in T23 + T30
  **Category**: `quick` | **Skills**: `[flext-architecture-layers]`
  **Blocked By**: T23 (tap-oracle) + T30 (target-oracle-wms) | **Blocks**: F1-F4
  **Commit**: `refactor(gruponos): fix imports for renamed integration classes`

- [ ] 36. algar-oud-mig — Special Standardization

  **What to do**:
  - Verify facade imports from flext-ldap + flext-cli are correct
  - Standard facade audit if applicable (may have non-standard structure)
  - Pydantic v2, typing, Make alignment checks

  **Known Issues**: Depends on flext-ldap + flext-cli chains being correct
  **Category**: `quick` | **Skills**: `[flext-architecture-layers]`
  **Blocked By**: T15 (ldap) + T7 (cli) | **Blocks**: F1-F4
  **Commit**: `refactor(algar-oud-mig): standardize facade imports and typing`

- [ ] 37. flexcore — Special Standardization

  **What to do**:
  - Go/Python hybrid — verify Python facade structure only
  - Standard facade audit for Python components
  - Typing and Make alignment checks

  **Known Issues**: Go/Python hybrid — may have non-standard facade structure
  **Category**: `quick` | **Skills**: `[flext-architecture-layers]`
  **Blocked By**: T6 (flext-core) | **Blocks**: F1-F4
  **Commit**: `refactor(flexcore): standardize Python facade components`

## Final Verification Wave (4 parallel reviewers, after ALL tasks)

> ALL must APPROVE. Rejection → fix → re-run.

- [ ] F1. Plan Compliance Audit — `oracle`

  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, run command).
  For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found.
  Check evidence files exist in `.sisyphus/evidence/` for every task.
  Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | Evidence [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. Code Quality Review — `unspecified-high`

  Run `make validate VALIDATE_SCOPE=workspace`. Review all changed files for:
  `as any`/`@ts-ignore`, empty catches, print() in prod, commented-out code, unused imports.
  Check for AI slop: excessive comments, over-abstraction, generic names.
  Run `ruff check` on every project.
  Output: `Workspace Validate [PASS/FAIL] | Projects [N/N clean] | VERDICT`

- [ ] F3. Full MRO Workspace Audit — `deep`

  For EVERY project:
  1. Import all 5 facade aliases (m, c, t, u, p)
  2. Print MRO for each: `[c.__name__ for c in alias.__mro__]`
  3. Verify chain matches Per-Tier Inheritance Lookup Table in this plan
  4. For integration projects: verify BOTH FlextMeltano*AND FlextDomain* appear in chain
  5. Verify NO `FlextMeltanoTap*` or `FlextMeltanoTarget*` or `FlextMeltanoDbt*` class names remain
  6. Verify NO broken references (`_t`, `_FlextTypes`, `ft`, or alias-based base classes)
  Save full MRO dump to `.sisyphus/evidence/final-mro-audit.txt`.
  Output: `Projects [N/33 correct MRO] | Naming [N/N clean] | Broken Refs [N found] | VERDICT`

- [ ] F4. Scope Fidelity Check — `deep`

  For each task: read "What to do", read actual diff (`git log --oneline`).
  Verify 1:1 — everything in spec was built (no missing), nothing beyond spec was built (no creep).
  Check "Must NOT do" compliance per task.
  Detect cross-task contamination: Task N touching files outside its project boundary.
  Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

## Commit Strategy

- Wave 0: `docs(governance): update CLAUDE.md and skills from session learnings`
- Wave 0: `chore: archive all superseded plans`
- Wave 1: `refactor(flext-core): full standardization — facades, model_rebuild, typing`
- Wave 2-4: `refactor(<project>): full standardization — facades, typing, pydantic, make`
- Wave F: `chore: final verification evidence`

---

## Success Criteria

### Verification Commands
```bash
# Per project:
make check PROJECT=<name>  # Expected: 0 exit code
make test PROJECT=<name>   # Expected: 0 exit code
python -c "from <pkg> import m; print([c.__name__ for c in m.__mro__])"  # Expected: correct chain

# Workspace-wide (after ALL projects):
make validate VALIDATE_SCOPE=workspace  # Expected: 0 exit code

# Naming audit (workspace-wide):
grep -rn "class FlextMeltanoTap\|class FlextMeltanoTarget\|class FlextMeltanoDbt" */src/  # Expected: 0 matches
```

### Final Checklist
- [ ] All "Must Have" items present
- [ ] All "Must NOT Have" items absent
- [ ] All 33 projects verified (make check + make test + MRO)
- [ ] CLAUDE.md updated with all session learnings
- [ ] Skills fixed (4 contradictions) and new skill created
- [ ] All 45 old plans archived
- [ ] Zero broken type references
- [ ] Zero FlextMeltanoTap*/FlextMeltanoTarget*/FlextMeltanoDbt* class names
