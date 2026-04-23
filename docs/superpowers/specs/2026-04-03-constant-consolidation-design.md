# Constant Consolidation Rule — Design Spec

**Date**: 2026-04-03
**Scope**: flext-infra codegen subcommand `consolidate`

## Goal

Automate the consolidation of inline constants into `c.Infra.*` references by reusing the existing census/governance/transformation pipeline with per-file validation and rollback.

## What Already Exists (90%)

| Need                                  | Existing API                            | Module                            |
| ------------------------------------- | --------------------------------------- | --------------------------------- |
| Find `Final[...] = value`             | `extract_constant_definitions()`        | `codegen_constant_detection`      |
| Match value → canonical               | `canonical_reference_for()`             | `codegen_constant_detection`      |
| Replace value with `c.Attr`           | `replace_canonical_values()`            | `codegen_constant_transformation` |
| Normalize `FlextXConstants.Y` → `c.Y` | `normalize_constant_aliases()`          | `codegen_constant_transformation` |
| Detect duplicates                     | `detect_duplicate_constants()`          | `codegen_constant_analysis`       |
| Detect unused                         | `detect_unused_constants()`             | `codegen_constant_detection`      |
| Remove unused                         | `remove_unused_constants()`             | `codegen_constant_transformation` |
| Scan violations (11 patterns)         | `scan_source()`                         | `violation_census_visitor`        |
| Governance canonical map              | YAML + `get_canonical_str/int_values()` | `codegen_governance`              |
| CLI codegen                           | `census`, `deduplicate`, `auto-fix`     | `codegen/cli.py`                  |

## What's New (10%)

### 1. Governance YAML — New entries only

Add frozenset/regex/tuple entries to `constants-governance.yml`:

```yaml
  - value: ["__pycache__", ".git", ".mypy_cache", "node_modules"]
    type: frozenset
    canonical_ref: "Excluded.COMMON_EXCLUDED_DIRS"
    semantic_names: [SKIP_DIRS, EXCLUDED_DIRS, IGNORE_DIRS]

  - value: "^class\\s+(\\w+)"
    type: regex
    canonical_ref: "SourceCode.CLASS_NAME_RE"
    semantic_names: [CLASS_RE, CLASS_PATTERN]
```

### 2. Governance getters — 2 new methods (same pattern)

In `codegen_governance.py`, add `get_canonical_frozenset_values()` and `get_canonical_regex_values()`. Same 5-line pattern as existing `get_canonical_str_values()`.

### 3. Subcommand `consolidate` — thin orchestrator

New handler in `codegen/cli.py` using existing APIs:

```
python -m flext_infra codegen consolidate [--projects PATH] [--dry-run] [--apply] [--json]
```

**Pipeline (two phases):**

Phase 1 — Scan (always runs):

1. `extract_constant_definitions()` per file
2. `detect_hardcoded_canonicals()` for exact matches
3. `scan_constant_usages()` for direct refs needing normalization
4. Report: found N exact, N structural, N semantic matches

Phase 2 — Apply (with `--apply`):
For each file with exact/structural matches:

1. Read source (backup in memory)
2. Call `replace_canonical_values()` + `normalize_constant_aliases()`
3. Validate via subprocess: `ruff check`, `pyright`, `mypy`, `pyrefly` on the single file
4. If ANY validator fails: revert file to backup, report diff + error
5. If all pass: keep changes, report success

**Semantic matches** (superset/subset frozensets) are NEVER auto-applied — report only.

### 4. Output

- **stdout**: colored table with applied/suggested/failed sections
- **JSON**: `.reports/constant-consolidation.json` with `--json` flag
- Same output pattern as existing `census` command

## Files Modified

1. `rules/constants-governance.yml` — add frozenset/regex/tuple entries
2. `_utilities/codegen_governance.py` — add 2 getter methods
3. `codegen/cli.py` — add `consolidate` handler
4. `models/` — add `ConsolidationResult` model (if needed, else reuse existing)

## Non-Goals

- No new detection logic — reuse `codegen_constant_detection`
- No new transformation logic — reuse `codegen_constant_transformation`
- No new visitor patterns — reuse `violation_census_visitor`
- No refactoring of existing code
