---
phase: 03-infrastructure-centralization
plan: 01
subsystem: infra
tags: [cli, utilities, parameter-normalization, flext-infra]

requires:
  - phase: 02-architecture-solid
    provides: MRO facade patterns and strict typing
provides:
  - "iter_projects() centralizing discover+filter+sort for project iteration"
  - "emit() centralizing JSON/text output switching"
  - "Zero bare root: Path parameters in flext-infra service interfaces"
affects: [03-02, 03-03, 03-04, 03-05]

tech-stack:
  added: []
  patterns:
    - "iter_projects(cli) wraps discover_projects + filter + sort"
    - "emit(data, cli=cli) switches JSON/text output based on cli.output_format"
    - "workspace_root/repo_root/scan_root canonical naming for Path parameters"

key-files:
  created: []
  modified:
    - "flext-infra/src/flext_infra/_utilities/cli.py"
    - "flext-infra/src/flext_infra/_utilities/git.py"
    - "flext-infra/src/flext_infra/_utilities/github.py"
    - "flext-infra/src/flext_infra/_utilities/release.py"
    - "flext-infra/src/flext_infra/refactor/census.py"
    - "flext-infra/src/flext_infra/refactor/__main__.py"
    - "flext-infra/src/flext_infra/github/__main__.py"
    - "flext-infra/src/flext_infra/validate/scanner.py"
    - "flext-infra/src/flext_infra/refactor/_utilities.py"

key-decisions:
  - "git.py root: Path renamed to repo_root (not workspace_root) since git ops are polymorphic across workspace and submodule repos"
  - "scanner.py root: Path renamed to scan_root since scanner operates on any directory"
  - "refactor/_utilities.py _is_path_within_root param renamed to base_path"

patterns-established:
  - "workspace_root for workspace-scoped operations"
  - "repo_root for generic git repository operations"
  - "scan_root for directory-scoped file scanning"

requirements-completed: [INFRA-01, INFRA-02, INFRA-03]

duration: 8min
completed: 2026-03-24
---

# Phase 03 Plan 01: CLI Utilities + Parameter Normalization Summary

**Added iter_projects() and emit() to CLI facade, normalized all bare root: Path to semantic variants (workspace_root, repo_root, scan_root) across 9 flext-infra files**

## Performance

- **Duration:** 8 min
- **Started:** 2026-03-24T13:38:03Z
- **Completed:** 2026-03-24T13:46:00Z
- **Tasks:** 3 (1 executed, 1 already-done, 1 executed)
- **Files modified:** 9

## Accomplishments

- iter_projects() centralizes the discover+filter+sort pattern previously duplicated across 13 call sites
- emit() centralizes JSON/text output switching for consistent CLI output
- Zero bare `root: Path` parameters remain in flext-infra service interfaces

## Task Commits

1. **Task 1: Add iter_projects() and emit()** - `26a2ff9b` (feat)
2. **Task 2: Migrate **main**.py to run_cli()** - SKIPPED (already done per research)
3. **Task 3: Normalize root: Path** - `16190e94` (refactor)

## Files Created/Modified

- `flext-infra/src/flext_infra/_utilities/cli.py` - Added iter_projects() and emit() static methods
- `flext-infra/src/flext_infra/_utilities/git.py` - Renamed root -> repo_root (12 methods)
- `flext-infra/src/flext_infra/_utilities/github.py` - Renamed root -> workspace_root in github_lint_workflows
- `flext-infra/src/flext_infra/_utilities/release.py` - Renamed root -> workspace_root in update_changelog
- `flext-infra/src/flext_infra/refactor/census.py` - Renamed root -> workspace_root in run()
- `flext-infra/src/flext_infra/refactor/__main__.py` - Updated census.run() call site to keyword arg
- `flext-infra/src/flext_infra/github/__main__.py` - Updated github_lint_workflows call site
- `flext-infra/src/flext_infra/validate/scanner.py` - Renamed root -> scan_root (polymorphic scanner)
- `flext-infra/src/flext_infra/refactor/_utilities.py` - Renamed root -> base_path in private helper

## Decisions Made

- git.py methods use `repo_root` (not `workspace_root`) because they operate on both workspace and submodule repos
- scanner.py uses `scan_root` because it scans arbitrary directories (workspace or project)
- Task 2 skipped entirely — research confirmed run_cli migration and D-07 bug fix were already completed in prior sisyphus work

## Deviations from Plan

### Task 2 Already Complete

- **Found during:** Task 2 pre-read
- **Issue:** Plan assumed run_cli() migration and D-07 dry_run bug were pending. Research (03-RESEARCH.md) confirmed both were already done.
- **Evidence:** All 12 **main**.py files already use u.Infra.run_cli(); `dry_run=cli.apply` bug has 0 grep matches.
- **Action:** Skipped task 2 entirely. No commit needed.

### Parameter Naming (Rule 2 - Missing Critical)

- **Found during:** Task 3
- **Issue:** Plan said to rename all `root: Path` to `workspace_root`. But git.py methods are called on both workspace AND project repos — renaming to `workspace_root` would be semantically wrong.
- **Fix:** Used semantic naming: `repo_root` for git ops, `scan_root` for scanner, `base_path` for private helper.
- **Verification:** `sg --pattern 'def $FN($$$, root: Path, $$$)' --lang py flext-infra/src/` returns 0 matches.

---

**Total deviations:** 2 (1 task already done, 1 naming refinement)
**Impact on plan:** Task 2 skip reduces scope. Naming refinement improves semantic correctness beyond plan's original intent.

## Issues Encountered

None

## Known Stubs

None

## Next Phase Readiness

- CLI utilities (run_cli, iter_projects, emit) are ready for consumer migration
- Parameter naming is consistent — future plans can reference workspace_root/repo_root/scan_root patterns

---
*Phase: 03-infrastructure-centralization*
*Completed: 2026-03-24*
