---
name: scripts-architecture
description: Architecture scripts — import analysis, violation detection, code reorganization, dead code scanning, and cross-project testing. Use when editing scripts/architecture/ or scripts/analysis/.
---

# Scripts Architecture

## Scope

- `scripts/architecture/analyze_violations.py`
- `scripts/architecture/correct_syntax_errors.py`
- `scripts/architecture/diagnostic_check.py`
- `scripts/architecture/fix_violations.sh`
- `scripts/architecture/__init__.py`
- `scripts/architecture/refactor_imports.py`
- `scripts/architecture/remove_ignore_comments.sh`
- `scripts/architecture/reorder_imports.py`
- `scripts/architecture/reorganize_di_container.py`
- `scripts/architecture/simple_analyze.py`
- `scripts/architecture/standardize_serviceresult.py`
- `scripts/architecture/standardize_singer_architecture.py`
- `scripts/architecture/test_all_projects.sh`
- `scripts/architecture/test_cross_project_imports.py`
- `scripts/architecture/verify_meltano_consolidation.py`
- `scripts/analysis/find_dead_code.py`
- `scripts/analyze-duplication.sh`
- `scripts/ast_dead_code_scanner.py`
- `scripts/create-dead-code-baseline.sh`
- `scripts/create-duplicate-baseline.sh`
- `scripts/create-duplicate-baseline-global.sh`
- `scripts/create-duplicate-baseline-tests.sh`
- `scripts/convert_aliases_to_inheritance.py`
- `scripts/refactor_aliases_to_inheritance.py`
- `scripts/content_optimizer.py`
- `scripts/fix_flext_core_unwrap.sh`
- `scripts/namespace_fix.py`
- `scripts/unified_module_optimizer_simple.py`
- `scripts/standardize_test_aliases.py`
- `scripts/standardize_tests.py`
- `scripts/fix_examples_syntax.py`
- `scripts/flext_meltano_bridge.py`

## References

- `.claude/skills/flext-architecture-layers/SKILL.md`
- `.claude/skills/flext-import-rules/SKILL.md`
- `.claude/skills/rules-scripts/SKILL.md`

## Rules

- Architecture scripts must not modify code without explicit `--fix` or `--apply` flag.
- Analysis output must go to `.sisyphus/reports/` using artifact naming contract.
- Cross-project tests must pass from repo root using `bash scripts/architecture/test_all_projects.sh`.

## Instructions

- When adding new architecture analysis, follow the pattern in `analyze_violations.py`.
- When modifying import rules, verify cross-project imports still work.
- Keep analysis scripts read-only by default; mutations require explicit opt-in.

## Workflow

1. Identify the architecture invariant to enforce or analyze.
2. Create or modify the script under `scripts/architecture/`.
3. Test with `--help` and a dry-run mode first.
4. Verify with `python -m compileall scripts/architecture`.

## Examples

Good:

```bash
python scripts/architecture/analyze_violations.py --output .sisyphus/reports/scripts-architecture--json--violations-latest.json
```

Why good: Explicit output path, artifact naming, read-only by default.

Bad:

```bash
python scripts/architecture/fix_violations.sh  # no --dry-run
```

Why bad: Mutations without explicit opt-in.

## Verification

- `python -m compileall scripts/architecture scripts/analysis`
- `bash -n scripts/architecture/fix_violations.sh`
- `bash -n scripts/architecture/test_all_projects.sh`
- `rg "Owner-Skill:.*scripts-architecture" scripts/architecture scripts/analysis`

## Scripts

| Path | Purpose | Invocation |
|------|---------|------------|
| `scripts/architecture/__init__.py` | Package marker | — |
| `scripts/architecture/analyze_violations.py` | Analyze architecture violations | `python scripts/architecture/analyze_violations.py` |
| `scripts/architecture/correct_syntax_errors.py` | Fix syntax errors | `python scripts/architecture/correct_syntax_errors.py` |
| `scripts/architecture/diagnostic_check.py` | Run diagnostic checks | `python scripts/architecture/diagnostic_check.py` |
| `scripts/architecture/fix_violations.sh` | Fix architecture violations | `bash scripts/architecture/fix_violations.sh` |
| `scripts/architecture/refactor_imports.py` | Refactor imports to canonical form | `python scripts/architecture/refactor_imports.py` |
| `scripts/architecture/remove_ignore_comments.sh` | Remove stale ignore comments | `bash scripts/architecture/remove_ignore_comments.sh` |
| `scripts/architecture/reorder_imports.py` | Reorder imports per convention | `python scripts/architecture/reorder_imports.py` |
| `scripts/architecture/reorganize_di_container.py` | Reorganize DI container | `python scripts/architecture/reorganize_di_container.py` |
| `scripts/architecture/simple_analyze.py` | Simple architecture analysis | `python scripts/architecture/simple_analyze.py` |
| `scripts/architecture/standardize_serviceresult.py` | Standardize ServiceResult usage | `python scripts/architecture/standardize_serviceresult.py` |
| `scripts/architecture/standardize_singer_architecture.py` | Standardize Singer architecture | `python scripts/architecture/standardize_singer_architecture.py` |
| `scripts/architecture/test_all_projects.sh` | Test all projects | `bash scripts/architecture/test_all_projects.sh` |
| `scripts/architecture/test_cross_project_imports.py` | Test cross-project imports | `python scripts/architecture/test_cross_project_imports.py` |
| `scripts/architecture/verify_meltano_consolidation.py` | Verify Meltano consolidation | `python scripts/architecture/verify_meltano_consolidation.py` |
| `scripts/analysis/find_dead_code.py` | Find dead/unused code | `python scripts/analysis/find_dead_code.py` |
