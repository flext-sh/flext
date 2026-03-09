# ARCHIVED — Subsumed by modernization-reorg-execution.md

# Workspace Zero Quality Gates — All 32 Projects

## TL;DR

> **Quick Summary**: Bring every project in the flext workspace to `make check = 0` (all 8 quality gates pass) by fixing root causes with strong typing from flext-core's type system. No shortcuts, no config weakening, no behavior changes.
>
> **Deliverables**:
> - `make check` exit code 0 for all 32 projects
> - `make validate VALIDATE_SCOPE=workspace` exit code 0
> - Zero new suppressions (no cast, Any, type:ignore, noqa added)
> - One commit per project, all submodule refs updated
>
> **Estimated Effort**: XL (32 projects × 8 gates × src/tests/examples)
> **Parallel Execution**: YES — 5+ waves
> **Critical Path**: Phase 0 → Phase 1 → Phase 2 (flext-core) → Phase 3 (consumers by tier) → Phase 4 (final)

---

## Context

### Original Request
"Planeje fazer isso para toda a workspace flext em todos os projetos, em src/ tests/ scripts and examples/" — Fix all quality gate errors across the entire workspace using root-cause fixes with strong typing per flext-core's type system.

### Interview Summary
**Key Discussions**:
- Sequencing: Parallel where possible, flext-core first (foundation)
- Quality target: `make check = 0` per project (all 8 gates)
- Priority: Core → consumers → taps → targets → dbt → misc
- Strictness: Tests get same treatment as src/ — zero tolerance
- Method: Root-cause ONLY — fix the code, not the config

**Research Findings**:
- 32 projects total (30 submodules + 2 external: algar-oud-mig, gruponos-meltano-native)
- All share base.mk with 8 gates: lint, format, pyrefly, mypy, pyright, security, markdown, go
- Go gate only applies to `flexcore` project (CORE_STACK=go)
- Security gate (bandit) only checks src/ — not tests/examples
- flext-core src/ already clean (0 errors, 177 files) — needs re-verification
- flext-core tests/ has ~253 mypy errors in 47 files (partially fixed this session)
- Workspace mypy src/ heatmap: ~1,463 errors (STALE — baseline capture needed)
- 4 projects have local [tool.mypy] overrides deviating from workspace config
- 7 existing mypy override blocks in workspace pyproject.toml (pre-existing tech debt)
- Pyrefly tests/ suppresses ONLY `bad-argument-type` — all other errors active
- `.flext-deps/` vendored directories must be excluded

### Metis Review
**Identified Gaps** (addressed in plan):
- Q1: "make check = 0" defined as exit code 0 from `make check` (all gates pass)
- Q2: Existing 7 mypy overrides in workspace config → OUT OF SCOPE (pre-existing debt)
- Q3: 4 local mypy configs → unify to workspace config in Phase 1
- Q5: `make test` must also pass → added as acceptance criteria
- SC1-SC6: Scope creep locks defined in Guardrails
- A1-A6: All assumptions validated via Phase 0 baseline
- AC1-AC6: Acceptance criteria fully specified
- E1-E8: Edge cases addressed in tasks and guardrails

---

## Work Objectives

### Core Objective
Achieve `make check` exit code 0 (all 8 quality gates pass) for every project in the flext workspace, for src/, tests/, and examples/ directories, through root-cause type fixes only.

### Concrete Deliverables
- All 32 projects: `make check` = exit 0
- All 32 projects: `make test` = same or better pass count vs baseline
- Workspace: `make validate VALIDATE_SCOPE=workspace` = exit 0
- Zero new suppressions across all commits
- Baseline report at `.reports/check/baseline/`
- Final report at `.reports/check/final/`

### Definition of Done
- [ ] `make check` from workspace root = exit 0
- [ ] `git submodule foreach 'git status --porcelain'` = empty (all committed)
- [ ] `git diff HEAD~N -- '*.py' | grep -cE '# type: ignore|cast\(|: Any\b|# noqa'` = 0 (no new suppressions)
- [ ] `.reports/check/final/summary.json` shows 0 errors per project per gate

### Must Have
- Root-cause fixes using flext-core type system (t.*, m.*, p.*, etc.)
- isinstance narrowing (never type()) for type narrowing
- Pydantic v2 patterns, `from __future__ import annotations` everywhere
- Python 3.13+ syntax
- One commit per project (submodule + parent ref update)

### Must NOT Have (Guardrails)
- **G1**: NEVER use `cast()`, `Any`, `# type: ignore`, `object` as type, `eval()`, `exec()`, `model_rebuild()`, inline imports
- **G2**: NEVER modify workspace `pyproject.toml` [tool.mypy] overrides (7 existing blocks) without dedicated impact assessment task
- **G3**: NEVER modify `_CombinedModelMeta` or `ProtocolModelMeta` without Oracle consultation first
- **G4**: NEVER modify `[MANAGED]` pyrefly config sections — the fix-pyrefly-config fixer manages these
- **G5**: NEVER create custom type stubs in `typings/` without Oracle review
- **G6**: NEVER touch `.flext-deps/` vendored directories
- **G7**: NEVER change test behavior (assertions, expected values, test coverage) — only type annotations, return types, and imports
- **G8**: Root-cause fixes must be MINIMAL — if a fix touches >20 lines per error, it needs Oracle review
- **G9**: `make check` is the ONLY acceptance oracle — not individual tool runs
- **G10**: After ANY flext-core type system change, re-verify ALL 32 projects (not just 3) with `make check CHECK_GATES=mypy,pyright,pyrefly`
- **G11**: Do NOT remove existing mypy overrides in workspace config — they are pre-existing debt, out of scope
- **G12**: Pyrefly tests/ only suppresses `bad-argument-type` — all other pyrefly errors are ACTIVE in tests/
- **G13**: Security gate (bandit) only checks src/ — no need to fix security issues in tests/examples
- **G14**: For external projects (algar-oud-mig, gruponos-meltano-native): commit directly, not as submodule

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES (pytest, make test)
- **Automated tests**: NO new tests — existing tests must PASS (same or better count)
- **Framework**: pytest (all projects)

### QA Policy
Every task MUST execute verification commands and capture evidence.
Evidence saved to `.reports/check/<project>/<phase>/`.

- **Per-project gate check**: `cd <project> && make check` → exit 0
- **Per-gate check**: `cd <project> && make check CHECK_GATES=<gate>` → exit 0
- **No-new-suppressions**: `git diff HEAD~1 -- '*.py' | grep -cE '# type: ignore|cast\(|: Any\b|# noqa'` → 0
- **Submodule integrity**: `git submodule status <project>` → no leading '+'
- **Test integrity**: `cd <project> && make test` → same or better pass count

### Gate Order (cheapest first)
1. `lint` — ruff check (auto-fixable with `make format`)
2. `format` — ruff format --check (auto-fixable with `make format`)
3. `security` — bandit (src/ only)
4. `markdown` — mdformat/markdownlint
5. `mypy` — strict type checking
6. `pyright` — complementary type checking
7. `pyrefly` — Meta's type checker
8. `go` — only for flexcore project

---

## Execution Strategy

### Parallel Execution Waves

```
Phase 0 — BASELINE (measurement only, zero code changes):
├── T1: Baseline capture for all 32 projects [deep]
└── T2: Verify flext-core src/ still clean [quick]

Phase 1 — CONFIG/INFRA (unblock type checking):
├── T3: Fix 6 invalid package names in pyproject.toml [quick]
├── T4: Fix mypy_path source-found-twice in workspace config [quick]
├── T5: Unify 4 local mypy configs to workspace config [deep]
├── T6: Verify .flext-deps/ exclusion patterns [quick]
├── T7: Run make format per project (auto-fix lint+format) [quick]
└── T8: Re-run baseline to measure config fix delta [quick]

Phase 2 — FLEXT-CORE TYPE SYSTEM (foundation for all consumers):
├── T9: Fix MetaclassConflict (Oracle consultation required) [ultrabrain]
├── T10: Fix DomainEvent valid-type (Oracle consultation required) [ultrabrain]
├── T11: Fix flext-core tests/ — tomlkit index errors (85 errors, 3 files) [deep]
├── T12: Fix flext-core tests/ — handler/dispatcher protocol (22 errors, 2 files) [deep]
├── T13: Fix flext-core tests/ — guards input type design (24 errors, 1 file) [deep]
├── T14: Fix flext-core tests/ — registry handler protocol (14 errors, 2 files) [deep]
├── T15: Fix flext-core tests/ — remaining var-annotated/union-attr (60+ errors, 30+ files) [deep]
├── T16: Fix flext-core tests/ — DomainEvent/MetaclassConflict refs (9+ errors) [deep]
├── T17: Fix flext-core examples/ [quick]
├── T18: make check PROJECT=flext-core → exit 0 [quick]
└── T19: Cascade verification — ALL 32 projects after core changes [deep]

Phase 3 — CONSUMER PROJECTS (by tier, max parallel):

  Wave 3A — LOW errors (1-9 mypy, likely few other gates):
  ├── T20: flext-quality (1 mypy) [quick]
  ├── T21: flext-oracle-oic (1 mypy) [quick]
  ├── T22: flext-target-oracle-oic (1 mypy) [quick]
  ├── T23: flext-tap-oracle (2 mypy) [quick]
  ├── T24: flext-grpc (2 mypy + protobuf exclusion) [quick]
  ├── T25: flext-target-oracle-wms (3 mypy) [quick]
  ├── T26: flext-web (4 mypy) [quick]
  └── T27: flext-tap-oracle-wms (4 mypy) [quick]

  Wave 3B — MEDIUM errors (6-43 mypy):
  ├── T28: flext-target-ldif (6 mypy) [unspecified-high]
  ├── T29: flext-dbt-oracle-wms (7 mypy) [unspecified-high]
  ├── T30: flext-dbt-ldap (9 mypy) [unspecified-high]
  ├── T31: flext-tap-ldif (13 mypy) [unspecified-high]
  ├── T32: flext-oracle-wms (29 mypy) [unspecified-high]
  ├── T33: flext-target-oracle (41 mypy) [unspecified-high]
  ├── T34: flext-ldap (42 mypy) [deep]
  └── T35: flext-tap-ldap (43 mypy) [deep]

  Wave 3C — HIGH errors (47-99 mypy):
  ├── T36: flext-tap-oracle-oic (47 mypy) [deep]
  ├── T37: flext-plugin (49 mypy) [deep]
  ├── T38: flext-cli (81 mypy + local config) [deep]
  └── T39: flext-target-ldap (99 mypy) [deep]

  Wave 3D — CRITICAL errors (100+ mypy):
  ├── T40: flext-meltano (117 mypy) [deep]
  ├── T41: flext-observability (149 mypy) [deep]
  ├── T42: flext-ldif (244 mypy) [deep]
  └── T43: flext-api (410 mypy) [deep]

  Wave 3E — CONFIG-ISSUE projects (invalid package names, post-T3 fix):
  ├── T44: flext-auth [unspecified-high]
  ├── T45: flext-db-oracle [unspecified-high]
  ├── T46: flext-dbt-ldif [unspecified-high]
  ├── T47: flext-dbt-oracle [unspecified-high]
  ├── T48: algar-oud-mig [unspecified-high]
  └── T49: gruponos-meltano-native [unspecified-high]

Phase 4 — GO + FINAL VERIFICATION:
├── T50: Fix Go gate for flexcore project [quick]
├── T51: Final workspace-wide verification [deep]

Wave FINAL — INDEPENDENT REVIEW (4 parallel):
├── F1: Plan compliance audit (oracle)
├── F2: Code quality review (unspecified-high)
├── F3: Real QA — make check from clean state (unspecified-high)
└── F4: Scope fidelity check (deep)

Critical Path: T1 → T3-T7 → T9-T10 → T18 → T19 → T20-T49 → T51 → F1-F4
Parallel Speedup: ~65% faster than sequential
Max Concurrent: 8 (Waves 3A, 3B)
```

### Dependency Matrix

| Task | Blocked By | Blocks |
|------|-----------|--------|
| T1-T2 | — | T3-T51 |
| T3-T7 | T1 | T8, T20-T49 |
| T8 | T3-T7 | T9 |
| T9-T10 | T8 | T11-T17 |
| T11-T17 | T9-T10 | T18 |
| T18 | T11-T17 | T19 |
| T19 | T18 | T20-T49 |
| T20-T27 | T19 | T51 |
| T28-T35 | T19 | T51 |
| T36-T39 | T19 | T51 |
| T40-T43 | T19 | T51 |
| T44-T49 | T3, T19 | T51 |
| T50 | T1, T19 | T51 |
| T51 | T20-T50 | F1-F4 |
| F1-F4 | T51 | — |

### Agent Dispatch Summary

| Wave | Tasks | Categories |
|------|-------|-----------|
| Phase 0 | 2 | deep, quick |
| Phase 1 | 6 | quick(5), deep(1) |
| Phase 2 | 11 | ultrabrain(2), deep(7), quick(2) |
| Wave 3A | 8 | quick(8) |
| Wave 3B | 8 | unspecified-high(5), deep(3) |
| Wave 3C | 4 | deep(4) |
| Wave 3D | 4 | deep(4) |
| Wave 3E | 6 | unspecified-high(6) |
| Phase 4 | 2 | quick(1), deep(1) |
| FINAL | 4 | oracle(1), unspecified-high(2), deep(1) |
| **TOTAL** | **55** | |

---

## TODOs

### Phase 0 — BASELINE (measurement only, zero code changes)

- [ ] 1. Baseline Capture — All 32 Projects

  **What to do**:
  - Create `.reports/check/baseline/` directory
  - For each of 32 projects: `make check PROJECT=<name> 2>&1 | tee .reports/check/baseline/<name>.txt; echo EXIT:$?`
  - For each project: `make test PROJECT=<name> 2>&1 | tail -30 > .reports/check/baseline/<name>-tests.txt`
  - Parse outputs → `.reports/check/baseline/summary.json` with structure: `{ "timestamp", "projects": { "<name>": { "gates": { "lint": N, "format": N, "mypy": N, "pyright": N, "pyrefly": N, "security": N, "markdown": N, "go": N }, "tests": { "passed": N, "failed": N }, "sha": "..." } } }`
  - Record submodule SHAs: `git submodule foreach 'echo $name $(git rev-parse HEAD)'`
  - Identify pass-through projects (already exit 0) vs projects needing work
  - **IMPORTANT**: Run from workspace root using `make check PROJECT=<name>`, never cd into project

  **Must NOT do**:
  - **G1**: Do NOT modify any source file, config, or Makefile
  - **G9**: Raw `make check` exit code is the ONLY metric

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Systematic execution of 64+ commands across 32 projects with structured aggregation
  - **Skills**: [`flext-development-workflow`, `scripts-validation`]
    - `flext-development-workflow`: Workspace make commands, PROJECT variable
    - `scripts-validation`: Validation report structure and conventions
  - **Omitted**: `rules-flext-core` (not fixing core, measuring all projects)

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T2)
  - **Parallel Group**: Phase 0
  - **Blocks**: T3-T8 (Phase 1), T50 (Go gate)
  - **Blocked By**: None (starts immediately)

  **References**:
  - `base.mk` — Gate definitions, `CHECK_GATES` variable, `check-lint`/`check-mypy`/etc. targets
  - `pyproject.toml` (workspace root) — mypy, ruff, pyrefly, pyright, bandit tool configs
  - `.reports/validate/` — May not exist yet; T1 will create `.reports/check/baseline/` with its own format
  - `Makefile` (workspace root) — `check` target, `PROJECT` variable routing

  **Acceptance Criteria**:
  - [ ] `.reports/check/baseline/summary.json` exists with valid JSON, 32 project entries
  - [ ] Each entry has counts for all 8 gates (0=pass, N>0=errors)
  - [ ] Each entry has test pass/fail counts
  - [ ] Per-project raw output at `.reports/check/baseline/<name>.txt` (32 files)
  - [ ] Git SHAs recorded for all submodules

  **QA Scenarios**:
  ```
  Scenario: Baseline JSON is complete
    Tool: Bash
    Steps:
      1. python -c "import json; d=json.load(open('.reports/check/baseline/summary.json')); assert len(d['projects'])==32, f'Got {len(d[\"projects\"])}'; print('OK: 32 projects')"
      2. python -c "import json; d=json.load(open('.reports/check/baseline/summary.json')); gates={'lint','format','mypy','pyright','pyrefly','security','markdown','go'}; [assert set(v['gates'].keys())==gates for v in d['projects'].values()]; print('OK: all gates present')"
    Expected: 32 projects, each with 8 gate entries
    Evidence: .reports/check/baseline/summary.json

  Scenario: Per-project raw outputs exist
    Tool: Bash
    Steps:
      1. ls .reports/check/baseline/*.txt | wc -l
    Expected: 64 files (32 check + 32 tests)
    Evidence: .reports/check/baseline/
  ```

  **Commit**: YES
  - Message: `chore: capture baseline quality gate report for all 32 projects`
  - Files: `.reports/check/baseline/*`
  - Pre-commit: `python -c "import json; json.load(open('.reports/check/baseline/summary.json'))"`

- [ ] 2. Verify flext-core src/ Still Clean

  **What to do**:
  - Run `make check PROJECT=flext-core` and capture exit code
  - If exit 0: confirm src/ is still clean, proceed
  - If non-zero: document which gates fail and error counts — this becomes a P0 blocker for Phase 2
  - Cross-reference with T1 baseline to ensure consistency
  - Save evidence to `.reports/check/baseline/flext-core-verification.txt`

  **Must NOT do**:
  - **G1**: Do NOT fix anything — verification only

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Single project, single command, binary pass/fail
  - **Skills**: [`rules-flext-core`]
    - `rules-flext-core`: Expected clean state, core conventions

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T1)
  - **Parallel Group**: Phase 0
  - **Blocks**: T9-T19 (Phase 2 depends on known core state)
  - **Blocked By**: None (starts immediately)

  **References**:
  - `flext-core/src/` — 177 source files (previously verified clean)
  - `flext-core/pyproject.toml` — Type checker configs for core
  - Previous session: flext-core src/ had 0 mypy errors

  **Acceptance Criteria**:
  - [ ] `make check PROJECT=flext-core` exit code documented
  - [ ] If non-zero: specific gates + error counts listed
  - [ ] Evidence at `.reports/check/baseline/flext-core-verification.txt`

  **QA Scenarios**:
  ```
  Scenario: flext-core gate status known
    Tool: Bash
    Steps:
      1. make check PROJECT=flext-core 2>&1 | tee .reports/check/baseline/flext-core-verification.txt; echo "EXIT:$?"
      2. grep "EXIT:" .reports/check/baseline/flext-core-verification.txt
    Expected: Exit code captured (0 = clean, non-zero = document errors)
    Evidence: .reports/check/baseline/flext-core-verification.txt
  ```

  **Commit**: NO (evidence captured in T1's commit)

### Phase 1 — CONFIG/INFRA (unblock type checking)

- [ ] 3. Fix Invalid Package Names in 6 Projects

  **What to do**:
  - Find all `pyproject.toml` files where `[project] name = "..."` contains hyphens that don't match the importable package name
  - Known affected: flext-auth, flext-db-oracle, flext-dbt-ldif, flext-dbt-oracle (verify full list from T1 baseline)
  - For each: change `name` field to use underscores matching the actual Python package (e.g., `flext-auth` → `flext_auth`)
  - Verify with `python -c "import <package_name>"` that the name matches the importable module
  - **DO NOT change directory names, only the `name` field in pyproject.toml**

  **Must NOT do**:
  - **G2**: Do NOT touch workspace-level `pyproject.toml` [tool.mypy] overrides
  - Do NOT rename directories or module folders — only the metadata `name` field

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple metadata fix in 6 pyproject.toml files
  - **Skills**: [`flext-development-workflow`]
    - `flext-development-workflow`: pyproject.toml conventions, package naming rules

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T4, T5, T6)
  - **Parallel Group**: Phase 1 (Wave 1A)
  - **Blocks**: T8 (re-baseline), T44-T49 (CONFIG-tier projects)
  - **Blocked By**: T1 (need baseline to confirm which 6 projects)

  **References**:
  - Each affected project's `pyproject.toml` — `[project]` section, `name` field
  - `base.mk` — How `PROJECT` variable maps to directory names
  - T1 baseline — Confirms which projects have `source-not-found` or name mismatch errors

  **Acceptance Criteria**:
  - [ ] All 6 project `pyproject.toml` names use underscores matching importable package
  - [ ] `grep -rn 'name.*=.*flext-' */pyproject.toml` returns 0 matches (all hyphens fixed)
  - [ ] No directory renames occurred

  **QA Scenarios**:
  ```
  Scenario: Package names are valid Python identifiers
    Tool: Bash
    Steps:
      1. for p in flext-auth flext-db-oracle flext-dbt-ldif flext-dbt-oracle; do grep '^name' $p/pyproject.toml; done
      2. Assert no hyphens in name values
    Expected: All names use underscores (flext_auth, flext_db_oracle, etc.)
    Evidence: .reports/check/phase1/package-names.txt

  Scenario: Packages remain importable
    Tool: Bash
    Steps:
      1. For each fixed project: cd <project> && python -c "import <package>" 2>&1
    Expected: No ImportError
    Evidence: .reports/check/phase1/import-check.txt
  ```

  **Commit**: YES (grouped with T4-T7 into single Phase 1 commit)
  - Message: `fix: correct package names and mypy config for quality gate compliance`
  - Files: `*/pyproject.toml`

- [ ] 4. Fix mypy_path Source-Found-Twice in Workspace Config

  **What to do**:
  - Open workspace root `pyproject.toml` → `[tool.mypy]` section
  - Examine `mypy_path` value — it likely includes both `"src"` and explicit submodule paths like `"flext-core/src"`
  - Deduplicate: if `src` is already in the path AND project-specific `<name>/src` is also listed, remove the duplicate
  - Run `make check PROJECT=flext-core CHECK_GATES=mypy 2>&1 | grep -i 'source.*found.*twice'` to verify fix
  - **CRITICAL**: Only remove TRUE duplicates — some entries may be intentional cross-project references

  **Must NOT do**:
  - **G2**: Do NOT modify the 7 existing `[[tool.mypy.overrides]]` blocks
  - **G11**: Do NOT remove existing overrides — only fix the `mypy_path` dedup

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Single config file, targeted dedup of one setting
  - **Skills**: [`flext-development-workflow`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T3, T5, T6)
  - **Parallel Group**: Phase 1 (Wave 1A)
  - **Blocks**: T8 (re-baseline)
  - **Blocked By**: T1 (need baseline to confirm source-found-twice errors)

  **References**:
  - `pyproject.toml` (workspace root) — `[tool.mypy]` section, `mypy_path` setting
  - mypy docs: <https://mypy.readthedocs.io/en/stable/config_file.html#confval-mypy_path>
  - T1 baseline — Projects showing "source file found twice" warnings

  **Acceptance Criteria**:
  - [ ] `make check PROJECT=flext-core CHECK_GATES=mypy 2>&1 | grep -ci 'found twice'` = 0
  - [ ] No `mypy_path` entries are duplicated
  - [ ] All projects that previously imported cross-project types still resolve

  **QA Scenarios**:
  ```
  Scenario: No more source-found-twice warnings
    Tool: Bash
    Steps:
      1. make check PROJECT=flext-core CHECK_GATES=mypy 2>&1 | grep -i 'found twice' | wc -l
    Expected: 0 lines
    Evidence: .reports/check/phase1/mypy-dedup.txt
  ```

  **Commit**: YES (grouped with T3, T5-T7)

- [ ] 5. Unify 4 Local mypy Configs to Workspace Config

  **What to do** (NOTE: this task may be a NO-OP if local configs were already unified — T1 baseline will confirm):
  - Identify the 4 projects with local `[tool.mypy]` sections: flext-cli, flext-ldap, flext-grpc, flext-plugin
  - For each, compare local config vs workspace config — document the diff
  - If local config is STRICTER than workspace: safe to remove (workspace is the floor)
  - If local config is WEAKER than workspace: this is a problem — understand why, then fix the code to comply with workspace config
  - If local config has PROJECT-SPECIFIC settings (e.g., protobuf exclusions for flext-grpc): KEEP those, but move to workspace `[[tool.mypy.overrides]]` with `module` filter
  - Remove the local `[tool.mypy]` section once all settings are either: in workspace config OR moved to workspace overrides
  - **flext-grpc special case**: Protobuf-generated files need explicit exclusion — add `[[tool.mypy.overrides]]` for `*_pb2*` modules

  **Must NOT do**:
  - **G2**: Do NOT modify EXISTING workspace overrides — only ADD new ones if needed
  - Do NOT weaken any setting — if a local config was stricter, that's fine to lose

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Requires careful comparison of 4 configs, understanding context, and potentially adding workspace overrides
  - **Skills**: [`flext-development-workflow`, `flext-strict-typing`]
    - `flext-development-workflow`: pyproject.toml structure, workspace vs project config
    - `flext-strict-typing`: Understanding mypy strictness levels and what each flag means

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T3, T4, T6)
  - **Parallel Group**: Phase 1 (Wave 1A)
  - **Blocks**: T8 (re-baseline), T24 (flext-grpc), T34 (flext-ldap), T37 (flext-plugin), T38 (flext-cli)
  - **Blocked By**: T1 (need baseline to see current error differences)

  **References**:
  - `flext-cli/pyproject.toml` — Local `[tool.mypy]` section
  - `flext-ldap/pyproject.toml` — Local `[tool.mypy]` section
  - `flext-grpc/pyproject.toml` — Local `[tool.mypy]` + protobuf exclusion
  - `flext-plugin/pyproject.toml` — Local `[tool.mypy]` section
  - `pyproject.toml` (workspace root) — Canonical `[tool.mypy]` config

  **Acceptance Criteria**:
  - [ ] Zero local `[tool.mypy]` sections remain in any project pyproject.toml
  - [ ] `grep -rn '\[tool.mypy\]' */pyproject.toml` returns only workspace root
  - [ ] Any project-specific needs are in workspace `[[tool.mypy.overrides]]` with module filter
  - [ ] `make check CHECK_GATES=mypy` still works for all 4 projects (may still have errors, but no NEW errors from config change)

  **QA Scenarios**:
  ```
  Scenario: No local mypy configs remain
    Tool: Bash
    Steps:
      1. grep -rn '\[tool.mypy\]' flext-cli/pyproject.toml flext-ldap/pyproject.toml flext-grpc/pyproject.toml flext-plugin/pyproject.toml
    Expected: 0 matches
    Evidence: .reports/check/phase1/mypy-unification.txt

  Scenario: Config change doesn't increase errors
    Tool: Bash
    Steps:
      1. For each of the 4 projects: make check PROJECT=<name> CHECK_GATES=mypy 2>&1 | tail -3
      2. Compare error count vs T1 baseline
    Expected: Same or fewer errors than baseline
    Evidence: .reports/check/phase1/mypy-unification-delta.txt
  ```

  **Commit**: YES (grouped with T3, T4, T6-T7)

- [ ] 6. Verify .flext-deps/ Exclusion Patterns

  **What to do**:
  - Check that `.flext-deps/` directories are excluded from ALL quality gates (mypy, pyright, pyrefly, ruff, bandit)
  - Verify in workspace `pyproject.toml`: `[tool.mypy] exclude`, `[tool.ruff] exclude`, `[tool.pyright] exclude`
  - Verify in `pyrefly.toml` or relevant pyrefly config: exclude pattern
  - If ANY gate is NOT excluding `.flext-deps/`, add the exclusion
  - Run `find . -name '.flext-deps' -type d` to identify which projects have vendored deps
  - For each project with `.flext-deps/`: run `make check PROJECT=<name>` and verify no errors from vendored files

  **Must NOT do**:
  - **G6**: Do NOT modify contents of `.flext-deps/` directories
  - Do NOT remove `.flext-deps/` from any project

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Config verification and at most a few exclusion additions
  - **Skills**: [`flext-development-workflow`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T3, T4, T5)
  - **Parallel Group**: Phase 1 (Wave 1A)
  - **Blocks**: T8 (re-baseline)
  - **Blocked By**: T1 (need baseline to identify affected projects)

  **References**:
  - `pyproject.toml` (workspace root) — Exclusion patterns in each tool section
  - `base.mk` — How `src/`, `tests/`, `examples/` directories are passed to tools
  - Any `.flext-deps/` directories found via `find . -name '.flext-deps' -type d`

  **Acceptance Criteria**:
  - [ ] All quality gate configs exclude `.flext-deps/`
  - [ ] `find . -name '.flext-deps' -type d | while read d; do echo $d; done` — all identified
  - [ ] No gate reports errors from vendored files

  **QA Scenarios**:
  ```
  Scenario: .flext-deps/ excluded from all gates
    Tool: Bash
    Steps:
      1. grep -n 'flext.deps\|flext_deps' pyproject.toml
      2. Verify exclusion exists in [tool.mypy], [tool.ruff], [tool.pyright] sections
    Expected: Exclusion pattern present in all relevant tool sections
    Evidence: .reports/check/phase1/flext-deps-exclusion.txt
  ```

  **Commit**: YES (grouped with T3-T5, T7)

- [ ] 7. Run `make format` Per Project (Auto-Fix lint+format)

  **What to do**:
  - For each of 32 projects: `make format PROJECT=<name>`
  - This auto-fixes ALL ruff lint and format issues (cheapest gates to close)
  - After running: verify `make check PROJECT=<name> CHECK_GATES=lint,format` exits 0 for each
  - If any project STILL has lint/format errors after `make format`, investigate — likely a ruff config issue
  - **Run this AFTER T3-T6** so format applies to the corrected configs
  - Capture per-project diff stats: `git diff --stat <project>/` for the report

  **Must NOT do**:
  - Do NOT manually edit files for lint/format — `make format` handles it
  - **G7**: Verify `make format` didn't change test behavior (no assertion changes, no logic changes)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Automated tool execution, no judgment needed
  - **Skills**: [`flext-development-workflow`]

  **Parallelization**:
  - **Can Run In Parallel**: NO (must run after T3-T6 complete, but before T8)
  - **Parallel Group**: Phase 1 (Wave 1B — after Wave 1A)
  - **Blocks**: T8 (re-baseline)
  - **Blocked By**: T3, T4, T5, T6 (config must be correct before formatting)

  **References**:
  - `base.mk` — `format` target definition
  - `pyproject.toml` (workspace root) — `[tool.ruff]` section with rules

  **Acceptance Criteria**:
  - [ ] `make check PROJECT=<name> CHECK_GATES=lint,format` exits 0 for all 32 projects
  - [ ] `git diff --stat` shows only auto-format changes (whitespace, import sorting, etc.)

  **QA Scenarios**:
  ```
  Scenario: All lint+format gates pass
    Tool: Bash
    Steps:
      1. for p in $(ls -d */); do make check PROJECT=${p%/} CHECK_GATES=lint,format 2>&1 | tail -1; done
    Expected: All 32 show exit 0 or pass
    Evidence: .reports/check/phase1/format-results.txt

  Scenario: No behavioral changes from formatting
    Tool: Bash
    Steps:
      1. git diff --name-only | grep -v '\(__pycache__\|\.pyc\)' | head -50
      2. Spot-check 3 changed files: only whitespace/import changes
    Expected: No logic, assertion, or fixture changes
    Evidence: .reports/check/phase1/format-diff-check.txt
  ```

  **Commit**: YES (grouped with T3-T6)
  - Message: `fix: correct package names, unify mypy configs, and auto-format all projects`
  - Files: All modified `pyproject.toml` + all auto-formatted `*.py` files
  - Pre-commit: `make check CHECK_GATES=lint,format` (from workspace root)

- [ ] 8. Re-Run Baseline to Measure Config Fix Delta

  **What to do**:
  - Repeat T1's measurement process: `make check PROJECT=<name>` for all 32 projects
  - Save to `.reports/check/post-phase1/summary.json` (same format as T1)
  - Compare `.reports/check/baseline/summary.json` vs `.reports/check/post-phase1/summary.json`
  - Generate delta report: which gates improved, which stayed same, any regressions?
  - **CRITICAL**: If ANY project has MORE errors after Phase 1 than baseline, investigate immediately
  - This becomes the new baseline for Phase 2

  **Must NOT do**:
  - **G1**: Do NOT fix anything — measurement only
  - If regressions found, document but don't fix here (create P0 task)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Re-run same measurement as T1 with delta comparison
  - **Skills**: [`flext-development-workflow`, `scripts-validation`]

  **Parallelization**:
  - **Can Run In Parallel**: NO (must wait for ALL Phase 1 fixes)
  - **Parallel Group**: Phase 1 (Wave 1C — final)
  - **Blocks**: T9-T19 (Phase 2 starts from this baseline)
  - **Blocked By**: T3, T4, T5, T6, T7 (all config fixes must be complete)

  **References**:
  - `.reports/check/baseline/summary.json` — T1 baseline for comparison
  - Same measurement process as T1

  **Acceptance Criteria**:
  - [ ] `.reports/check/post-phase1/summary.json` exists with 32 entries
  - [ ] Delta report shows zero regressions (no project has MORE errors)
  - [ ] lint and format gates pass for all 32 projects (from T7)

  **QA Scenarios**:
  ```
  Scenario: No regressions from Phase 1
    Tool: Bash
    Steps:
      1. python -c "
         import json
         base = json.load(open('.reports/check/baseline/summary.json'))
         post = json.load(open('.reports/check/post-phase1/summary.json'))
         for p in base['projects']:
           for g in base['projects'][p]['gates']:
             b = base['projects'][p]['gates'][g]
             a = post['projects'][p]['gates'][g]
             if a > b: print(f'REGRESSION: {p}/{g}: {b} -> {a}')
         print('Check complete')"
    Expected: No REGRESSION lines
    Evidence: .reports/check/post-phase1/delta-report.txt
  ```

  **Commit**: YES
  - Message: `chore: capture post-phase1 quality gate baseline`
  - Files: `.reports/check/post-phase1/*`

### Phase 2 — FLEXT-CORE TYPE SYSTEM (foundation for all consumers)

- [ ] 9. Fix MetaclassConflict — FlextSettings ProtocolModelMeta vs Pydantic ModelMetaclass

  **What to do**:
  - **FIRST**: Consult Oracle agent with full context of the MetaclassConflict before making any changes
  - The issue: `FlextSettings` (or `ProtocolModelMeta`) creates a metaclass conflict when combined with Pydantic `BaseSettings` which uses `ModelMetaclass`
  - `_CombinedModelMeta` in flext-core was designed to resolve this — investigate if it's incomplete or misapplied
  - Research: Find all classes that trigger `TypeError: metaclass conflict` via `ast_grep` and `grep`
  - Determine root cause: Is the MRO (Method Resolution Order) wrong? Is `_CombinedModelMeta` missing a base? Is there a Pydantic v2 migration gap?
  - Implement fix in flext-core that resolves the conflict for ALL downstream consumers
  - **After fix**: run `make check PROJECT=flext-core CHECK_GATES=mypy,pyright,pyrefly` to verify no regressions in core
  - **After fix**: spot-check 3 consumer projects known to have MetaclassConflict errors

  **Must NOT do**:
  - **G3**: Do NOT modify `_CombinedModelMeta` or `ProtocolModelMeta` without Oracle review of proposed change
  - **G1**: Do NOT use `type: ignore` to suppress the conflict
  - **G8**: If fix requires >20 lines, get Oracle approval first
  - **G10**: After change, cascade verification happens in T19 (not ad-hoc)

  **Recommended Agent Profile**:
  - **Category**: `ultrabrain`
    - Reason: Metaclass resolution requires deep Python MRO understanding + Pydantic v2 internals
  - **Skills**: [`flext-strict-typing`, `flext-type-system`, `rules-flext-core`, `lib-pydantic-v2`]
    - `flext-strict-typing`: Prohibited patterns, isinstance narrowing rules
    - `flext-type-system`: FlextTypes namespace, protocol/model hierarchy
    - `rules-flext-core`: Core modification rules, G3 guardrail
    - `lib-pydantic-v2`: Pydantic v2 metaclass behavior, BaseSettings internals
  - **Oracle consultation**: MANDATORY before implementation

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T10)
  - **Parallel Group**: Phase 2 (Wave 2A)
  - **Blocks**: T11-T18 (all subsequent core tasks depend on metaclass fix)
  - **Blocked By**: T8 (need post-phase1 baseline)

  **References**:
  - `flext-core/src/flext_core/models.py` — `_CombinedModelMeta` class definition
  - `flext-core/src/flext_core/protocols.py` — `ProtocolModelMeta` definition
  - `flext-core/src/flext_core/settings.py` — `FlextSettings` base class (if it exists)
  - `flext-core/src/flext_core/typings.py` — Type aliases that reference settings types
  - Pydantic v2 docs: `BaseSettings` metaclass behavior — <https://docs.pydantic.dev/latest/concepts/pydantic_settings/>
  - Python MRO docs: <https://docs.python.org/3/reference/datamodel.html#determining-the-appropriate-metaclass>
  - Consumer projects with MetaclassConflict: `grep -rn 'MetaclassConflict\|metaclass conflict' */src/`

  **Acceptance Criteria**:
  - [ ] Oracle agent approved the proposed change before implementation
  - [ ] `make check PROJECT=flext-core CHECK_GATES=mypy,pyright,pyrefly` → no new errors in src/
  - [ ] `grep -rn 'MetaclassConflict' flext-core/src/` → 0 matches (conflict resolved)
  - [ ] 3 consumer spot-checks show MetaclassConflict errors eliminated

  **QA Scenarios**:
  ```
  Scenario: MetaclassConflict resolved in core
    Tool: Bash
    Steps:
      1. make check PROJECT=flext-core CHECK_GATES=mypy 2>&1 | grep -i 'metaclass' | wc -l
      2. Assert 0 metaclass-related errors
    Expected: 0 metaclass errors
    Evidence: .reports/check/phase2/metaclass-fix.txt

  Scenario: Consumer spot-check (3 projects)
    Tool: Bash
    Steps:
      1. make check PROJECT=flext-api CHECK_GATES=mypy 2>&1 | grep -ci 'metaclass'
      2. make check PROJECT=flext-meltano CHECK_GATES=mypy 2>&1 | grep -ci 'metaclass'
      3. make check PROJECT=flext-ldif CHECK_GATES=mypy 2>&1 | grep -ci 'metaclass'
    Expected: 0 metaclass errors in each
    Evidence: .reports/check/phase2/metaclass-consumer-spot.txt
  ```

  **Commit**: NO (wait for T10, commit together as core type system fix)

- [ ] 10. Fix DomainEvent valid-type — Model Variable vs Type Usage

  **What to do**:
  - **FIRST**: Consult Oracle agent with full context of the DomainEvent valid-type error
  - The issue: `m.DomainEvent` is used as a type annotation in consumer projects, but mypy reports `valid-type` error because it's a model class instance, not a type
  - Research: `grep -rn 'm\.DomainEvent\|models\.DomainEvent' */src/ */tests/` — find ALL usages
  - Determine root cause: Is `DomainEvent` defined as a class? As a TypeAlias? As a model instance?
  - Look at `flext-core/src/flext_core/models.py` for the DomainEvent definition
  - Fix options (Oracle decides):
    a. If DomainEvent should be a class: ensure it's `class DomainEvent(...)` not an instance
    b. If it's a TypeAlias: ensure proper `TypeAlias` annotation
    c. If consumer code misuses it: fix consumer code patterns (this becomes Phase 3 work)
  - After fix: verify `m.DomainEvent` is usable as a type annotation without `valid-type` error

  **Must NOT do**:
  - **G3**: Do NOT change DomainEvent's semantic meaning without Oracle review
  - **G1**: Do NOT use `type: ignore` to suppress valid-type
  - **G7**: Do NOT change what DomainEvent represents in the domain model

  **Recommended Agent Profile**:
  - **Category**: `ultrabrain`
    - Reason: Requires understanding type system semantics and domain model design intent
  - **Skills**: [`flext-strict-typing`, `flext-type-system`, `rules-flext-core`, `lib-pydantic-v2`]
    - Same skills as T9 — closely related type system work
  - **Oracle consultation**: MANDATORY before implementation

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T9)
  - **Parallel Group**: Phase 2 (Wave 2A)
  - **Blocks**: T11-T18 (subsequent core tasks), T16 (DomainEvent refs in tests)
  - **Blocked By**: T8 (need post-phase1 baseline)

  **References**:
  - `flext-core/src/flext_core/models.py` — `DomainEvent` definition (check if class or instance)
  - `flext-core/src/flext_core/typings.py` — Any type aliases referencing DomainEvent
  - Consumer usage: `grep -rn 'm\.DomainEvent\|: DomainEvent' */src/ */tests/`
  - mypy docs on `valid-type`: <https://mypy.readthedocs.io/en/stable/error_codes.html#check-that-type-is-valid-valid-type>

  **Acceptance Criteria**:
  - [ ] Oracle agent approved the proposed change
  - [ ] `m.DomainEvent` is usable as a type annotation without valid-type error
  - [ ] `make check PROJECT=flext-core CHECK_GATES=mypy` → no new errors from this change
  - [ ] Consumer spot-check: 2 projects using `m.DomainEvent` show valid-type error eliminated

  **QA Scenarios**:
  ```
  Scenario: DomainEvent valid-type resolved
    Tool: Bash
    Steps:
      1. make check PROJECT=flext-core CHECK_GATES=mypy 2>&1 | grep -i 'valid-type.*DomainEvent' | wc -l
    Expected: 0 valid-type errors for DomainEvent
    Evidence: .reports/check/phase2/domain-event-fix.txt
  ```

  **Commit**: YES (T9 + T10 together)
  - Message: `fix(flext-core): resolve MetaclassConflict and DomainEvent valid-type in type system`
  - Files: `flext-core/src/flext_core/models.py`, `flext-core/src/flext_core/protocols.py`, related
  - Pre-commit: `make check PROJECT=flext-core CHECK_GATES=mypy,pyright,pyrefly`

- [ ] 11. Fix flext-core tests/ — tomlkit Index Errors (85 errors, 3 files)

  **What to do**:
  - Target files: `test_infra_toml_io.py` (~46 errors), `test_infra_deps_modernizer.py` (~39 errors), related toml test files
  - Root cause: `tomlkit` returns `Item | None` for bracket access, but tests use the result without narrowing
  - Pattern: `doc["key"]` returns `Item | None` — needs `isinstance(val, Item)` or proper type guard
  - For each file:
    1. Find all `[index]` errors via `make check PROJECT=flext-core CHECK_GATES=mypy 2>&1 | grep 'index'`
    2. Add isinstance narrowing after each tomlkit bracket access
    3. Use `tomlkit.items.Table`, `tomlkit.items.Array`, `tomlkit.items.String` etc. for narrowing
    4. Do NOT use `cast()` — always isinstance or TypeGuard
  - Also fix `var-annotated` errors in same files (variables need explicit type annotations)

  **Must NOT do**:
  - **G1**: No `cast()`, no `Any`, no `# type: ignore`
  - **G7**: Do NOT change test assertions or expected values — only type annotations and narrowing
  - Do NOT change the tomlkit API calls — only add narrowing after them

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 85 errors across 3 files requiring systematic tomlkit type narrowing pattern
  - **Skills**: [`flext-strict-typing`, `rules-flext-core`]
    - `flext-strict-typing`: isinstance narrowing rules, prohibited patterns
    - `rules-flext-core`: Test file conventions, import rules
  - **Omitted**: `lib-pydantic-v2` (tomlkit, not Pydantic)

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T12, T13, T14)
  - **Parallel Group**: Phase 2 (Wave 2B)
  - **Blocks**: T15 (remaining errors), T18 (full check)
  - **Blocked By**: T9, T10 (MetaclassConflict/DomainEvent may affect imports)

  **References**:
  - `flext-core/tests/unit/test_infra_toml_io.py` — 46 errors, tomlkit index + var-annotated
  - `flext-core/tests/unit/test_infra_deps_modernizer.py` — 39 errors, tomlkit index
  - `flext-core/tests/unit/test_infra_deps_path_sync.py` — 19 errors (may be part of this)
  - tomlkit API: `tomlkit.items.Table`, `tomlkit.items.Item`, `tomlkit.items.Array`
  - Previous session: Some tomlkit patterns already discovered via explore agent

  **Acceptance Criteria**:
  - [ ] `make check PROJECT=flext-core CHECK_GATES=mypy 2>&1 | grep -c 'test_infra_toml_io'` = 0
  - [ ] `make check PROJECT=flext-core CHECK_GATES=mypy 2>&1 | grep -c 'test_infra_deps_modernizer'` = 0
  - [ ] Zero `cast()` or `# type: ignore` in changed files
  - [ ] `make test PROJECT=flext-core` — same or better pass count for affected test files

  **QA Scenarios**:
  ```
  Scenario: tomlkit test files have zero mypy errors
    Tool: Bash
    Steps:
      1. make check PROJECT=flext-core CHECK_GATES=mypy 2>&1 | grep -E 'test_infra_toml|test_infra_deps_mod|test_infra_deps_path' | wc -l
    Expected: 0 errors in these files
    Evidence: .reports/check/phase2/tomlkit-tests.txt

  Scenario: Tests still pass
    Tool: Bash
    Steps:
      1. cd flext-core && python -m pytest tests/unit/test_infra_toml_io.py tests/unit/test_infra_deps_modernizer.py -v 2>&1 | tail -5
    Expected: All tests pass
    Evidence: .reports/check/phase2/tomlkit-tests-run.txt
  ```

  **Commit**: NO (wait for T12-T17, commit all core tests together)

- [ ] 12. Fix flext-core tests/ — Handler/Dispatcher Protocol Errors (22 errors, 2 files)

  **What to do**:
  - Target files: `test_dispatcher_full_coverage.py` (~12 errors), `test_handlers.py` (~10 errors)
  - Root cause: Tests reference `t.HandlerType` which does NOT exist — correct alias is `t.HandlerLike`
  - Root cause: Tests use `cast(t.AcceptableMessageType, ...)` — `AcceptableMessageType` does NOT exist
  - Root cause: Handler protocol expects `validate(self, message) -> FlextResult` and `handle(self, message) -> _ContainerValue | None`
  - For each file:
    1. Replace `t.HandlerType` with `t.HandlerLike` (= `Callable[..., _ContainerValue | None]`)
    2. Remove all `cast()` calls — replace with proper typed variables or isinstance narrowing
    3. Fix handler protocol compliance: ensure test handlers implement `validate()` and `handle()` correctly
    4. Fix `AcceptableMessageType` references — use the actual message types from `m.Command`, `m.Query`, `m.Event`

  **Must NOT do**:
  - **G1**: No `cast()`, no `# type: ignore`
  - **G7**: Do NOT change test assertions — only handler signatures and type references

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Handler protocol understanding needed, 22 errors requiring semantic type fixes
  - **Skills**: [`flext-strict-typing`, `flext-type-system`, `rules-flext-core`]
    - `flext-type-system`: Handler protocol, HandlerLike alias, message types

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T11, T13, T14)
  - **Parallel Group**: Phase 2 (Wave 2B)
  - **Blocks**: T15 (remaining errors), T18 (full check)
  - **Blocked By**: T9, T10 (type system fixes may change handler types)

  **References**:
  - `flext-core/tests/unit/test_dispatcher_full_coverage.py` — 12 errors (HandlerType, cast, protocol)
  - `flext-core/tests/unit/test_handlers.py` — 10 errors (AcceptableMessageType, cast)
  - `flext-core/src/flext_core/typings.py:159` — `HandlerLike = Callable[..., _ContainerValue | None]`
  - `flext-core/src/flext_core/handlers.py` — Handler protocol (validate, handle methods)
  - `flext-core/src/flext_core/models.py` — Command, Query, Event message types
  - **CRITICAL**: `t.HandlerType` does NOT exist. `t.AcceptableMessageType` does NOT exist.

  **Acceptance Criteria**:
  - [ ] Zero `cast()` calls in both files: `grep -c 'cast(' flext-core/tests/unit/test_dispatcher*.py flext-core/tests/unit/test_handlers.py` = 0
  - [ ] Zero references to non-existent types: `grep -c 'HandlerType\|AcceptableMessageType' flext-core/tests/unit/test_*.py` = 0
  - [ ] Both test files pass mypy: `make check PROJECT=flext-core CHECK_GATES=mypy 2>&1 | grep -c 'test_dispatch\|test_handlers'` = 0

  **QA Scenarios**:
  ```
  Scenario: Handler test files clean
    Tool: Bash
    Steps:
      1. grep -c 'cast(\|HandlerType\|AcceptableMessageType' flext-core/tests/unit/test_dispatcher_full_coverage.py flext-core/tests/unit/test_handlers.py
    Expected: 0 matches in each file
    Evidence: .reports/check/phase2/handler-tests.txt
  ```

  **Commit**: NO (grouped with T11, T13-T17)

- [ ] 13. Fix flext-core tests/ — Guards Input Type Design (24 errors, 1 file)

  **What to do**:
  - Target: `test_utilities_guards_full_coverage.py` (~24 errors)
  - Root cause: Guard functions like `is_flexible_value()`, `is_type()` accept `t.GuardInputValue` (= `_ContainerValue`), but tests pass `object()` which is NOT `_ContainerValue`
  - `_ContainerValue = str | bytes | int | float | bool | None | list[Any] | dict[str, Any]`
  - Fix approach:
    1. Replace `object()` test inputs with values that ARE `_ContainerValue` (e.g., `"test"`, `42`, `None`, `[]`, `{}`)
    2. For negative test cases (testing rejection): use values of the correct input type that the guard should still reject
    3. Do NOT change the guard function signatures — change the test inputs to match the expected types
    4. Ensure test coverage is preserved: same number of positive/negative test cases

  **Must NOT do**:
  - **G7**: Do NOT change what the guards detect/reject — only change test input types to match the guard's input type
  - **G1**: No `cast()` to force `object()` into `GuardInputValue`
  - Do NOT widen `GuardInputValue` to accept `object` — the type system is correct, tests are wrong

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 24 errors in one file, requires understanding guard design intent to pick correct test values
  - **Skills**: [`flext-strict-typing`, `flext-type-system`, `rules-flext-core`]
    - `flext-type-system`: GuardInputValue definition, _ContainerValue union members

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T11, T12, T14)
  - **Parallel Group**: Phase 2 (Wave 2B)
  - **Blocks**: T15 (remaining errors), T18 (full check)
  - **Blocked By**: T9, T10 (type system may change _ContainerValue)

  **References**:
  - `flext-core/tests/unit/test_utilities_guards_full_coverage.py` — 24 errors
  - `flext-core/src/flext_core/_utilities/guards.py` — Guard function signatures
  - `flext-core/src/flext_core/typings.py:92` — `GuardInputValue = _ContainerValue`
  - `flext-core/src/flext_core/typings.py` — `_ContainerValue` union definition

  **Acceptance Criteria**:
  - [ ] `make check PROJECT=flext-core CHECK_GATES=mypy 2>&1 | grep -c 'test_utilities_guards'` = 0
  - [ ] Zero `object()` as guard input: `grep -c 'object()' flext-core/tests/unit/test_utilities_guards_full_coverage.py` = 0
  - [ ] Same number of test cases: `python -m pytest flext-core/tests/unit/test_utilities_guards_full_coverage.py --co -q | tail -1`

  **QA Scenarios**:
  ```
  Scenario: Guard tests pass with correct input types
    Tool: Bash
    Steps:
      1. cd flext-core && python -m pytest tests/unit/test_utilities_guards_full_coverage.py -v 2>&1 | tail -10
    Expected: All tests pass, same count as before
    Evidence: .reports/check/phase2/guard-tests.txt
  ```

  **Commit**: NO (grouped with T11-T12, T14-T17)

- [ ] 14. Fix flext-core tests/ — Registry Handler Protocol (14 errors, 2 files)

  **What to do**:
  - Target: `test_registry.py` (~9 errors), `test_infra_deps_detection.py` (~5 errors, set/dict type + classify_issues arg-type)
  - Root cause in registry: Test handler classes don't match the Handler protocol (missing/wrong `validate` and `handle` signatures)
  - Root cause in deps detection: `classify_issues()` gets wrong argument types, set/dict literals need explicit types
  - For registry:
    1. Fix test handler classes to implement `validate(self, message: T) -> FlextResult[T]` and `handle(self, message: T) -> _ContainerValue | None`
    2. Fix any `set()` or `dict()` that need explicit type parameters
  - For deps detection:
    1. Add explicit type annotations to set/dict literals
    2. Fix `classify_issues()` call arguments to match expected signature

  **Must NOT do**:
  - **G7**: Do NOT change assertions or test logic
  - **G1**: No `cast()`, no `# type: ignore`

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Handler protocol compliance requires understanding registry's registration flow
  - **Skills**: [`flext-strict-typing`, `flext-type-system`, `rules-flext-core`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T11, T12, T13)
  - **Parallel Group**: Phase 2 (Wave 2B)
  - **Blocks**: T15, T18
  - **Blocked By**: T9, T10

  **References**:
  - `flext-core/tests/unit/test_registry.py` — 9 errors (handler protocol mismatch)
  - `flext-core/tests/unit/test_infra_deps_detection.py` — 5 errors (set/dict type, classify_issues)
  - `flext-core/src/flext_core/registry.py` — Handler registration API
  - `flext-core/src/flext_core/handlers.py` — Handler protocol definition
  - `flext-core/src/flext_infra/deps/detection.py` — `classify_issues()` signature

  **Acceptance Criteria**:
  - [ ] `make check PROJECT=flext-core CHECK_GATES=mypy 2>&1 | grep -c 'test_registry\|test_infra_deps_detection'` = 0
  - [ ] All tests still pass: `cd flext-core && python -m pytest tests/unit/test_registry.py tests/unit/test_infra_deps_detection.py -v`

  **QA Scenarios**:
  ```
  Scenario: Registry and deps detection tests clean
    Tool: Bash
    Steps:
      1. make check PROJECT=flext-core CHECK_GATES=mypy 2>&1 | grep -E 'test_registry|test_infra_deps_det' | wc -l
    Expected: 0 errors
    Evidence: .reports/check/phase2/registry-deps-tests.txt
  ```

  **Commit**: NO (grouped with T11-T13, T15-T17)

- [ ] 15. Fix flext-core tests/ — Remaining var-annotated/union-attr/name-defined (60+ errors, 30+ files)

  **What to do**:
  - After T11-T14 fix the biggest clusters, handle ALL remaining mypy errors across tests/
  - Categories of remaining errors:
    1. `var-annotated`: Variables need explicit type annotations — add them
    2. `union-attr`: Attribute access on union types — add isinstance narrowing
    3. `name-defined`: Undefined names — add missing imports or fix references
    4. `arg-type`: Argument type mismatches — fix to match function signatures
    5. `return-value`: Wrong return types — fix return type annotations
  - Process:
    1. Run `make check PROJECT=flext-core CHECK_GATES=mypy 2>&1 | grep 'tests/' | sort -t: -k1,1 -k2,2n` to get sorted error list
    2. Fix file by file, cheapest first
    3. Re-check after every 5 files to ensure no cascade
  - **This is the catch-all task** — everything not covered by T11-T14 and T16

  **Must NOT do**:
  - **G1**: No `cast()`, `Any`, `# type: ignore`
  - **G7**: No test behavior changes
  - **G8**: If any single file needs >20 lines of changes, review approach

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 60+ errors across 30+ files, needs systematic sweep
  - **Skills**: [`flext-strict-typing`, `flext-type-system`, `rules-flext-core`]

  **Parallelization**:
  - **Can Run In Parallel**: NO (must wait for T11-T14 to avoid overlap)
  - **Parallel Group**: Phase 2 (Wave 2C)
  - **Blocks**: T18 (full check)
  - **Blocked By**: T11, T12, T13, T14 (biggest clusters must be fixed first)

  **References**:
  - All files in `flext-core/tests/unit/` with remaining mypy errors (determine from T11-T14 delta)
  - `flext-core/src/flext_core/typings.py` — All type definitions for correct annotations
  - `flext-core/src/flext_core/result.py` — FlextResult API (fold, map, flat_map signatures)
  - Previous session fixes: `test_result_exception_carrying.py`, `test_infra_codegen_lazy_init.py`, `test_infra_subprocess.py` — patterns to follow

  **Acceptance Criteria**:
  - [ ] `make check PROJECT=flext-core CHECK_GATES=mypy 2>&1 | grep 'tests/' | wc -l` = 0 (zero test errors)
  - [ ] Zero new suppressions: `grep -rn 'cast(\|# type: ignore\|: Any' flext-core/tests/ | wc -l` = same as baseline

  **QA Scenarios**:
  ```
  Scenario: All test files clean of mypy errors
    Tool: Bash
    Steps:
      1. make check PROJECT=flext-core CHECK_GATES=mypy 2>&1 | grep -c 'tests/'
    Expected: 0
    Evidence: .reports/check/phase2/all-tests-clean.txt
  ```

  **Commit**: NO (grouped with T11-T14, T16-T17)

- [ ] 16. Fix flext-core tests/ — DomainEvent/MetaclassConflict Refs After T9-T10 (9+ errors)

  **What to do**:
  - After T9 and T10 fix the type system, some test files referencing `DomainEvent` or triggering MetaclassConflict will need updates
  - Scan: `grep -rn 'DomainEvent\|MetaclassConflict\|ProtocolModelMeta' flext-core/tests/`
  - Update test imports and usages to match the new fixed type definitions from T9-T10
  - This may involve:
    1. Changing `m.DomainEvent` usage patterns if T10 changed the definition
    2. Updating settings test classes if T9 changed the metaclass hierarchy
    3. Fixing imports if types were moved or renamed

  **Must NOT do**:
  - **G7**: Do NOT change test assertions
  - Must follow whatever T9-T10 established (read their commit to understand changes)

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Must understand T9-T10 changes and propagate correctly to tests
  - **Skills**: [`flext-strict-typing`, `flext-type-system`, `rules-flext-core`]

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on T9-T10 outputs)
  - **Parallel Group**: Phase 2 (Wave 2C, with T15)
  - **Blocks**: T18 (full check)
  - **Blocked By**: T9, T10 (must know what changed), T15 (coordinate to avoid conflicts)

  **References**:
  - T9 and T10 commit diffs (read after they complete)
  - `flext-core/tests/` — files referencing DomainEvent or MetaclassConflict patterns

  **Acceptance Criteria**:
  - [ ] Zero test errors related to DomainEvent or MetaclassConflict
  - [ ] All affected tests still pass

  **QA Scenarios**:
  ```
  Scenario: DomainEvent/Metaclass test refs clean
    Tool: Bash
    Steps:
      1. make check PROJECT=flext-core CHECK_GATES=mypy 2>&1 | grep -i 'domain.event\|metaclass' | wc -l
    Expected: 0
    Evidence: .reports/check/phase2/domain-metaclass-test-refs.txt
  ```

  **Commit**: NO (grouped with T11-T15, T17)

- [ ] 17. Fix flext-core examples/ — All Quality Gates

  **What to do**:
  - Run `make check PROJECT=flext-core` and filter errors from `examples/` directory
  - Fix all mypy, pyright, pyrefly errors in example files
  - Apply same rules: isinstance narrowing, proper type annotations, no cast/Any
  - Examples should demonstrate correct type usage — they're documentation-as-code
  - Run `make format PROJECT=flext-core` first to auto-fix lint/format in examples/

  **Must NOT do**:
  - **G1**: Same prohibitions as src/ and tests/
  - Do NOT change example functionality — only type annotations

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Examples are typically small files with few errors
  - **Skills**: [`rules-flext-core`, `flext-strict-typing`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T15, T16)
  - **Parallel Group**: Phase 2 (Wave 2C)
  - **Blocks**: T18 (full check)
  - **Blocked By**: T9, T10 (type system must be stable)

  **References**:
  - `flext-core/examples/` — All example files
  - `flext-core/src/flext_core/` — Correct usage patterns to follow

  **Acceptance Criteria**:
  - [ ] `make check PROJECT=flext-core CHECK_GATES=mypy 2>&1 | grep 'examples/' | wc -l` = 0
  - [ ] Example files run without errors: `cd flext-core && python examples/*.py` (if executable)

  **QA Scenarios**:
  ```
  Scenario: Examples clean
    Tool: Bash
    Steps:
      1. make check PROJECT=flext-core CHECK_GATES=mypy,pyright,pyrefly 2>&1 | grep 'examples/' | wc -l
    Expected: 0 errors in examples/
    Evidence: .reports/check/phase2/core-examples.txt
  ```

  **Commit**: YES (all of T11-T17 together)
  - Message: `fix(flext-core): zero all mypy/pyright/pyrefly errors in tests/ and examples/`
  - Files: `flext-core/tests/**/*.py`, `flext-core/examples/**/*.py`
  - Pre-commit: `make check PROJECT=flext-core CHECK_GATES=mypy,pyright,pyrefly`

- [ ] 18. Full Quality Gate Check — `make check PROJECT=flext-core` = exit 0

  **What to do**:
  - Run `make check PROJECT=flext-core` and verify ALL 8 gates pass (exit 0)
  - If any gate fails: identify which gate, fix remaining issues
  - This is the GATE task — flext-core must be 100% clean before consumers start
  - Run `make test PROJECT=flext-core` and compare pass count vs T1 baseline
  - Capture evidence to `.reports/check/phase2/flext-core-final.txt`

  **Must NOT do**:
  - Do NOT skip any gate — all 8 must pass
  - **G9**: `make check` is the ONLY acceptance oracle

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Verification task, should be clean after T9-T17
  - **Skills**: [`rules-flext-core`]

  **Parallelization**:
  - **Can Run In Parallel**: NO (must verify all Phase 2 work)
  - **Parallel Group**: Phase 2 (Wave 2D — gate)
  - **Blocks**: T19 (cascade verification)
  - **Blocked By**: T11-T17 (all core fixes must be complete)

  **References**:
  - All T11-T17 evidence files
  - T8 post-phase1 baseline for comparison

  **Acceptance Criteria**:
  - [ ] `make check PROJECT=flext-core` → exit 0
  - [ ] `make test PROJECT=flext-core` → same or better pass count vs baseline
  - [ ] Evidence at `.reports/check/phase2/flext-core-final.txt`

  **QA Scenarios**:
  ```
  Scenario: flext-core fully clean
    Tool: Bash
    Steps:
      1. make check PROJECT=flext-core 2>&1 | tee .reports/check/phase2/flext-core-final.txt; echo "EXIT:$?"
      2. make test PROJECT=flext-core 2>&1 | tail -5
    Expected: Both exit 0
    Evidence: .reports/check/phase2/flext-core-final.txt
  ```

  **Commit**: NO (T17 commit already covers the code; this is verification)

- [ ] 19. Cascade Verification — ALL 32 Projects After Core Changes

  **What to do**:
  - **CRITICAL (G10)**: After flext-core type system changes, verify ALL 32 projects
  - Run `make check PROJECT=<name> CHECK_GATES=mypy,pyright,pyrefly` for every project
  - Compare vs T8 post-phase1 baseline:
    - If a project has FEWER errors: core changes helped → good
    - If SAME: neutral → expected
    - If MORE errors: core changes caused regression → STOP, investigate, fix in core
  - Save results to `.reports/check/post-phase2/summary.json`
  - This becomes the new baseline for Phase 3
  - **If regressions found**: create P0 tasks to fix in flext-core before proceeding to Phase 3

  **Must NOT do**:
  - Do NOT proceed to Phase 3 if ANY project has MORE errors than post-phase1 baseline
  - Do NOT fix consumer projects here — only verify and document

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 32 projects to check with delta comparison
  - **Skills**: [`flext-development-workflow`, `scripts-validation`]

  **Parallelization**:
  - **Can Run In Parallel**: NO (gate task)
  - **Parallel Group**: Phase 2 (Wave 2E — final)
  - **Blocks**: T20-T49 (all Phase 3 tasks), T50 (Go gate)
  - **Blocked By**: T18 (flext-core must be clean first)

  **References**:
  - `.reports/check/post-phase1/summary.json` — Baseline for comparison
  - T9-T10 commit diffs — What changed in core

  **Acceptance Criteria**:
  - [ ] `.reports/check/post-phase2/summary.json` exists with 32 entries
  - [ ] Zero regressions: no project has more errors than post-phase1 baseline
  - [ ] Delta report generated

  **QA Scenarios**:
  ```
  Scenario: No regressions from core changes
    Tool: Bash
    Steps:
      1. python -c "
         import json
         base = json.load(open('.reports/check/post-phase1/summary.json'))
         post = json.load(open('.reports/check/post-phase2/summary.json'))
         regressions = []
         for p in base['projects']:
           for g in ['mypy','pyright','pyrefly']:
             b = base['projects'][p]['gates'][g]
             a = post['projects'][p]['gates'][g]
             if a > b: regressions.append(f'{p}/{g}: {b} -> {a}')
         if regressions: print('REGRESSIONS:', regressions); exit(1)
         print(f'OK: 0 regressions across {len(base["projects"])} projects')"
    Expected: 0 regressions
    Evidence: .reports/check/post-phase2/cascade-check.txt
  ```

  **Commit**: YES
  - Message: `chore: capture post-phase2 cascade verification (flext-core type system complete)`
  - Files: `.reports/check/post-phase2/*`

### Phase 3 — CONSUMER PROJECTS (by tier, max parallel)

> **CONSUMER TASK TEMPLATE** — ALL tasks T20-T49 follow this pattern unless overridden:
>
> **Common What to do**:
> 1. `make format PROJECT=<name>` (auto-fix lint/format)
> 2. `make check PROJECT=<name> CHECK_GATES=mypy` → fix errors in src/, tests/, examples/
> 3. `make check PROJECT=<name> CHECK_GATES=pyright` → fix remaining type errors
> 4. `make check PROJECT=<name> CHECK_GATES=pyrefly` → fix remaining type errors
> 5. `make check PROJECT=<name> CHECK_GATES=security` → fix bandit issues in src/ (if any)
> 6. `make check PROJECT=<name>` → verify ALL 8 gates pass (exit 0)
> 7. `make test PROJECT=<name>` → verify tests pass (same or better vs baseline)
>
> **Common Fix Patterns** (for mypy/pyright/pyrefly errors):
> - MetaclassConflict: Should be resolved by T9 — if still present, update Settings class to use fixed base
> - DomainEvent valid-type: Should be resolved by T10 — if still present, update usage pattern
> - `arg-type`: Fix argument to match function signature using correct flext-core types
> - `return-value`: Fix return type annotation to match actual return
> - `attr-defined`: Use isinstance narrowing before attribute access
> - `import-untyped`: Add type stubs or use typed alternatives
> - `override`: Add `@override` decorator or fix method signature to match parent
>
> **Common Must NOT do**: G1 (no cast/Any/ignore), G4 (no [MANAGED] pyrefly config changes), G5 (no custom type stubs in typings/ without Oracle), G7 (no test behavior changes), G9 (make check is oracle), G12 (pyrefly tests/ only suppresses `bad-argument-type` — all other pyrefly errors are ACTIVE in tests/)
>
> **Common Acceptance Criteria**:
> - [ ] `make check PROJECT=<name>` → exit 0
> - [ ] `make test PROJECT=<name>` → same or better pass count vs T19 baseline
> - [ ] `grep -rn 'cast(\|# type: ignore\|: Any' <name>/src/ <name>/tests/` → no NEW matches vs baseline
>
> **Common QA Scenario**:
> ```
> Scenario: Project fully clean
>   Tool: Bash
>   Steps:
>     1. make check PROJECT=<name> 2>&1 | tee .reports/check/phase3/<name>.txt; echo "EXIT:$?"
>     2. make test PROJECT=<name> 2>&1 | tail -5
>   Expected: Both exit 0
>   Evidence: .reports/check/phase3/<name>.txt
> ```
>
> **Common Commit**: YES (one per project)
> - Message: `fix(<name>): zero all quality gates — root-cause type fixes`
> - Files: `<name>/src/**/*.py`, `<name>/tests/**/*.py`, `<name>/examples/**/*.py`
> - Pre-commit: `make check PROJECT=<name> && make test PROJECT=<name>`

#### Wave 3A — LOW errors (1-9 mypy, likely few other gates)

- [ ] 20. flext-quality (1 mypy)

  **Category**: `quick` | **Skills**: [`flext-strict-typing`]
  **Blocked By**: T19 | **Blocks**: T51
  **Known issues**: 1 mypy error — likely a single arg-type or missing annotation
  **Special notes**: 29/30 projects have examples/ but flext-quality does NOT — skip examples/ check

- [ ] 21. flext-oracle-oic (1 mypy)

  **Category**: `quick` | **Skills**: [`flext-strict-typing`]
  **Blocked By**: T19 | **Blocks**: T51
  **Known issues**: 1 mypy error — likely Oracle Integration Cloud client type

- [ ] 22. flext-target-oracle-oic (1 mypy)

  **Category**: `quick` | **Skills**: [`flext-strict-typing`]
  **Blocked By**: T19 | **Blocks**: T51
  **Known issues**: 1 mypy error — likely Singer target protocol type

- [ ] 23. flext-tap-oracle (2 mypy)

  **Category**: `quick` | **Skills**: [`flext-strict-typing`]
  **Blocked By**: T19 | **Blocks**: T51
  **Known issues**: 2 mypy errors — likely Singer tap protocol types

- [ ] 24. flext-grpc (2 mypy + protobuf exclusion)

  **Category**: `quick` | **Skills**: [`flext-strict-typing`]
  **Blocked By**: T5 (local mypy config unification), T19 | **Blocks**: T51
  **Known issues**: 2 mypy errors + protobuf-generated `*_pb2*.py` files may cause noise
  **Special notes**: After T5 unifies local config, protobuf exclusion should be in workspace overrides. Verify `*_pb2*` files are excluded from all type checkers.

- [ ] 25. flext-target-oracle-wms (3 mypy)

  **Category**: `quick` | **Skills**: [`flext-strict-typing`]
  **Blocked By**: T19 | **Blocks**: T51
  **Known issues**: 3 mypy errors — likely Singer target + WMS types

- [ ] 26. flext-web (4 mypy)

  **Category**: `quick` | **Skills**: [`flext-strict-typing`]
  **Blocked By**: T19 | **Blocks**: T51
  **Known issues**: 4 mypy errors — likely web framework type annotations

- [ ] 27. flext-tap-oracle-wms (4 mypy)

  **Category**: `quick` | **Skills**: [`flext-strict-typing`]
  **Blocked By**: T19 | **Blocks**: T51
  **Known issues**: 4 mypy errors — likely Singer tap + WMS types

#### Wave 3B — MEDIUM errors (6-43 mypy)

- [ ] 28. flext-target-ldif (6 mypy)

  **Category**: `unspecified-high` | **Skills**: [`flext-strict-typing`]
  **Blocked By**: T19 | **Blocks**: T51
  **Known issues**: 6 mypy errors — likely LDIF target write/output types

- [ ] 29. flext-dbt-oracle-wms (7 mypy)

  **Category**: `unspecified-high` | **Skills**: [`flext-strict-typing`]
  **Blocked By**: T19 | **Blocks**: T51
  **Known issues**: 7 mypy errors — dbt model/source type annotations

- [ ] 30. flext-dbt-ldap (9 mypy)

  **Category**: `unspecified-high` | **Skills**: [`flext-strict-typing`]
  **Blocked By**: T19 | **Blocks**: T51
  **Known issues**: 9 mypy errors — dbt model/source type annotations

- [ ] 31. flext-tap-ldif (13 mypy)

  **Category**: `unspecified-high` | **Skills**: [`flext-strict-typing`]
  **Blocked By**: T19 | **Blocks**: T51
  **Known issues**: 13 mypy errors — LDIF parsing + Singer tap protocol types

- [ ] 32. flext-oracle-wms (29 mypy)

  **Category**: `unspecified-high` | **Skills**: [`flext-strict-typing`]
  **Blocked By**: T19 | **Blocks**: T51
  **Known issues**: 29 mypy errors — Oracle WMS client type annotations, likely arg-type and return-value clusters

- [ ] 33. flext-target-oracle (41 mypy)

  **Category**: `unspecified-high` | **Skills**: [`flext-strict-typing`]
  **Blocked By**: T19 | **Blocks**: T51
  **Known issues**: 41 mypy errors — Singer target protocol + Oracle write operations
  **Special notes**: May share patterns with flext-target-ldap (T39). Fix one first, apply pattern to other.

- [ ] 34. flext-ldap (42 mypy)

  **Category**: `deep` | **Skills**: [`flext-strict-typing`, `flext-type-system`]
  **Blocked By**: T5 (local mypy config unification), T19 | **Blocks**: T51
  **Known issues**: 42 mypy errors — LDAP connection/search/modify operation types
  **Special notes**: Has local `[tool.mypy]` override that T5 will unify. After T5, error count may change.

- [ ] 35. flext-tap-ldap (43 mypy)

  **Category**: `deep` | **Skills**: [`flext-strict-typing`, `flext-type-system`]
  **Blocked By**: T19 | **Blocks**: T51
  **Known issues**: 43 mypy errors — LDAP connection types + Singer tap protocol
  **Special notes**: Shares LDAP patterns with flext-ldap (T34). Coordinate fixes.

#### Wave 3C — HIGH errors (47-99 mypy)

- [ ] 36. flext-tap-oracle-oic (47 mypy)

  **Category**: `deep` | **Skills**: [`flext-strict-typing`, `flext-type-system`]
  **Blocked By**: T19 | **Blocks**: T51
  **Known issues**: 47 mypy errors — Oracle OIC API client types, likely complex response type hierarchies

- [ ] 37. flext-plugin (49 mypy)

  **Category**: `deep` | **Skills**: [`flext-strict-typing`, `flext-type-system`]
  **Blocked By**: T5 (local mypy config unification), T19 | **Blocks**: T51
  **Known issues**: 49 mypy errors — Plugin system type annotations, likely protocol compliance and registry types
  **Special notes**: Has local `[tool.mypy]` override that T5 will unify. Plugin system may need flext-core protocol types.

- [ ] 38. flext-cli (81 mypy + local config)

  **Category**: `deep` | **Skills**: [`flext-strict-typing`, `flext-type-system`]
  **Blocked By**: T5 (local mypy config unification), T19 | **Blocks**: T51
  **Known issues**: 81 mypy errors — CLI framework types, command registration, argument parsing
  **Special notes**: Has local `[tool.mypy]` override. After T5 unification, error count may change significantly. This project is a framework (like Click/Typer) — expect complex callable/generic types.

- [ ] 39. flext-target-ldap (99 mypy)

  **Category**: `deep` | **Skills**: [`flext-strict-typing`, `flext-type-system`]
  **Blocked By**: T19 | **Blocks**: T51
  **Known issues**: 99 mypy errors — LDAP target write operations, Singer target protocol
  **Special notes**: Shares LDAP patterns with T34 (flext-ldap) and T35 (flext-tap-ldap). Fix those first, apply patterns here.

#### Wave 3D — CRITICAL errors (100+ mypy)

- [ ] 40. flext-meltano (117 mypy)

  **Category**: `deep` | **Skills**: [`flext-strict-typing`, `flext-type-system`]
  **Blocked By**: T19 | **Blocks**: T51
  **Known issues**: 117 mypy errors — Meltano orchestration types, Singer protocol integration
  **Special notes**: Meltano SDK has its own type system. May need `librarian` agent to research Meltano SDK types. Expect complex plugin/executor/job types.

- [ ] 41. flext-observability (149 mypy)

  **Category**: `deep` | **Skills**: [`flext-strict-typing`, `flext-type-system`]
  **Blocked By**: T19 | **Blocks**: T51
  **Known issues**: 149 mypy errors — OpenTelemetry/metrics/tracing types
  **Special notes**: OpenTelemetry SDK has complex generic types. May need `librarian` agent to research OTel SDK type patterns. Expect Span, Meter, TracerProvider generics.

- [ ] 42. flext-ldif (244 mypy)

  **Category**: `deep` | **Skills**: [`flext-strict-typing`, `flext-type-system`]
  **Blocked By**: T19 | **Blocks**: T51
  **Known issues**: 244 mypy errors — LDIF parsing, validation, transformation types
  **Special notes**: Highest non-API error count. Likely needs systematic approach: categorize errors first, then fix by category. May have MetaclassConflict (check after T9).

- [ ] 43. flext-api (410 mypy)

  **Category**: `deep` | **Skills**: [`flext-strict-typing`, `flext-type-system`, `backend-api-patterns`]
  **Blocked By**: T19 | **Blocks**: T51
  **Known issues**: 410 mypy errors — Highest error count in workspace
  **Special notes**: This is the largest project. Must be split internally by the executing agent:
    1. First pass: categorize all 410 errors (arg-type, return-value, attr-defined, etc.)
    2. Fix by category, cheapest first
    3. May need multiple sessions. Agent should checkpoint progress.
    `backend-api-patterns` skill: HTTP framework patterns, request/response types, middleware typing.

#### Wave 3E — CONFIG-ISSUE projects (invalid package names, post-T3 fix)

- [ ] 44. flext-auth

  **Category**: `unspecified-high` | **Skills**: [`flext-strict-typing`]
  **Blocked By**: T3 (package name fix), T19 | **Blocks**: T51
  **Known issues**: Package name was invalid (hyphen). After T3 fix, measure actual error count from T19 baseline.
  **Special notes**: Auth patterns — expect JWT/session/middleware types.

- [ ] 45. flext-db-oracle

  **Category**: `unspecified-high` | **Skills**: [`flext-strict-typing`]
  **Blocked By**: T3 (package name fix), T19 | **Blocks**: T51
  **Known issues**: Package name was invalid. After T3 fix, measure actual error count.
  **Special notes**: Database access patterns — expect connection/cursor/result types.

- [ ] 46. flext-dbt-ldif

  **Category**: `unspecified-high` | **Skills**: [`flext-strict-typing`]
  **Blocked By**: T3 (package name fix), T19 | **Blocks**: T51
  **Known issues**: Package name was invalid. After T3 fix, measure actual error count.
  **Special notes**: dbt project — may have minimal Python code.

- [ ] 47. flext-dbt-oracle

  **Category**: `unspecified-high` | **Skills**: [`flext-strict-typing`]
  **Blocked By**: T3 (package name fix), T19 | **Blocks**: T51
  **Known issues**: Package name was invalid. After T3 fix, measure actual error count.
  **Special notes**: dbt project — may have minimal Python code.

- [ ] 48. algar-oud-mig

  **Category**: `unspecified-high` | **Skills**: [`flext-strict-typing`]
  **Blocked By**: T19 | **Blocks**: T51
  **Known issues**: External project (not a submodule). Measure error count from T1 baseline.
  **Special notes**: **G14**: Commit directly, not as submodule update. LDAP migration tool — expect LDIF/LDAP types.

- [ ] 49. gruponos-meltano-native

  **Category**: `unspecified-high` | **Skills**: [`flext-strict-typing`]
  **Blocked By**: T19 | **Blocks**: T51
  **Known issues**: External project (not a submodule). Measure error count from T1 baseline.
  **Special notes**: **G14**: Commit directly, not as submodule update. Meltano pipeline — expect Singer/Meltano types.

### Phase 4 — GO GATE + FINAL VERIFICATION

- [ ] 50. Fix Go Gate for flexcore Project

  **What to do**:
  - The `go` gate only applies to the `flexcore` project (CORE_STACK=go in its Makefile)
  - Run `make check PROJECT=flexcore CHECK_GATES=go` to see current state
  - If errors: fix Go source files in `flexcore/` (likely `go vet`, `golint`, `go build` issues)
  - If already passing: document as pass and move on
  - **NOTE**: This is the Go runtime component, separate from flext-core (Python)

  **Must NOT do**:
  - Do NOT change Go module dependencies without understanding impact
  - Do NOT modify Go code behavior — only fix linting/type/build issues

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Single project, single gate, likely few issues
  - **Skills**: [`flext-development-workflow`]
  - **Omitted**: Python-specific skills (this is Go code)

  **Parallelization**:
  - **Can Run In Parallel**: YES (independent of Phase 3)
  - **Parallel Group**: Phase 4 (can start after T1 provides baseline)
  - **Blocks**: T51 (final verification)
  - **Blocked By**: T1 (need baseline), T19 (if Go code imports generated Python bindings)

  **References**:
  - `flexcore/` — Go source directory
  - `flexcore/Makefile` — `CORE_STACK=go` flag, go-specific targets
  - `base.mk` — `check-go` target definition

  **Acceptance Criteria**:
  - [ ] `make check PROJECT=flexcore CHECK_GATES=go` → exit 0
  - [ ] `make check PROJECT=flexcore` → exit 0 (all gates including go)

  **QA Scenarios**:
  ```
  Scenario: Go gate passes
    Tool: Bash
    Steps:
      1. make check PROJECT=flexcore CHECK_GATES=go 2>&1 | tee .reports/check/phase4/flexcore-go.txt; echo "EXIT:$?"
    Expected: Exit 0
    Evidence: .reports/check/phase4/flexcore-go.txt
  ```

  **Commit**: YES
  - Message: `fix(flexcore): zero Go quality gate errors`
  - Files: `flexcore/**/*.go`
  - Pre-commit: `make check PROJECT=flexcore`

- [ ] 51. Final Workspace-Wide Verification

  **What to do**:
  - Run `make check` from workspace root (no PROJECT filter) — must exit 0
  - Run `make validate VALIDATE_SCOPE=workspace` — must exit 0
  - Run `make test` for every project and compare vs T1 baseline
  - Verify all submodules are clean: `git submodule foreach 'git status --porcelain'` → empty
  - Verify no new suppressions: `git diff $(cat .reports/check/baseline/root-sha.txt) -- '*.py' | grep -cE '# type: ignore|cast\(|: Any\b|# noqa'` → 0
  - Generate final report: `.reports/check/final/summary.json` (same format as baseline)
  - Compare `.reports/check/baseline/summary.json` vs `.reports/check/final/summary.json`:
    - ALL projects must show 0 errors for ALL gates
    - ALL projects must show same or better test pass counts
  - If ANY project fails: create P0 fix task, do NOT proceed to Final Wave

  **Must NOT do**:
  - Do NOT proceed to Final Wave if ANY check fails
  - **G9**: `make check` from workspace root is the FINAL acceptance oracle

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Full workspace sweep, 32 projects, delta comparison, final gate
  - **Skills**: [`flext-development-workflow`, `scripts-validation`]

  **Parallelization**:
  - **Can Run In Parallel**: NO (must verify ALL previous work)
  - **Parallel Group**: Phase 4 (final gate)
  - **Blocks**: F1-F4 (Final Verification Wave)
  - **Blocked By**: T20-T50 (ALL implementation tasks must be complete)

  **References**:
  - `.reports/check/baseline/summary.json` — Original baseline from T1
  - `.reports/check/post-phase1/summary.json` — Post-config baseline
  - `.reports/check/post-phase2/summary.json` — Post-core baseline
  - All `.reports/check/phase3/<name>.txt` — Per-project evidence

  **Acceptance Criteria**:
  - [ ] `make check` (workspace root) → exit 0
  - [ ] `make validate VALIDATE_SCOPE=workspace` → exit 0
  - [ ] `git submodule foreach 'git status --porcelain'` → empty (all clean)
  - [ ] `.reports/check/final/summary.json` shows 0 errors for all 32 projects, all 8 gates
  - [ ] Test pass counts: all same or better vs baseline
  - [ ] No new suppressions across entire diff

  **QA Scenarios**:
  ```
  Scenario: Workspace fully clean
    Tool: Bash
    Steps:
      1. make check 2>&1 | tee .reports/check/final/workspace-check.txt; echo "EXIT:$?"
      2. make validate VALIDATE_SCOPE=workspace 2>&1 | tail -10
      3. git submodule foreach 'git status --porcelain' 2>&1 | grep -v '^Entering' | wc -l
    Expected: All exit 0, submodule status empty (0 dirty lines)
    Evidence: .reports/check/final/workspace-check.txt

  Scenario: Zero new suppressions
    Tool: Bash
    Steps:
      1. git diff $(cat .reports/check/baseline/root-sha.txt) -- '*.py' | grep -cE '# type: ignore|cast\(|: Any\b|# noqa'
    Expected: 0
    Evidence: .reports/check/final/suppression-check.txt

  Scenario: Final report complete
    Tool: Bash
    Steps:
      1. python -c "import json; d=json.load(open('.reports/check/final/summary.json')); assert all(sum(v['gates'].values())==0 for v in d['projects'].values()), 'Not all zero'; print('ALL ZERO')"
    Expected: ALL ZERO
    Evidence: .reports/check/final/summary.json
  ```

  **Commit**: YES
  - Message: `chore: capture final quality gate report — all 32 projects at zero`
  - Files: `.reports/check/final/*`
  - Pre-commit: `make check && make validate VALIDATE_SCOPE=workspace`

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Rejection → fix → re-run.

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (`make check PROJECT=<name>` exit 0). For each "Must NOT Have": search codebase for forbidden patterns (`grep -rn 'cast(\|# type: ignore\|: Any\b' <project>/src/ <project>/tests/`) — reject with file:line if found. Check evidence files in `.reports/check/`. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run `make check` per project. Review all changed files for: `cast()`, `Any`, `# type: ignore`, empty catches, console.log in prod, commented-out code, unused imports. Check AI slop: excessive comments, over-abstraction, generic names (data/result/item/temp). Verify no config weakening (diff pyproject.toml against baseline).
  Output: `Build [PASS/FAIL] | Lint [PASS/FAIL] | Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [ ] F3. **Real QA — Clean State Verification** — `unspecified-high`
  Start from clean state (`make clean` per project). Run `make check` for ALL 32 projects. Run `make test` for ALL 32 projects. Compare test pass counts vs baseline. Verify no regressions. Save evidence to `.reports/check/final/`.
  Output: `Projects [32/32 pass] | Tests [N pass vs baseline] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  For each project: read git diff vs baseline. Verify only type annotations, return types, imports, and isinstance narrowing changed. Flag any behavioral changes (new assertions, changed logic, modified test fixtures). Check "Must NOT do" compliance. Detect scope creep: new files, new dependencies, new config options.
  Output: `Projects [N/N compliant] | Behavioral Changes [CLEAN/N issues] | Scope Creep [CLEAN/N files] | VERDICT`

---

## Commit Strategy

### Per-Project Commit Pattern
```bash
# In submodule:
cd <project>
make format    # Auto-fix lint+format first
# ... type fixes ...
make check     # Verify all 8 gates pass
make test      # Verify tests still pass
git add -A && git commit -m "fix(<project>): zero all quality gates — root-cause type fixes"

# In workspace root:
cd ..
git add <project>
git commit -m "chore: update <project> submodule ref (zero quality gates)"
```

### External Projects (algar-oud-mig, gruponos-meltano-native)
```bash
cd <project>
make format && make check && make test
git add -A && git commit -m "fix(<project>): zero all quality gates"
git push
```

---

## Success Criteria

### Verification Commands
```bash
# Final acceptance (from workspace root):
make check                                    # Expected: exit 0
make validate VALIDATE_SCOPE=workspace        # Expected: exit 0
git submodule foreach 'git status --porcelain' # Expected: empty output

# Per-project spot check:
cd flext-core && make check && make test      # Expected: both exit 0
cd flext-api && make check && make test       # Expected: both exit 0
cd flext-ldif && make check && make test      # Expected: both exit 0

# No-new-suppressions:
git log --oneline HEAD~55..HEAD -- '*.py' | wc -l  # Expected: ~55 commits
git diff $(git log --format=%H HEAD~55..HEAD | tail -1) -- '*.py' | grep -cE '# type: ignore|cast\(|: Any\b|# noqa'
# Expected: 0 (no new suppressions)
```

### Final Checklist
- [ ] All 32 projects: `make check` = exit 0
- [ ] All 32 projects: `make test` = same or better pass count
- [ ] `make validate VALIDATE_SCOPE=workspace` = exit 0
- [ ] Zero new cast(), Any, # type: ignore, # noqa
- [ ] All submodule refs updated and committed
- [ ] Baseline report at `.reports/check/baseline/`
- [ ] Final report at `.reports/check/final/`
