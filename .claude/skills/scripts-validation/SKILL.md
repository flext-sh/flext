---
name: scripts-validation
description: Validation scripts — policy gates, automated checks, ast-grep enforcement, and the validation orchestrator. Use when editing scripts/validation/ or scripts/validate_all_projects.sh.
---

# Scripts Validation

## Scope

- `scripts/validation/run_automated_validation.sh`
- `scripts/validation/enforce_no_dict_no_any.sh`
- `scripts/validation/enforce_pydantic_v2_skill.sh`
- `scripts/validation/fix_pydantic_v2_violations.sh`
- `scripts/validation/run_skill_autofix.sh`
- `scripts/validation/run_skill_scan.sh`
- `scripts/validation/collect_file_metrics.py`
- `scripts/validation/domain_separation_validator.sh`
- `scripts/validation/ecosystem_quality_validator.sh`
- `scripts/validation/ast-grep-no-dict.yml`
- `scripts/validation/ast-grep-safe-fixes.yml`
- `scripts/validation/ast-grep-pydantic-v2.yml`
- `scripts/validation/scripts-validation--ast-grep--bash-strict-mode.yml`
- `scripts/validation/scripts-validation--ast-grep--python-main-guard.yml`
- `scripts/validation/scripts-validation--ast-grep--no-interactive.yml`
- `scripts/validate_all_projects.sh`
- `scripts/quick_lint_check.sh`
- `scripts/baseline_quality_check.sh`
- `scripts/constants_standardization_validator.sh`
- `scripts/detect_violations_large_scale.sh`
- `scripts/analyze_project_pre_violations.sh`
- `scripts/ecosystem_validation.py`
- `scripts/verify_standardization.py`
- `scripts/fix_ruff_errors.py`
- `scripts/singer_protocol_validator.sh`
- `scripts/field_parameter_standardizer.sh`

## References

- `.claude/skills/flext-automation-skill-pattern/SKILL.md`
- `.claude/skills/flext-quality-gates/SKILL.md`
- `.sisyphus/baselines/`
- `.sisyphus/reports/`
- `Makefile`

## Rules

- Every checker script must support `baseline` and `strict` modes.
- Quick validation must complete in under 60 seconds.
- Policy gates must emit machine-readable JSON reports under `.sisyphus/reports/`.
- ast-grep rule packs must use the artifact naming contract: `scripts-validation--ast-grep--<slug>.yml`.
- All validators must be non-interactive and exit with clear status codes (0=pass, 1=fail, 2=invalid args).

## Instructions

- When adding a new validation gate, wire it into `run_automated_validation.sh` for both quick and full modes.
- When modifying policy gates, update both baseline and latest report paths.
- When creating ast-grep rule packs, follow the existing pattern in `ast-grep-no-dict.yml`.
- Wire new gates into `make validate-scripts` for CI enforcement.

## Workflow

1. Identify the validation invariant to enforce.
2. Create or modify the checker script with baseline/strict modes.
3. Add report output under `.sisyphus/reports/` using artifact naming helpers.
4. Wire into `run_automated_validation.sh` (quick and/or full).
5. Run `scripts/validation/run_automated_validation.sh quick` to verify integration.

## Examples

Good:

```bash
scripts/validation/enforce_no_dict_no_any.sh --mode baseline --root .
scripts/validation/run_automated_validation.sh quick
```

Why good: Reproducible, non-interactive, tied to artifacts.

Bad:

```bash
grep -r "dict" . | wc -l
```

Why bad: No baseline comparison, no structured output, no gate behavior.

## Verification

- `bash -n scripts/validation/enforce_no_dict_no_any.sh`
- `bash -n scripts/validation/run_automated_validation.sh`
- `bash -n scripts/validate_all_projects.sh`
- `scripts/validation/run_automated_validation.sh quick`
- `rg "Owner-Skill:.*scripts-validation" scripts/validation scripts/validate_all_projects.sh`

## Scripts

| Path | Purpose | Invocation |
|------|---------|------------|
| `scripts/validation/run_automated_validation.sh` | Orchestrator: quick/full validation | `scripts/validation/run_automated_validation.sh quick` |
| `scripts/validation/enforce_no_dict_no_any.sh` | Policy gate: ban dict/Any patterns | `scripts/validation/enforce_no_dict_no_any.sh --mode baseline --root .` |
| `scripts/validation/enforce_pydantic_v2_skill.sh` | Policy gate: Pydantic v2 compliance | `scripts/validation/enforce_pydantic_v2_skill.sh --mode baseline --root .` |
| `scripts/validation/fix_pydantic_v2_violations.sh` | Autofix: Pydantic v2 violations | `scripts/validation/fix_pydantic_v2_violations.sh` |
| `scripts/validation/run_skill_autofix.sh` | Run skill-driven autofixes | `scripts/validation/run_skill_autofix.sh` |
| `scripts/validation/run_skill_scan.sh` | Run skill-driven scans | `scripts/validation/run_skill_scan.sh` |
| `scripts/validation/collect_file_metrics.py` | Collect per-file quality metrics | `python scripts/validation/collect_file_metrics.py` |
| `scripts/validation/domain_separation_validator.sh` | Validate domain separation | `scripts/validation/domain_separation_validator.sh` |
| `scripts/validation/ecosystem_quality_validator.sh` | Validate ecosystem quality | `scripts/validation/ecosystem_quality_validator.sh` |
| `scripts/validate_all_projects.sh` | Workspace-wide validation across all projects | `bash scripts/validate_all_projects.sh` |
| `scripts/quick_lint_check.sh` | Quick lint check | `bash scripts/quick_lint_check.sh` |
| `scripts/baseline_quality_check.sh` | Baseline quality check | `bash scripts/baseline_quality_check.sh` |
| `scripts/constants_standardization_validator.sh` | Constants standardization validator | `bash scripts/constants_standardization_validator.sh` |
| `scripts/detect_violations_large_scale.sh` | Large-scale violation detection | `bash scripts/detect_violations_large_scale.sh` |
| `scripts/analyze_project_pre_violations.sh` | Pre-violation analysis | `bash scripts/analyze_project_pre_violations.sh` |
| `scripts/ecosystem_validation.py` | Ecosystem validation | `python scripts/ecosystem_validation.py` |
| `scripts/verify_standardization.py` | Verify standardization | `python scripts/verify_standardization.py` |
| `scripts/fix_ruff_errors.py` | Fix ruff errors | `python scripts/fix_ruff_errors.py` |
| `scripts/singer_protocol_validator.sh` | Singer protocol validator | `bash scripts/singer_protocol_validator.sh` |
| `scripts/field_parameter_standardizer.sh` | Field parameter standardizer | `bash scripts/field_parameter_standardizer.sh` |
