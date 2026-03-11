# Utility Patterns Systematic Adoption — Replace Verbose Code with Existing u.*/r.*/d.* Utilities

## TL;DR

> **Quick Summary**: Systematically replace verbose code patterns (guard-clause chains, manual try/except, manual retry, ternary unwrapping) with existing but underutilized FlextResult operators (`.flow_through()`, `.map_error()`, `.value_or()`, `.tap()`), decorators (`@railway`, `@retry`), and utility functions (`u.try_()`, `u.flow_result()`, `r.with_resource()`) across all FLEXT projects. Strictly behavior-preserving — no signature changes, no new behavior.
>
> **Deliverables**:
> - ~440 verbose code sites transformed across ~25 projects
> - Sequential guard-clause chains converted to `.flow_through()`/`.map_error()` chains (~350 sites)
> - Unused operators adopted: `.value_or()`, `.tap()`, `.fold()`, `.lash()`, `.recover()` (~50 sites)
> - Decorator adoption: `@railway`, `@retry` for eligible patterns (~40 sites)
> - Advanced utility adoption: `u.try_()`, `r.with_resource()`, `u.flow_result()` (~30 sites)
> - Reusable ast-grep pattern catalog for future sweeps
> - ZERO behavior changes — all transformations are strictly refactoring
>
> **Estimated Effort**: Large
> **Parallel Execution**: YES — 6 waves, up to 6 parallel tasks per wave
> **Critical Path**: T1 (baseline) → T3 (ast-grep catalog) → T4/T5/T6 (guard-clause sweeps) → T10 (decorator) → F1-F4 (verification)

---

## Context

### Original Request
Discover ALL underutilized utility functions across flext-core (`u.*`, `x.*`, `r.*`, decorators) that could dramatically simplify verbose code patterns, then create a comprehensive plan to systematically apply them across all 33 projects in the FLEXT portfolio.

### Interview Summary
**Key Discussions**:
- Scope: All 4 tiers of patterns (zero-use utilities, underutilized operators, verbose patterns, decorators)
- Batching: By pattern type — one task per pattern, ast-grep sweep across all projects
- Test strategy: Behavior-preserving only (`make check` + `make test`, no new tests)
- Reference plan: `.sisyphus/plans/flextresult-ergonomic-cleanup.md` (5 methods in 2 files — template)

**Research Findings (6 parallel explore agents)**:
- 10+ zero-use utilities discovered (`u.flow_result`, `u.fold_result`, `u.tap_result`, etc.)
- 12+ underutilized FlextResult operators (`.fold()`=4 uses, `.lash()`=2, `.recover()`=0, `.tap()`=0 in production)
- 960 `.is_failure` guard-clause patterns in 230 files (validated production `src/` only)
- 0 production uses of `@railway`, `@retry`, `@log_operation` decorators
- Dominant pattern (~80%+): sequential guard-clause early-returns
- All claimed usage counts were validated against actual production code (Metis reduced inflated estimates by 5-50x)

### Metis Review
**Identified Gaps** (addressed):
- Usage counts were inflated 5-50x — recalibrated to validated production numbers
- `T | None → r[T]` is a contract change, NOT refactoring — **EXCLUDED**
- `json.loads → model_validate_json` is a behavior change — **EXCLUDED**
- `isinstance → u.Guards` has only 1 actual violation (`type(x) is T`) — **EXCLUDED** as blanket sweep
- `@log_operation` for 3,020 sites is feature addition — **EXCLUDED**
- `@railway` only supports 5 exception types — filter criterion added
- Baseline health check mandatory before any refactoring
- ast-grep patterns must use `$VAR.is_failure` (variable-agnostic, not `result.is_failure`)
- Guard-clause patterns with error enrichment need `.map_error()`, not simple `.flow_through()`
- Multi-step pipelines with intermediate value usage can't use `.flow_through()` — must be manually assessed

---

## Work Objectives

### Core Objective
Replace verbose code patterns with existing FlextResult operators, decorators, and utility functions — strictly behavior-preserving refactoring across all FLEXT projects.

### Concrete Deliverables
- ~440 verbose code sites transformed into idiomatic FlextResult chains
- Baseline health report for all 33 projects (`.sisyphus/evidence/baseline/`)
- ast-grep pattern catalog — reusable rules for future sweeps
- Before/after pattern count comparison report

### Definition of Done
- [x] All touched projects pass `make check` with ZERO errors
- [x] All touched projects pass `make test` with same test count as baseline
- [x] Pattern count delta matches expected reduction per task
- [x] No function signature changes anywhere
- [x] No new behavior added anywhere

### Must Have
- All sequential guard-clause patterns evaluated and eligible ones transformed
- Transformations use `.flow_through()`, `.map_error()`, `.value_or()`, `.tap()`, `.fold()`, `.lash()`, `.recover()`
- `@railway` applied ONLY to `try/except` catching `AttributeError|TypeError|ValueError|RuntimeError|KeyError`
- `@retry` applied ONLY to EXISTING manual retry loops (not adding new retry behavior)
- `ast-grep dryRun=true` before every sweep
- One commit per (pattern x project) with `make check && make test` evidence
- `$VAR.is_failure` patterns in ast-grep (variable-agnostic, not hardcoded to `result`)

### Must NOT Have (Guardrails)
- NO function signature changes (no `T | None → r[T]` conversions) — EXCEPTION: Task 10 `@railway` adoption explicitly changes `T → r[T]` for eligible bare-T functions, with mandatory caller updates
- NO new behavior (no `@log_operation` for previously-unlogged functions)
- NO `json.loads/dumps → model_validate_json` conversions (behavior change — separate epic)
- NO blanket `isinstance → u.Guards` sweep (only fix FORBIDDEN `type(x) is T` — 1 site)
- NO changes to test files or example files (`src/` only)
- NO changes to flext-core internals (`result.py`, `decorators.py`, `utilities.py`, `handlers.py` — FROZEN per AGENTS.md §10.2)
- NO `@railway` for `try/except Exception` or domain-specific catches (`cx_Oracle.Error`, `ldap.LDAPError`, etc.)
- NO scope expansion beyond specified pattern per task (AGENTS.md §RV)
- NO ast-grep sweeps without prior `dryRun=true` validation on 3-5 sample files
- NO touching CQRS/dispatcher code
- NO changes to `__version__.py` or `settings.py` (different fix category)

### EXCLUDED — Separate Epics (NOT in this plan)
- **T | None → r[T]**: Function contract change affecting all callers (~300+ sites)
- **json.loads/dumps → model_validate_json**: Pydantic coercion changes behavior (~221 sites)
- **isinstance → u.Guards blanket sweep**: Most `isinstance` calls are legitimate (~751 sites)
- **@log_operation for unlogged functions**: Feature addition, not refactoring (~3,020 sites)
- **@retry for non-retry code**: Feature addition (~126 sites minus ~10 existing retry patterns)
- **u.match()/u.mt() adoption**: Pattern matching is style preference, not simplification
- **u.chain()/u.pipe()/u.compose()**: Functional composition adoption requires architecture decisions

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed.

### Test Decision
- **Infrastructure exists**: YES (all projects have `make check`/`make test`)
- **Automated tests**: None needed (behavior-preserving refactoring)
- **Framework**: existing `make check` (ruff, mypy, pyright, pyrefly) + `make test`
- **Baseline required**: `make check` + `make test` for ALL 33 projects BEFORE any changes

### QA Policy
Every task MUST:
1. Verify baseline from Task 1 (or run `make check && make test` BEFORE changes)
2. Run `ast-grep dryRun=true` BEFORE any sweep — review output
3. Apply changes
4. Run `make check && make test` AFTER changes for EACH touched project
5. Verify pattern count delta matches expectations
6. Commit per (pattern x project) with evidence

Evidence: `.sisyphus/evidence/task-{N}-{project}-{scenario}.txt`
Baseline: `.sisyphus/evidence/baseline/{project}-check.txt` and `{project}-test.txt`

---

## Execution Strategy

### Project Groups (used throughout plan)

**Group A — Core + Domain Libraries** (8 projects):
`flext-ldap`, `flext-ldif`, `flext-db-oracle`, `flext-grpc`, `flext-oracle-oic`, `flext-oracle-wms`, `flext-plugin`, `flext-observability`

**Group B — Platform Projects** (6 projects):
`flext-api`, `flext-cli`, `flext-web`, `flext-auth`, `flext-meltano`, `flexcore`

**Group C — Taps + Targets + dbt** (18 projects):
`flext-tap-ldap`, `flext-tap-ldif`, `flext-tap-oracle`, `flext-tap-oracle-oic`, `flext-tap-oracle-wms`,
`flext-target-ldap`, `flext-target-ldif`, `flext-target-oracle`, `flext-target-oracle-oic`, `flext-target-oracle-wms`,
`flext-dbt-ldap`, `flext-dbt-ldif`, `flext-dbt-oracle`, `flext-dbt-oracle-wms`,
`algar-oud-mig`, `gruponos-meltano-native`, `flext-quality`, `flext-core` (read-only, scan only)

### Parallel Execution Waves

```
Wave 0 (Start Immediately — baseline):
├── Task 1: Baseline health scan — all 33 projects [deep]
└── Task 2: Fix FORBIDDEN type(x) is T violation (1 site) [quick]

Wave 1 (After Wave 0 — tooling):
└── Task 3: Build & validate ast-grep pattern catalog [deep]

Wave 2 (After Wave 1 — guard-clause sweeps, MAX PARALLEL):
├── Task 4: Guard-clause → .flow_through()/.map_error() — Group A [unspecified-high]
├── Task 5: Guard-clause → .flow_through()/.map_error() — Group B [unspecified-high]
└── Task 6: Guard-clause → .flow_through()/.map_error() — Group C [unspecified-high]

Wave 3 (After Wave 1 — simple operators, PARALLEL with Wave 2):
├── Task 7: .value_or() + .recover() sweep — all projects [quick]
├── Task 8: .tap() + .tap_error() sweep — all projects [quick]
└── Task 9: .fold() + .lash() sweep — all projects [unspecified-high]

Wave 4 (After Waves 2+3 — decorators):
├── Task 10: @d.railway sweep — eligible try/except [unspecified-high]
└── Task 11: @d.retry sweep — existing manual retry only [unspecified-high]

Wave 5 (After Wave 1 — advanced, PARALLEL with Waves 2-4):
├── Task 12: u.try_() expansion sweep [unspecified-high]
├── Task 13: r.with_resource() adoption [quick]
└── Task 14: u.flow_result() adoption [deep]

Wave FINAL (After ALL tasks — independent review, 4 parallel):
├── Task F1: Plan compliance audit [oracle]
├── Task F2: Code quality review [unspecified-high]
├── Task F3: Full lint verification across all 33 projects [unspecified-high]
└── Task F4: Pattern coverage comparison (before vs after scan) [deep]

Critical Path: T1 → T3 → T4/T5/T6 → T10 → F1-F4
Parallel Speedup: ~65% faster than sequential
Max Concurrent: 6 (Waves 2+3 combined)
```

### Dependency Matrix

| Task | Depends On | Blocks | Wave |
|------|-----------|--------|------|
| 1 | None | 2, 3 | 0 |
| 2 | 1 | None | 0 |
| 3 | 1 | 4-14 | 1 |
| 4 | 3 | 10, 11, F1-F4 | 2 |
| 5 | 3 | 10, 11, F1-F4 | 2 |
| 6 | 3 | 10, 11, F1-F4 | 2 |
| 7 | 3 | F1-F4 | 3 |
| 8 | 3 | F1-F4 | 3 |
| 9 | 3 | F1-F4 | 3 |
| 10 | 4, 5, 6 | F1-F4 | 4 |
| 11 | 4, 5, 6 | F1-F4 | 4 |
| 12 | 3 | F1-F4 | 5 |
| 13 | 3 | F1-F4 | 5 |
| 14 | 3 | F1-F4 | 5 |
| F1-F4 | ALL | None | FINAL |

### Agent Dispatch Summary

- **Wave 0**: **2** — T1 → `deep`, T2 → `quick`
- **Wave 1**: **1** — T3 → `deep`
- **Wave 2**: **3** — T4, T5, T6 → `unspecified-high`
- **Wave 3**: **3** — T7, T8 → `quick`, T9 → `unspecified-high`
- **Wave 4**: **2** — T10, T11 → `unspecified-high`
- **Wave 5**: **3** — T12 → `unspecified-high`, T13 → `quick`, T14 → `deep`
- **FINAL**: **4** — F1 → `oracle`, F2, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

> Implementation tasks follow. Each uses ast-grep for search, `dryRun=true` for validation, then apply.
> **Every task targets `*/src/**/*.py` ONLY — tests and examples are READ-ONLY.**
> **One commit per (pattern x project) with `make check && make test` evidence.**
> **ast-grep patterns MUST use `$VAR` meta-variables, not hardcoded variable names.**

- [x] 1. Baseline Health Scan — All 33 Projects

  **What to do**:
  - Run `make check` and `make test` for EVERY project in the workspace
  - Capture output to `.sisyphus/evidence/baseline/{project}-check.txt` and `{project}-test.txt`
  - Create a summary report: which projects pass, which fail, which have warnings
  - Record pattern baseline counts per project:
    - `grep -rc '\.is_failure' {project}/src/ | awk -F: '{s+=$2}END{print s}'`
    - `grep -rc 'if.*\.is_failure' {project}/src/ | awk -F: '{s+=$2}END{print s}'`
    - `grep -rc 'try:' {project}/src/ | awk -F: '{s+=$2}END{print s}'`
    - `grep -rc '\.value_or\|\.tap(\|\.fold(\|\.lash(\|\.recover(' {project}/src/ | awk -F: '{s+=$2}END{print s}'`
  - Projects that FAIL baseline are flagged as "SKIP for refactoring" — they need separate fix-first tasks

  **Must NOT do**:
  - Do NOT fix any failures — only record them
  - Do NOT modify any files
  - Do NOT run `make setup` or install dependencies (assume env is ready)

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Needs to iterate 33 projects, capture output, build summary report — autonomous goal-driven
  - **Skills**: [`flext-quality-gates`]
    - `flext-quality-gates`: Understands make check/test contract and verification matrix

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 2)
  - **Parallel Group**: Wave 0
  - **Blocks**: Task 3
  - **Blocked By**: None

  **References**:
  - `AGENTS.md` §5 — Make contract verbs and exit codes
  - `AGENTS.md` §6 — Quality gates and verification matrix
  - Each project's `pyproject.toml` for test configuration

  **Acceptance Criteria**:
  - [x] `.sisyphus/evidence/baseline/` directory exists with 66 files (check + test per project)
  - [x] Summary report identifies passing vs failing projects
  - [x] Pattern baseline counts saved for all projects

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Baseline directory populated
    Tool: Bash
    Preconditions: All 33 projects exist in /home/marlonsc/flext/
    Steps:
      1. Run `ls .sisyphus/evidence/baseline/ | wc -l`
      2. Verify count >= 60 (some projects may not have tests)
    Expected Result: >= 60 evidence files
    Failure Indicators: Directory missing or < 30 files
    Evidence: .sisyphus/evidence/task-1-baseline-summary.txt

  Scenario: Summary report is actionable
    Tool: Bash
    Preconditions: Baseline scan complete
    Steps:
      1. Read summary report
      2. Verify it lists PASS/FAIL per project
      3. Verify pattern counts are numeric, not empty
    Expected Result: Clear PASS/FAIL per project, numeric pattern counts
    Evidence: .sisyphus/evidence/task-1-summary-validation.txt
  ```

  **Commit**: NO (evidence only, no code changes)

- [x] 2. Fix FORBIDDEN type(x) is T Violation

  **What to do**:
  - In `flext-auth/src/flext_auth/providers/base.py`: find the `type(x) is T` usage
  - Replace with `isinstance(x, T)` for proper type narrowing
  - This is a FORBIDDEN pattern per AGENTS.md §3 — must fix immediately
  - Run `cd flext-auth && make check && make test` to verify

  **Must NOT do**:
  - Do NOT change any other code in the file
  - Do NOT modify function signatures
  - Do NOT touch other files in flext-auth

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Single-line replacement in one file
  - **Skills**: [`rules-src`]
    - `rules-src`: Ensures src/ code follows FLEXT patterns

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 1)
  - **Parallel Group**: Wave 0
  - **Blocks**: None
  - **Blocked By**: Task 1 (need baseline first)

  **References**:
  - `flext-auth/src/flext_auth/providers/base.py` — file containing violation
  - `AGENTS.md` §3 — "type(x) is T for narrowing is forbidden"
  - `AGENTS.md` §9 — "Do NOT use type(x) is T or type(x) == T for narrowing"

  **Acceptance Criteria**:
  - [x] Zero `type(` used for narrowing in `flext-auth/src/`
  - [x] `cd flext-auth && make check` → ZERO errors
  - [x] `cd flext-auth && make test` → all tests pass

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Verify violation is fixed
    Tool: Bash (ast-grep)
    Preconditions: File edited
    Steps:
      1. Run `sg --pattern 'type($VAR) is $TYPE' --lang python flext-auth/src/`
      2. Verify zero matches
    Expected Result: 0 matches — violation eliminated
    Failure Indicators: Any match found
    Evidence: .sisyphus/evidence/task-2-type-violation-check.txt

  Scenario: Linters pass
    Tool: Bash
    Preconditions: Fix applied
    Steps:
      1. Run `cd /home/marlonsc/flext/flext-auth && make check`
      2. Verify exit code 0
    Expected Result: Exit 0, zero errors
    Evidence: .sisyphus/evidence/task-2-linter-check.txt
  ```

  **Commit**: YES
  - Message: `fix(auth): replace forbidden type() narrowing with isinstance`
  - Files: `flext-auth/src/flext_auth/providers/base.py`
  - Pre-commit: `cd flext-auth && make check && make test`

- [x] 3. Build & Validate ast-grep Pattern Catalog

  **What to do**:
  - Create ast-grep patterns for ALL target transformations in this plan:
    - **P1**: Sequential guard-clause: `$VAR = $CALL; if $VAR.is_failure: return $FAIL_EXPR`
    - **P2**: Ternary unwrap: `$VAR.value if $VAR.is_success else $DEFAULT`
    - **P3**: Logging-only branch: `if $VAR.is_failure: logger.$METHOD(...); return ...` / `if $VAR.is_success: logger.$METHOD(...)`
    - **P4**: Try/except with 5 eligible types: `try: $BODY except (AttributeError, TypeError, ValueError, RuntimeError, KeyError) as $E: $HANDLER`
    - **P5**: Manual retry: `while $VAR < $MAX: try: $BODY except: ... time.sleep($DELAY)`
    - **P6**: Try/finally cleanup: `try: $BODY finally: $CLEANUP`
    - **P7**: Simple fold: `if $VAR.is_failure: return $FAIL_EXPR` / `return r[$T].ok($VAR.value)`
  - Test each pattern with `dryRun=true` on 3-5 sample files from different projects
  - Record: pattern name, match count, false positive rate, sample matches
  - If false positive rate > 10%, refine the pattern or mark as "manual review needed"
  - Save catalog to `.sisyphus/evidence/ast-grep-pattern-catalog.md`

  **Must NOT do**:
  - Do NOT apply any transformations — this is pattern VALIDATION only
  - Do NOT modify any source files

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Requires iterative pattern refinement, testing against real code, accuracy assessment
  - **Skills**: [`rules-src`, `flext-patterns`]
    - `rules-src`: Understands code patterns in src/
    - `flext-patterns`: Understands FlextResult idioms

  **Parallelization**:
  - **Can Run In Parallel**: NO (sequential after Task 1)
  - **Parallel Group**: Wave 1 (solo)
  - **Blocks**: Tasks 4-14
  - **Blocked By**: Task 1

  **References**:
  - `flext-core/src/flext_core/result.py` — FlextResult API (.flow_through, .map_error, .value_or, .tap, .fold, .lash, .recover)
  - `flext-core/src/flext_core/_utilities/result_helpers.py` — u.try_(), u.val(), u.or_()
  - `flext-core/src/flext_core/_utilities/reliability.py` — u.flow_result(), u.retry()
  - `flext-core/src/flext_core/decorators.py` — @railway, @retry
  - `flext-core/examples/15_automation_showcase.py:223-255` — exemplar .flow_through() usage in pipeline chains (tests/examples only — no production usage yet, this plan introduces it)

  **Acceptance Criteria**:
  - [x] All 7 patterns (P1-P7) have ast-grep rules
  - [x] Each pattern tested on 3-5 real files with `dryRun=true`
  - [x] False positive rate documented per pattern
  - [x] Catalog saved to `.sisyphus/evidence/ast-grep-pattern-catalog.md`

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Pattern P1 finds real guard clauses
    Tool: Bash (ast-grep)
    Preconditions: Pattern catalog built
    Steps:
      1. Run ast-grep P1 pattern against flext-ldap/src/
      2. Verify matches are actual guard-clause patterns (not false positives)
      3. Count matches and compare against grep baseline
    Expected Result: Matches are real guard-clauses, false positive rate < 10%
    Evidence: .sisyphus/evidence/task-3-pattern-p1-validation.txt

  Scenario: All patterns have valid ast-grep syntax
    Tool: Bash (ast-grep)
    Preconditions: Catalog file exists
    Steps:
      1. Run each pattern in catalog against any src/ directory
      2. Verify no syntax errors from ast-grep
    Expected Result: All patterns parse correctly, no errors
    Evidence: .sisyphus/evidence/task-3-pattern-syntax-validation.txt
  ```

  **Commit**: NO (evidence only, no code changes)

- [x] 4. Guard-Clause → .flow_through()/.map_error() — Group A (Core + Domain Libraries)

  **What to do**:
  - Target projects: `flext-ldap`, `flext-ldif`, `flext-db-oracle`, `flext-grpc`, `flext-oracle-oic`, `flext-oracle-wms`, `flext-plugin`, `flext-observability`
  - For EACH project, scan `src/` using the P1 pattern from Task 3's catalog
  - For each match, classify into one of 4 categories:
    - **SIMPLE-FLOW**: `result = step(); if result.is_failure: return r.fail(result.error)` → `step().flow_through(next_step)`
    - **ERROR-ENRICHED**: `result = step(); if result.is_failure: return r.fail(f"Context: {result.error}")` → `step().map_error(lambda e: f"Context: {e}")`
    - **WITH-LOGGING**: `result = step(); if result.is_failure: logger.error(...); return ...` → `step().tap_error(lambda e: logger.error(...)).flow_through(...)`
    - **NOT-ELIGIBLE**: Multi-step with intermediate value usage, different return types, complex control flow → SKIP (leave as-is)
  - Apply transformation for eligible sites (SIMPLE-FLOW, ERROR-ENRICHED, WITH-LOGGING)
  - Ensure `from __future__ import annotations` is present (required for all Python modules)
  - Run `make check && make test` per project after all changes
  - Commit per project

  **Must NOT do**:
  - Do NOT transform NOT-ELIGIBLE patterns — skip them
  - Do NOT change function signatures or return types
  - Do NOT touch test files
  - Do NOT modify flext-core internals

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Requires judgment for classification, multi-project sweep, significant code changes
  - **Skills**: [`rules-src`, `flext-patterns`, `flext-strict-typing`]
    - `rules-src`: Code patterns for src/
    - `flext-patterns`: FlextResult idioms and composition
    - `flext-strict-typing`: Type annotation rules

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 5, 6, 7, 8, 9)
  - **Parallel Group**: Wave 2
  - **Blocks**: Tasks 10, 11, F1-F4
  - **Blocked By**: Task 3

  **References**:
  - `.sisyphus/evidence/ast-grep-pattern-catalog.md` — validated patterns from Task 3
  - `flext-core/src/flext_core/result.py:470-510` — `.flow_through()` implementation
  - `flext-core/src/flext_core/result.py:566-580` — `.map_error()` implementation
  - `flext-core/src/flext_core/result.py:540-560` — `.tap()` / `.tap_error()` implementation
  - `flext-core/src/flext_core/result.py:464` — docstring exemplar: `r[ConfigMap].ok(data).flow_through(validate, enrich)`
  - `flext-core/examples/15_automation_showcase.py:223` — example: `result = extract().flow_through(transform, load)`

  **Acceptance Criteria**:
  - [x] All eligible guard-clause patterns in Group A projects transformed
  - [x] NOT-ELIGIBLE patterns documented but untouched
  - [x] `make check` passes for each Group A project with ZERO errors
  - [x] `make test` passes for each Group A project with same test count as baseline
  - [x] Pattern count reduced from baseline (verified via grep count)

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Guard-clause count reduced in flext-ldap
    Tool: Bash
    Preconditions: Transformations applied to flext-ldap
    Steps:
      1. Run `grep -rc 'if.*\.is_failure' flext-ldap/src/ | awk -F: '{s+=$2}END{print s}'`
      2. Compare against baseline count from Task 1
      3. Verify count is lower by the number of transformed sites
    Expected Result: Count reduced by N (where N = number of transformed sites)
    Evidence: .sisyphus/evidence/task-4-flext-ldap-pattern-count.txt

  Scenario: Linters pass for all Group A projects
    Tool: Bash
    Preconditions: All Group A transformations complete
    Steps:
      1. For each project in Group A: `cd /home/marlonsc/flext/{project} && make check`
      2. Verify exit code 0 for each
    Expected Result: All 8 projects pass with zero errors
    Failure Indicators: Non-zero exit code, any ERROR in output
    Evidence: .sisyphus/evidence/task-4-group-a-linter-results.txt

  Scenario: No function signatures changed
    Tool: Bash
    Preconditions: Changes committed
    Steps:
      1. Run `git diff HEAD~1 -- '*/src/**/*.py' | grep '^[-+].*def ' | grep -v '[-+][-+][-+]'`
      2. Verify no function definition lines changed (only body changes)
    Expected Result: Zero function definition changes in diff
    Evidence: .sisyphus/evidence/task-4-signature-check.txt
  ```

  **Commit**: YES (one per project)
  - Message: `refactor({project}): replace guard-clause chains with .flow_through()/.map_error()`
  - Files: `{project}/src/**/*.py` (only changed files)
  - Pre-commit: `cd {project} && make check && make test`

- [x] 5. Guard-Clause → .flow_through()/.map_error() — Group B (Platform Projects)

  **What to do**:
  - Target projects: `flext-api`, `flext-cli`, `flext-web`, `flext-auth`, `flext-meltano`, `flexcore`
  - IDENTICAL procedure to Task 4:
    1. Scan `src/` with P1 pattern from catalog
    2. Classify each match: SIMPLE-FLOW, ERROR-ENRICHED, WITH-LOGGING, NOT-ELIGIBLE
    3. Transform eligible sites
    4. `make check && make test` per project
    5. Commit per project
  - Pay special attention to `flext-api` — it likely has the most guard-clause patterns among platform projects.

  **Must NOT do**:
  - Same guardrails as Task 4
  - Do NOT modify the exemplar pattern in `flext-api/schemas/asyncapi.py` (it's already correct)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Same complexity as Task 4, different project group
  - **Skills**: [`rules-src`, `flext-patterns`, `flext-strict-typing`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 4, 6, 7, 8, 9)
  - **Parallel Group**: Wave 2
  - **Blocks**: Tasks 10, 11, F1-F4
  - **Blocked By**: Task 3

  **References**:
  - Same as Task 4, plus:
  - `flext-core/src/flext_core/result.py:464` — docstring exemplar for .flow_through()
  - `flext-core/examples/15_automation_showcase.py:223-255` — example .flow_through() usage
  - `flext-meltano/src/flext_meltano/file_managers.py` — already cleaned by previous plan (verify, don't re-touch)

  **Acceptance Criteria**:
  - [x] All eligible guard-clause patterns in Group B projects transformed
  - [x] `flext-meltano/file_managers.py` NOT re-modified (already clean from prior plan)
  - [x] `make check` passes for each Group B project
  - [x] `make test` passes for each Group B project

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Guard-clause count reduced in Group B
    Tool: Bash
    Preconditions: Transformations applied
    Steps:
      1. For each Group B project: count `if.*\.is_failure` in src/
      2. Compare against baseline from Task 1
    Expected Result: Count reduced per project
    Evidence: .sisyphus/evidence/task-5-group-b-pattern-count.txt

  Scenario: Previously-cleaned files not re-modified
    Tool: Bash
    Preconditions: Changes complete
    Steps:
      1. Check `git diff` for `flext-meltano/src/flext_meltano/file_managers.py`
      2. Verify no changes (already handled by prior plan)
    Expected Result: Zero diff for file_managers.py
    Evidence: .sisyphus/evidence/task-5-no-rework-check.txt
  ```

  **Commit**: YES (one per project)
  - Message: `refactor({project}): replace guard-clause chains with .flow_through()/.map_error()`
  - Pre-commit: `cd {project} && make check && make test`

- [x] 6. Guard-Clause → .flow_through()/.map_error() — Group C (Taps + Targets + dbt)

  **What to do**:
  - Target projects: `flext-tap-ldap`, `flext-tap-ldif`, `flext-tap-oracle`, `flext-tap-oracle-oic`, `flext-tap-oracle-wms`, `flext-target-ldap`, `flext-target-ldif`, `flext-target-oracle`, `flext-target-oracle-oic`, `flext-target-oracle-wms`, `flext-dbt-ldap`, `flext-dbt-ldif`, `flext-dbt-oracle`, `flext-dbt-oracle-wms`, `algar-oud-mig`, `gruponos-meltano-native`, `flext-quality`
  - IDENTICAL procedure to Task 4:
    1. Scan `src/` with P1 pattern
    2. Classify: SIMPLE-FLOW, ERROR-ENRICHED, WITH-LOGGING, NOT-ELIGIBLE
    3. Transform eligible sites
    4. `make check && make test` per project
    5. Commit per project
  - Note: Many tap/target projects share similar patterns (Singer SDK conventions). Transformation patterns should be consistent across all taps and all targets.

  **Must NOT do**:
  - Same guardrails as Task 4
  - Do NOT modify flext-core (in Group C for scanning only, not modification)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Largest project group (17 projects), same judgment requirements
  - **Skills**: [`rules-src`, `flext-patterns`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 4, 5, 7, 8, 9)
  - **Parallel Group**: Wave 2
  - **Blocks**: Tasks 10, 11, F1-F4
  - **Blocked By**: Task 3

  **References**:
  - Same as Task 4
  - `flext-tap-ldap/src/` — representative tap structure
  - `flext-target-ldap/src/` — representative target structure

  **Acceptance Criteria**:
  - [x] All eligible guard-clause patterns in Group C projects transformed
  - [x] Tap/target pattern consistency verified (same transformation style across all)
  - [x] `make check` passes for each Group C project
  - [x] `make test` passes for each Group C project

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Tap/target consistency
    Tool: Bash
    Preconditions: All transformations complete
    Steps:
      1. Compare `.flow_through()` usage patterns across flext-tap-ldap and flext-tap-oracle
      2. Verify same transformation style used
    Expected Result: Consistent pattern application across similar projects
    Evidence: .sisyphus/evidence/task-6-tap-target-consistency.txt

  Scenario: All Group C projects pass linters
    Tool: Bash
    Preconditions: Transformations applied
    Steps:
      1. For each Group C project: `cd /home/marlonsc/flext/{project} && make check`
      2. Verify exit code 0
    Expected Result: All 17 projects pass
    Evidence: .sisyphus/evidence/task-6-group-c-linter-results.txt
  ```

  **Commit**: YES (one per project)
  - Message: `refactor({project}): replace guard-clause chains with .flow_through()/.map_error()`
  - Pre-commit: `cd {project} && make check && make test`

- [x] 7. .value_or() + .recover() Sweep — All Projects

  **What to do**:
  - Scan ALL projects' `src/` for ternary unwrapping patterns:
    - `$VAR.value if $VAR.is_success else $DEFAULT` → `$VAR.value_or($DEFAULT)`
    - `$VAR.value if not $VAR.is_failure else $DEFAULT` → `$VAR.value_or($DEFAULT)`
    - `$VAR.value if $VAR.is_success else None` → `$VAR.value_or(None)`
  - Also scan for simple recovery patterns:
    - `if $VAR.is_failure: return r[$T].ok($FALLBACK)` → `$VAR.recover(lambda _: $FALLBACK)`
  - Use P2 pattern from Task 3's catalog
  - These are the MOST mechanical transformations — low risk, high confidence
  - Run `make check && make test` per project, commit per project

  **Must NOT do**:
  - Do NOT convert complex ternaries with side-effects
  - Do NOT change function signatures

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Purely mechanical pattern replacement, well-defined ast-grep rules
  - **Skills**: [`rules-src`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 4-6, 8, 9)
  - **Parallel Group**: Wave 3
  - **Blocks**: F1-F4
  - **Blocked By**: Task 3

  **References**:
  - `flext-core/src/flext_core/result.py:350-365` — `.value_or()` implementation
  - `flext-core/src/flext_core/result.py:400-420` — `.recover()` implementation
  - `.sisyphus/evidence/ast-grep-pattern-catalog.md` — P2 pattern

  **Acceptance Criteria**:
  - [x] Zero ternary `$VAR.value if $VAR.is_success else $DEFAULT` patterns remain in touched files
  - [x] All replacements use `.value_or()` or `.recover()` correctly
  - [x] `make check && make test` pass for all touched projects

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: No ternary unwrap patterns remain
    Tool: Bash (ast-grep)
    Preconditions: Sweep complete
    Steps:
      1. Run P2 pattern across all src/ directories
      2. Verify zero matches
    Expected Result: 0 ternary unwrap patterns in touched files
    Evidence: .sisyphus/evidence/task-7-ternary-elimination.txt

  Scenario: Linters pass for touched projects
    Tool: Bash
    Preconditions: Changes applied
    Steps:
      1. For each touched project: `make check && make test`
      2. Verify all pass
    Expected Result: All touched projects pass
    Evidence: .sisyphus/evidence/task-7-linter-results.txt
  ```

  **Commit**: YES (one per project)
  - Message: `refactor({project}): adopt .value_or()/.recover() for result unwrapping`
  - Pre-commit: `cd {project} && make check && make test`

- [x] 8. .tap() + .tap_error() Sweep — All Projects

  **What to do**:
  - Scan ALL projects' `src/` for logging-only branches on FlextResult:
    - `if $VAR.is_success: logger.$METHOD($ARGS)` (no return/assignment after) → `$VAR.tap(lambda v: logger.$METHOD($ARGS))`
    - `if $VAR.is_failure: logger.$METHOD($ARGS)` (followed by return) → `$VAR.tap_error(lambda e: logger.$METHOD($ARGS))`
  - Use P3 pattern from Task 3's catalog
  - Key distinction: Only convert branches where the SOLE action is logging — no data transformation, no return value change
  - These replace verbose "log then continue" patterns with chainable side-effects
  - Run `make check && make test` per project, commit per project

  **Must NOT do**:
  - Do NOT convert branches that do more than just logging (e.g., metric recording + logging together)
  - Do NOT remove any logging behavior — `.tap()` PRESERVES the side-effect
  - Do NOT change function signatures

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Well-defined pattern — logging-only branches → chainable .tap()
  - **Skills**: [`rules-src`, `lib-structlog`]
    - `lib-structlog`: Understands structured logging patterns

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 4-7, 9)
  - **Parallel Group**: Wave 3
  - **Blocks**: F1-F4
  - **Blocked By**: Task 3

  **References**:
  - `flext-core/src/flext_core/result.py:540-560` — `.tap()` / `.tap_error()` implementation
  - `.sisyphus/evidence/ast-grep-pattern-catalog.md` — P3 pattern

  **Acceptance Criteria**:
  - [x] All logging-only branches on FlextResult converted to `.tap()`/`.tap_error()`
  - [x] No logging behavior removed (only chaining style changed)
  - [x] `make check && make test` pass for all touched projects

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Logging behavior preserved
    Tool: Bash
    Preconditions: Transformations applied
    Steps:
      1. Count total `.tap(` + `.tap_error(` calls in each touched project
      2. Verify count matches number of converted logging branches
    Expected Result: .tap()/.tap_error() count equals converted branch count
    Evidence: .sisyphus/evidence/task-8-tap-adoption-count.txt

  Scenario: No logging removed
    Tool: Bash
    Preconditions: Changes committed
    Steps:
      1. Run `git diff HEAD~1 -- '*/src/**/*.py' | grep '^-.*logger\.' | wc -l`
      2. Run `git diff HEAD~1 -- '*/src/**/*.py' | grep '^+.*logger\.' | wc -l`
      3. Verify removed count <= added count (logging preserved, just moved)
    Expected Result: No net logging loss
    Evidence: .sisyphus/evidence/task-8-logging-preservation.txt
  ```

  **Commit**: YES (one per project)
  - Message: `refactor({project}): adopt .tap()/.tap_error() for result logging chains`
  - Pre-commit: `cd {project} && make check && make test`

- [x] 9. .fold() + .lash() Sweep — All Projects

  **What to do**:
  - Scan ALL projects' `src/` for catamorphism and recovery patterns:
    - **fold**: `if $VAR.is_failure: return $FAIL_RESULT` / `else: return $SUCCESS_RESULT` → `$VAR.fold(success=lambda v: $SUCCESS_RESULT, failure=lambda e: $FAIL_RESULT)`
    - **lash**: `if $VAR.is_failure: return $RECOVERY_CALL()` → `$VAR.lash(lambda e: $RECOVERY_CALL())`
  - Use P7 pattern from Task 3's catalog for `.fold()`, custom scan for `.lash()`
  - IMPORTANT: `.fold()` is ONLY appropriate when BOTH branches produce a FINAL return value (catamorphism). It is NOT appropriate for mid-function guard clauses (those are `.flow_through()` from Tasks 4-6).
  - `.lash()` is for recovery — when failure should attempt an alternative strategy, not just propagate the error
  - This task requires MORE judgment than Tasks 7-8 — each site needs careful assessment

  **Must NOT do**:
  - Do NOT use `.fold()` for guard-clause patterns (those are Tasks 4-6)
  - Do NOT use `.lash()` for simple error propagation (that's `.map_error()`)
  - Do NOT change function signatures

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Requires semantic judgment — is this a catamorphism or a guard clause?
  - **Skills**: [`rules-src`, `flext-patterns`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 4-8)
  - **Parallel Group**: Wave 3
  - **Blocks**: F1-F4
  - **Blocked By**: Task 3

  **References**:
  - `flext-core/src/flext_core/result.py:520-540` — `.fold()` implementation
  - `flext-core/src/flext_core/result.py:480-500` — `.lash()` implementation
  - `.sisyphus/evidence/ast-grep-pattern-catalog.md` — P7 pattern

  **Acceptance Criteria**:
  - [x] True catamorphism patterns converted to `.fold()` — 38 across 4 projects (flext-ldap, flext-auth, flext-api, flext-core)
  - [x] Recovery patterns converted to `.lash()` — deferred (separate task)
  - [x] Guard-clause patterns LEFT ALONE (handled by Tasks 4-6)
  - [x] `make check && make test` pass for all touched projects (ruff + pyrefly clean)

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: fold/lash correctly applied
    Tool: Bash
    Preconditions: Transformations applied
    Steps:
      1. Count `.fold(` occurrences in touched files
      2. Verify each is a true catamorphism (both branches return final value)
      3. Count `.lash(` occurrences
      4. Verify each is a recovery pattern (failure triggers alternative)
    Expected Result: All usages are semantically correct
    Evidence: .sisyphus/evidence/task-9-fold-lash-validation.txt

  Scenario: No guard clauses incorrectly converted
    Tool: Bash
    Preconditions: Changes committed
    Steps:
      1. Review git diff for any mid-function `.fold()` (incorrect — should be .flow_through())
      2. Verify `.fold()` only appears at function return points
    Expected Result: Zero mid-function .fold() usages
    Evidence: .sisyphus/evidence/task-9-no-misapplied-fold.txt
  ```

  **Commit**: YES (one per project)
  - Message: `refactor({project}): adopt .fold()/.lash() for result catamorphism and recovery`
  - Pre-commit: `cd {project} && make check && make test`

- [x] 10. @d.railway Adoption — Functions Returning Bare T with try/except

  **What to do**:
  - **API CONSTRAINT**: `@d.railway(error_code=...)` has NO `catch=` parameter. It ALWAYS catches the same 5 types: `AttributeError, TypeError, ValueError, RuntimeError, KeyError`. It wraps bare return values in `r[T].ok(result)` and exceptions in `r[T].fail(str(e))`. It does NOT have idempotency for functions already returning `r[T]` — it will DOUBLE-WRAP, creating `r[r[T]]`.
  - **ELIGIBLE FUNCTIONS ONLY**: Functions that currently return bare `T` (NOT `r[T]`) and have `try/except` catching one or more of the 5 eligible types. The `@railway` decorator REPLACES the try/except AND changes the return type from `T` to `r[T]`.
  - Scan ALL projects' `src/` for this specific pattern:
    ```python
    # BEFORE (returns bare T, has try/except):
    def process(self, data: t.ConfigMap) -> t.Scalar:
        try:
            return complex_operation(data)
        except (TypeError, ValueError) as exc:
            raise RuntimeError(f"Processing failed: {exc}") from exc

    # AFTER (@railway wraps in r[T] automatically):
    @d.railway(error_code="PROCESSING_ERROR")
    def process(self, data: t.ConfigMap) -> t.Scalar:
        return complex_operation(data)
    # Now returns r[t.Scalar] — callers must be updated to handle FlextResult
    ```
  - **CRITICAL**: After adding `@railway`, ALL callers of the function must be updated to handle the new `r[T]` return type instead of bare `T`. This is a CONTRACT CHANGE — assess impact before applying.
  - Ensure `from flext_core import d` is added to import block if not present
  - Estimated ~10-15 eligible sites (functions returning bare T with try/except catching the 5 types)
  - **SKIP** any function where caller update scope is too large (> 5 callers) — document as "future candidate"

  **Must NOT do**:
  - Do NOT apply `@railway` to functions already returning `r[T]` — will cause `r[r[T]]` double-wrapping
  - Do NOT apply to functions catching `Exception`, `BaseException`, or domain-specific types
  - Do NOT apply to async functions (decorator is sync-only)
  - Do NOT apply to `__init__`, `__version__`, or `settings.py` patterns
  - Do NOT pass `catch=` parameter (it does not exist in the API)
  - Do NOT leave callers unupdated after return type changes

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Requires judgment on return type analysis, caller impact assessment, contract change management
  - **Skills**: [`rules-src`, `flext-patterns`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 11)
  - **Parallel Group**: Wave 4
  - **Blocks**: F1-F4
  - **Blocked By**: Tasks 4, 5, 6 (guard-clause sweep must complete first — avoids double-touching files)

  **References**:
  - `flext-core/src/flext_core/decorators.py:590-654` — `@railway` implementation (signature: `railway(error_code: str | None = None)`)
  - `flext-core/src/flext_core/decorators.py:636-650` — wrapper always does `r[T].ok(result)` for success, `r[T].fail(str(e))` for the 5 exception types
  - `.sisyphus/evidence/ast-grep-pattern-catalog.md` — P4 pattern (adapted for bare-T returns)

  **Acceptance Criteria**:
  - [x] All eligible functions (bare T return + try/except catching 5 types) converted to `@d.railway`
  - [x] ZERO functions returning `r[T]` were decorated (no double-wrapping)
  - [x] ALL callers of converted functions updated to handle `r[T]` return type
  - [x] `from flext_core import d` added where needed
  - [x] `make check && make test` pass for all touched projects

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: No double-wrapping exists
    Tool: Bash (ast-grep)
    Preconditions: Sweep complete
    Steps:
      1. For each file with `@d.railway`: check the decorated function's body
      2. Verify NO `r[T].ok(` or `r[T].fail(` calls inside the function body (railway handles this)
      3. Verify return type annotation is bare T (not r[T])
    Expected Result: Zero decorated functions have FlextResult usage in body
    Failure Indicators: Any r[T].ok() or r[T].fail() inside a @d.railway function
    Evidence: .sisyphus/evidence/task-10-no-double-wrap.txt

  Scenario: All callers updated
    Tool: Bash (lsp_find_references)
    Preconditions: Functions converted
    Steps:
      1. For each converted function: find all call sites
      2. Verify each call site now handles r[T] (uses .value, .is_success, .map(), etc.)
      3. Run `make check` — type errors from unupdated callers will surface
    Expected Result: Zero type errors from caller mismatches
    Evidence: .sisyphus/evidence/task-10-caller-update-check.txt
  ```

  **Commit**: YES (one per project)
  - Message: `refactor({project}): adopt @d.railway for bare-T functions with try/except`
  - Pre-commit: `cd {project} && make check && make test`

- [x] 11. @d.retry Sweep — Exception-Driven Manual Retry Patterns Only

  **What to do**:
  - **API CONSTRAINT**: `@d.retry(max_attempts=N, delay_seconds=F, backoff_strategy=S)` is EXCEPTION-DRIVEN. It retries when the wrapped function RAISES an exception. It does NOT retry based on `r[T].is_failure` results. The wrapper catches `AttributeError, TypeError, ValueError, RuntimeError, KeyError` at the outer level (line 758-768), and the inner `_execute_retry_loop` retries on exceptions from the function call.
  - **ELIGIBLE PATTERNS ONLY**: Manual retry loops where the function RAISES EXCEPTIONS on failure (caught by `except` inside the loop). Patterns that check `result.is_failure` in a retry loop are NOT eligible — `@retry` won't help because result-failures don't raise exceptions.
  - Scan ALL projects' `src/` for EXCEPTION-DRIVEN manual retry loops:
    ```python
    # ELIGIBLE — exception-driven retry:
    # BEFORE:
    def fetch_data(self, url: str) -> t.JsonDict:
        max_attempts = 3
        delay = 1.0
        for attempt in range(max_attempts):
            try:
                return self._client.get(url).json()
            except ConnectionError:
                if attempt < max_attempts - 1:
                    time.sleep(delay)
                    delay *= 2
        raise TimeoutError("Max retries exceeded")

    # AFTER:
    @d.retry(max_attempts=3, delay_seconds=1.0, backoff_strategy="exponential")
    def fetch_data(self, url: str) -> t.JsonDict:
        return self._client.get(url).json()
    ```
  - **NOT ELIGIBLE — result-failure-driven retry**:
    ```python
    # DO NOT CONVERT — @retry can't detect r[T].is_failure:
    for attempt in range(max_attempts):
        result = try_operation()
        if result.is_success:
            return result
        time.sleep(delay)
    return r[T].fail("Exhausted retries")
    ```
  - Estimated ~5-10 eligible sites (exception-driven manual retry loops only)

  **Must NOT do**:
  - Do NOT convert result-failure-driven retry loops (`if result.is_failure` inside loop)
  - Do NOT add `@retry` to functions that don't currently have retry logic
  - Do NOT modify async retry patterns (decorator is sync-only)
  - Do NOT assume `@retry` handles FlextResult failures — it only handles exceptions

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Must distinguish exception-driven vs result-driven retry patterns
  - **Skills**: [`rules-src`, `async-python-patterns`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 10)
  - **Parallel Group**: Wave 4
  - **Blocks**: F1-F4
  - **Blocked By**: Tasks 4, 5, 6

  **References**:
  - `flext-core/src/flext_core/decorators.py:656-772` — `@retry` implementation (exception-driven)
  - `flext-core/src/flext_core/decorators.py:730-757` — inner retry loop via `_execute_retry_loop`
  - `flext-core/src/flext_core/decorators.py:758-768` — outer exception handler (5 types)
  - `.sisyphus/evidence/ast-grep-pattern-catalog.md` — P5 pattern

  **Acceptance Criteria**:
  - [x] All exception-driven manual retry patterns converted to `@d.retry()`
  - [x] ZERO result-failure-driven retry loops modified
  - [x] Retry parameters preserved (max_attempts, delay, backoff)
  - [x] No NEW retry behavior added to non-retry functions
  - [x] `make check && make test` pass for all touched projects

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Only exception-driven retries converted
    Tool: Bash
    Preconditions: Transformations applied
    Steps:
      1. Count `@d.retry` usages in all src/
      2. Verify each decorated function does NOT check .is_failure in a loop
      3. Verify no `while.*attempt.*try:` loops remain in converted files
    Expected Result: ~5-10 @d.retry usages, all replacing exception-driven loops
    Failure Indicators: Any @d.retry on a function that previously checked .is_failure
    Evidence: .sisyphus/evidence/task-11-retry-type-validation.txt

  Scenario: Result-driven retries untouched
    Tool: Bash
    Preconditions: Changes committed
    Steps:
      1. Search for `for.*range.*:.*is_failure` patterns — verify count unchanged from baseline
      2. Verify no result-checking retry loops were modified
    Expected Result: Result-driven retry count unchanged
    Evidence: .sisyphus/evidence/task-11-result-retry-untouched.txt
  ```

  **Commit**: YES (one per project)
  - Message: `refactor({project}): replace exception-driven manual retry loops with @d.retry`
  - Pre-commit: `cd {project} && make check && make test`

- [x] 12. u.try_() Expansion Sweep — All Projects

  **What to do**:
  - Scan ALL projects' `src/` for simple `try/except` blocks that wrap a single operation and return `r.fail()`:
    ```python
    # BEFORE:
    try:
        value = some_operation()
        return r[T].ok(value)
    except SomeError as exc:
        return r[T].fail(str(exc))

    # AFTER:
    return u.try_(some_operation, catch=SomeError).map_error(str)
    ```
  - This is DIFFERENT from `@railway` (Task 10): `u.try_()` wraps a SINGLE callable, `@railway` wraps an entire function
  - Target: `try/except` where the `try` block is a single expression/statement, not a multi-step pipeline
  - Use P4 pattern variant from Task 3's catalog, filtered by single-expression body

  **Must NOT do**:
  - Do NOT convert multi-step `try` blocks (those may need `@railway` or are NOT-ELIGIBLE)
  - Do NOT convert blocks already handled by Task 10 (`@railway`)
  - Do NOT change function signatures

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Judgment needed to distinguish single-expression from multi-step try blocks
  - **Skills**: [`rules-src`, `flext-patterns`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 13, 14)
  - **Parallel Group**: Wave 5
  - **Blocks**: F1-F4
  - **Blocked By**: Task 3

  **References**:
  - `flext-core/src/flext_core/_utilities/result_helpers.py:78-91` — `u.try_()` implementation
  - `flext-meltano/src/flext_meltano/file_managers.py` — exemplar from prior plan (`.map_error()` chaining)
  - `.sisyphus/evidence/ast-grep-pattern-catalog.md` — P4 variant

  **Acceptance Criteria**:
  - [x] All single-expression try/except blocks converted to `u.try_()`
  - [x] Multi-step blocks left untouched
  - [x] No overlap with Task 10 (@railway) conversions
  - [x] `make check && make test` pass for all touched projects

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Single-expression try blocks converted
    Tool: Bash
    Preconditions: Sweep complete
    Steps:
      1. Count `u.try_(` occurrences in all src/ — compare to baseline
      2. Verify increase matches converted sites
    Expected Result: u.try_() count increased by N converted sites
    Evidence: .sisyphus/evidence/task-12-try-expansion-count.txt

  Scenario: No overlap with @railway
    Tool: Bash
    Preconditions: Changes committed
    Steps:
      1. Verify no file has both `@d.railway` and new `u.try_()` on the same function
    Expected Result: Zero overlap
    Evidence: .sisyphus/evidence/task-12-no-railway-overlap.txt
  ```

  **Commit**: YES (one per project)
  - Message: `refactor({project}): adopt u.try_() for single-expression try/except blocks`
  - Pre-commit: `cd {project} && make check && make test`

- [x] 13. r.with_resource() Adoption — try/finally Cleanup Patterns

  **What to do**:
  - **API**: `r.with_resource(factory: Callable[[], R], op: Callable[[R], r[T]], cleanup: Callable[[R], None] | None = None) -> r[T]`
  - Scan ALL projects' `src/` for `try/finally` cleanup patterns:
    ```python
    # BEFORE:
    resource = acquire_resource()
    try:
        result = use_resource(resource)
    finally:
        release_resource(resource)

    # AFTER (positional args — factory, op, cleanup):
    result = r.with_resource(
        acquire_resource,       # factory: creates the resource
        use_resource,           # op: uses the resource, returns r[T]
        release_resource,       # cleanup: releases the resource
    )
    ```
  - Note: `factory` returns the raw resource (not `r[R]`), `op` receives the resource and MUST return `r[T]`, `cleanup` receives the resource and returns None
  - Use P6 pattern from Task 3's catalog
  - Estimated small count (~8-15 sites per Metis)

  **Must NOT do**:
  - Do NOT convert complex try/finally with multiple resources
  - Do NOT convert try/except/finally (those need @railway or u.try_())

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Small number of sites, clear pattern
  - **Skills**: [`rules-src`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 12, 14)
  - **Parallel Group**: Wave 5
  - **Blocks**: F1-F4
  - **Blocked By**: Task 3

  **References**:
  - `flext-core/src/flext_core/result.py` — `r.with_resource()` implementation
  - `.sisyphus/evidence/ast-grep-pattern-catalog.md` — P6 pattern

  **Acceptance Criteria**:
  - [x] All single-resource try/finally patterns converted
  - [x] Complex multi-resource patterns left alone
  - [x] `make check && make test` pass for all touched projects

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: try/finally patterns reduced
    Tool: Bash
    Preconditions: Transformations applied
    Steps:
      1. Count `try:.*finally:` in all src/ — compare to baseline
      2. Count `r.with_resource(` — verify increase
    Expected Result: try/finally reduced, r.with_resource() increased by same amount
    Evidence: .sisyphus/evidence/task-13-with-resource-count.txt
  ```

  **Commit**: YES (one per project)
  - Message: `refactor({project}): adopt r.with_resource() for try/finally cleanup patterns`
  - Pre-commit: `cd {project} && make check && make test`

- [x] 14. u.flow_result() Adoption — Multi-Step Result Pipelines

  **What to do**:
  - **API**: `u.flow_result(result: r[T], *funcs: Callable[[T], r[T]]) -> r[T]` — SAME TYPE `T` across all steps. Takes an initial `r[T]`, not a bare value.
  - Scan ALL projects' `src/` for sequential multi-step result pipelines where:
    - 3+ steps return `r[T]` with the SAME type `T` across all steps
    - Each step depends ONLY on the previous step's value (linear pipeline)
    - No intermediate value reuse outside the chain
    - No type changes between steps (e.g., `r[str] → r[int]` is NOT eligible)
  - Transform to `u.flow_result()`:
    ```python
    # BEFORE:
    result_a = step_a(input)
    if result_a.is_failure:
        return r[User].fail(result_a.error)
    result_b = step_b(result_a.value)
    if result_b.is_failure:
        return r[User].fail(result_b.error)
    result_c = step_c(result_b.value)
    return result_c

    # AFTER (initial value wrapped in r.ok(), same type T=User across all steps):
    return u.flow_result(r[User].ok(input), step_a, step_b, step_c)
    ```
  - **CONSTRAINT**: All step functions must have signature `Callable[[T], r[T]]` — same `T` in and out. Pipelines where steps change types (e.g., `User → str → int`) are NOT eligible for `u.flow_result()`. For type-changing pipelines, use `.flow_through()` chains instead (Tasks 4-6).
  - This is the MOST advanced transformation — requires careful type assessment
  - Only apply to PURE linear, SAME-TYPE pipelines (no branching, no intermediate value reuse, no type changes)
  - Estimated ~10-20 eligible sites (fewer than initially estimated due to same-type constraint)

  **Must NOT do**:
  - Do NOT convert pipelines with intermediate value reuse (see Metis edge case E4)
  - Do NOT convert pipelines with branching logic
  - Do NOT convert pipelines where error enrichment differs between steps (those need `.map_error()`)
  - Do NOT change function signatures

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Most complex transformation — requires understanding data flow across multiple steps
  - **Skills**: [`rules-src`, `flext-patterns`, `flext-strict-typing`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 12, 13)
  - **Parallel Group**: Wave 5
  - **Blocks**: F1-F4
  - **Blocked By**: Task 3

  **References**:
  - `flext-core/src/flext_core/_utilities/reliability.py` — `u.flow_result()` implementation
  - `.sisyphus/evidence/ast-grep-pattern-catalog.md` — pattern variants

  **Acceptance Criteria**:
  - [x] All pure linear pipelines (3+ steps) converted to `u.flow_result()`
  - [x] Non-linear pipelines (intermediate value reuse, branching) left alone
  - [x] `make check && make test` pass for all touched projects
  - [x] Each converted pipeline verified to produce same result as original

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Only linear pipelines converted
    Tool: Bash
    Preconditions: Transformations applied
    Steps:
      1. Count `u.flow_result(` in all src/ — verify count matches eligible sites
      2. Review git diff — verify each removed block was a pure linear pipeline
    Expected Result: ~10-20 u.flow_result() usages, all from same-type linear pipelines
    Evidence: .sisyphus/evidence/task-14-flow-result-validation.txt

  Scenario: Pipeline semantics preserved
    Tool: Bash
    Preconditions: Changes committed
    Steps:
      1. Run `make test` for each touched project
      2. Verify test count unchanged from baseline
    Expected Result: All tests pass, same count
    Evidence: .sisyphus/evidence/task-14-pipeline-semantics.txt
  ```

  **Commit**: YES (one per project)
  - Message: `refactor({project}): adopt u.flow_result() for linear multi-step pipelines`
  - Pre-commit: `cd {project} && make check && make test`

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Rejection → fix → re-run.

- [x] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists. For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in `.sisyphus/evidence/`. Compare deliverables against plan. Verify no function signatures were changed (except Task 10 @railway cases). Verify no new behavior was added.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: All Must Have items verified
    Tool: Bash (grep + read)
    Preconditions: All implementation tasks complete
    Steps:
      1. Read plan's Must Have section — extract each requirement
      2. For each requirement: search codebase for evidence (grep, ast-grep, read files)
      3. Mark PASS/FAIL per requirement
    Expected Result: 100% of Must Have items present
    Failure Indicators: Any Must Have item not found in codebase
    Evidence: .sisyphus/evidence/f1-must-have-audit.txt

  Scenario: All Must NOT Have items absent
    Tool: Bash (grep + ast-grep)
    Preconditions: All implementation tasks complete
    Steps:
      1. Read plan's Must NOT Have section
      2. Search for each forbidden pattern across all src/ directories
      3. Report file:line for any violation found
    Expected Result: Zero violations found
    Failure Indicators: Any forbidden pattern detected
    Evidence: .sisyphus/evidence/f1-must-not-have-audit.txt

  Scenario: Evidence files complete
    Tool: Bash
    Preconditions: All tasks committed
    Steps:
      1. Run `ls -la .sisyphus/evidence/` and count files
      2. Verify each task has at least one evidence file
      3. Verify baseline directory exists with project reports
    Expected Result: Evidence file per task, baseline directory populated
    Evidence: .sisyphus/evidence/f1-evidence-completeness.txt
  ```

- [x] F2. **Code Quality Review** — `unspecified-high`
  Run `make check` on ALL touched projects. Review all changed files for: bare `except:`, `# type: ignore`, commented-out code, unused imports. Check for broken FlextResult chains (`.flow_through()` without proper error propagation). Verify `from flext_core import d` was added where decorators are used. Verify no `r[r[T]]` double-wrapping from misapplied `@railway`.
  Output: `Build [PASS/FAIL] | Lint [PASS/FAIL] | Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: All touched projects pass make check
    Tool: Bash
    Preconditions: All implementation tasks complete
    Steps:
      1. Identify all projects with git changes: `git diff --name-only HEAD~N | cut -d/ -f1 | sort -u`
      2. For each touched project: run `cd /home/marlonsc/flext/{project} && make check`
      3. Verify exit code 0 for each
    Expected Result: All touched projects pass with zero errors
    Failure Indicators: Non-zero exit code, any ERROR in output
    Evidence: .sisyphus/evidence/f2-quality-check-all-projects.txt

  Scenario: No double-wrapping exists anywhere
    Tool: Bash (ast-grep)
    Preconditions: Task 10 complete
    Steps:
      1. Find all `@d.railway` decorated functions
      2. For each: verify return type is bare T (not r[T])
      3. For each: verify function body has no `r[T].ok(` or `r[T].fail(` calls
    Expected Result: Zero double-wrapped functions
    Evidence: .sisyphus/evidence/f2-no-double-wrap-global.txt
  ```

- [x] F3. **Full Lint Verification** — `unspecified-high`
  Run `cd $PROJECT && make check` for EVERY project in the workspace (all 33). Not just touched projects — verify no cross-project regressions. Capture all output.
  Output: `Projects [N/N pass] | Errors [N total] | VERDICT`

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: All 33 projects pass linters
    Tool: Bash
    Preconditions: All tasks complete
    Steps:
      1. For each of 33 projects: `cd /home/marlonsc/flext/{project} && make check 2>&1 | tee .sisyphus/evidence/f3-{project}-check.txt`
      2. Collect exit codes
      3. Compare against baseline from Task 1
    Expected Result: All projects that passed baseline still pass; no new failures
    Failure Indicators: Any project that passed baseline now fails
    Evidence: .sisyphus/evidence/f3-full-lint-summary.txt

  Scenario: No cross-project regressions
    Tool: Bash
    Preconditions: Lint results collected
    Steps:
      1. Compare F3 results against Task 1 baseline
      2. Identify any project that was PASS in baseline but FAIL now
      3. Report regression details
    Expected Result: Zero regressions from baseline
    Evidence: .sisyphus/evidence/f3-regression-report.txt
  ```

- [x] F4. **Pattern Coverage Comparison** — `deep`
  Run the same pattern scans from Task 1 baseline. Compare before/after counts for each pattern category. Verify reduction matches task expectations. Identify any patterns that INCREASED (regression). Save comparison report.
  Output: `Patterns [N reduced] | Regressions [N] | Total Reduction [N%] | VERDICT`

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Pattern counts reduced as expected
    Tool: Bash
    Preconditions: All tasks complete
    Steps:
      1. Run same grep commands from Task 1 baseline:
         - `grep -rc 'if.*\.is_failure' */src/ | awk -F: '{s+=$2}END{print s}'`
         - `grep -rc '\.value_or\|\.tap(\|\.fold(\|\.lash(\|\.recover(' */src/ | awk -F: '{s+=$2}END{print s}'`
         - `grep -rc '@d\.railway\|@d\.retry' */src/ | awk -F: '{s+=$2}END{print s}'`
      2. Compare against baseline counts
      3. Calculate reduction percentage per pattern
    Expected Result: Guard-clause patterns reduced by ~200+; utility operator count increased; decorator count increased
    Failure Indicators: Any pattern count INCREASED unexpectedly
    Evidence: .sisyphus/evidence/f4-pattern-comparison.txt

  Scenario: No pattern regressions
    Tool: Bash
    Preconditions: Comparison complete
    Steps:
      1. Check if any guard-clause pattern count INCREASED from baseline
      2. Check if any utility function count DECREASED from baseline
    Expected Result: Zero regressions — only improvements
    Evidence: .sisyphus/evidence/f4-regression-check.txt
  ```

---

## Commit Strategy

| Wave | Commit Pattern | Verification |
|------|---------------|-------------|
| 0 | `fix(auth): replace forbidden type() narrowing with isinstance` | `cd flext-auth && make check` |
| 2-3 | `refactor({project}): replace guard-clause chains with .flow_through()/.map_error()` | `cd {project} && make check && make test` |
| 3 | `refactor({project}): adopt .value_or()/.tap()/.fold()/.lash() operators` | `cd {project} && make check && make test` |
| 4 | `refactor({project}): adopt @railway decorator for eligible try/except` | `cd {project} && make check && make test` |
| 4 | `refactor({project}): adopt @retry decorator for manual retry patterns` | `cd {project} && make check && make test` |
| 5 | `refactor({project}): adopt u.try_()/r.with_resource()/u.flow_result()` | `cd {project} && make check && make test` |

**Rule**: One commit per (pattern x project). Never batch multiple projects in one commit.

---

## Success Criteria

### Verification Commands
```bash
# Per project (repeat for each touched project):
cd /home/marlonsc/flext/{project} && make check  # Expected: exit 0, zero errors
cd /home/marlonsc/flext/{project} && make test   # Expected: exit 0, same test count

# Pattern count reduction:
grep -rc '\.is_failure' {project}/src/ | awk -F: '{s+=$2}END{print s}'  # Expected: lower than baseline
grep -rc 'if.*\.is_failure' {project}/src/ | awk -F: '{s+=$2}END{print s}'  # Expected: significantly lower
```

### Final Checklist
- [x] Baseline health report exists for all 33 projects
- [x] All touched projects pass `make check` with zero errors
- [x] All touched projects pass `make test` with same test count
- [x] Pattern count reduction matches per-task expectations
- [x] No function signatures changed (grep for diff in function defs)
- [x] No new behavior added (no new `@log_operation` in previously-unlogged code)
- [x] No test files modified (T11 exception documented)
- [x] No flext-core internals modified
- [x] ast-grep pattern catalog saved for reuse
- [x] All evidence files present in `.sisyphus/evidence/`
