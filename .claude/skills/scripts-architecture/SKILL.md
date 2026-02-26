<!-- TOC START -->

- [Scope](#scope)
- [References](#references)
- [Rules](#rules)
- [Instructions](#instructions)
- [Workflow](#workflow)
- [Examples](#examples)
- [Verification](#verification)
- [Scripts](#scripts)
<!-- TOC END -->

---

name: scripts-architecture
description: Architecture services — import analysis, violation detection, code reorganization, dead code scanning, and cross-project testing. Use when using flext_infra or editing scripts/architecture/ or scripts/analysis/.

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

- `flext-core/src/flext_infra/` — Infrastructure module (contains shared services for analysis and discovery)
- `.claude/skills/flext-architecture-layers/SKILL.md`
- `.claude/skills/flext-import-rules/SKILL.md`
- `.claude/skills/rules-scripts/SKILL.md`

## Rules

- Architecture scripts must not modify code without explicit `--fix` or `--apply` flag.
- Analysis output must go to `.reports/` using artifact naming contract.
- Standard quality gates run via Make verbs (`make check`, `make validate`); architecture scripts are implementation details behind Make.
- Cross-project tests run via `make test` (or `make test FAIL_FAST=1` to stop on first failure).

## Instructions

- When adding new architecture analysis, follow the pattern in `analyze_violations.py`.
- When modifying import rules, verify cross-project imports still work.
- Keep analysis scripts read-only by default; mutations require explicit opt-in.

## Workflow

1. Identify the architecture invariant to enforce or analyze.
2. Create or modify the script under `scripts/architecture/`.
3. Test with `--help` and a dry-run mode first.
4. Verify script compiles: `python -m compileall scripts/architecture`.
5. Run project gates: `make check PROJECT=<name>` and `make validate PROJECT=<name>`.

## Examples

Good (primary — use Make verbs for standard gates):

```bash
make check PROJECT=flext-core
make check PROJECT=flext-core CHECK_GATES=lint,type
make validate PROJECT=flext-core VALIDATE_GATES=complexity
make test PROJECT=flext-core FAIL_FAST=1
```

Why good: Canonical Make contract, consistent with CLAUDE.md.

Good (internal — architecture analysis scripts behind Make):

```bash
python scripts/architecture/analyze_violations.py --output .reports/scripts-architecture--json--violations-latest.json
```

Why acceptable: Direct script invocation for detailed architecture analysis. Make verbs are the recommended workflow for standard gates.

Bad:

```bash
python scripts/architecture/fix_violations.sh  # no --dry-run
```

Why bad: Mutations without explicit opt-in.

## Verification

Make gates (primary):

- `make check PROJECT=flext-core` — lint + format + type + security gates
- `make check CHECK_GATES=lint,type` — selective check gates
- `make validate PROJECT=flext-core` — complexity + docstring gates
- `make test PROJECT=flext-core` — run project tests

Script-level checks (internal):

- `python -m compileall scripts/architecture scripts/analysis`
- `bash -n scripts/architecture/fix_violations.sh`
- `bash -n scripts/architecture/test_all_projects.sh`
- `rg "Owner-Skill:.*scripts-architecture" scripts/architecture scripts/analysis`

## Scripts

| Path                                                      | Purpose                            | Invocation                                                       |
| --------------------------------------------------------- | ---------------------------------- | ---------------------------------------------------------------- |
| `scripts/architecture/__init__.py`                        | Package marker                     | —                                                                |
| `scripts/architecture/analyze_violations.py`              | Analyze architecture violations    | `python scripts/architecture/analyze_violations.py`              |
| `scripts/architecture/correct_syntax_errors.py`           | Fix syntax errors                  | `python scripts/architecture/correct_syntax_errors.py`           |
| `scripts/architecture/diagnostic_check.py`                | Run diagnostic checks              | `python scripts/architecture/diagnostic_check.py`                |
| `scripts/architecture/fix_violations.sh`                  | Fix architecture violations        | `bash scripts/architecture/fix_violations.sh`                    |
| `scripts/architecture/refactor_imports.py`                | Refactor imports to canonical form | `python scripts/architecture/refactor_imports.py`                |
| `scripts/architecture/remove_ignore_comments.sh`          | Remove stale ignore comments       | `bash scripts/architecture/remove_ignore_comments.sh`            |
| `scripts/architecture/reorder_imports.py`                 | Reorder imports per convention     | `python scripts/architecture/reorder_imports.py`                 |
| `scripts/architecture/reorganize_di_container.py`         | Reorganize DI container            | `python scripts/architecture/reorganize_di_container.py`         |
| `scripts/architecture/simple_analyze.py`                  | Simple architecture analysis       | `python scripts/architecture/simple_analyze.py`                  |
| `scripts/architecture/standardize_serviceresult.py`       | Standardize ServiceResult usage    | `python scripts/architecture/standardize_serviceresult.py`       |
| `scripts/architecture/standardize_singer_architecture.py` | Standardize Singer architecture    | `python scripts/architecture/standardize_singer_architecture.py` |
| `scripts/architecture/test_all_projects.sh`               | Test all projects                  | `bash scripts/architecture/test_all_projects.sh`                 |
| `scripts/architecture/test_cross_project_imports.py`      | Test cross-project imports         | `python scripts/architecture/test_cross_project_imports.py`      |
| `scripts/architecture/verify_meltano_consolidation.py`    | Verify Meltano consolidation       | `python scripts/architecture/verify_meltano_consolidation.py`    |
| `scripts/analysis/find_dead_code.py`                      | Find dead/unused code              | `python scripts/analysis/find_dead_code.py`                      |
| `scripts/analyze-duplication.sh`                          | Analyze code duplication           | `bash scripts/analyze-duplication.sh`                            |
| `scripts/ast_dead_code_scanner.py`                        | AST-based dead code scanner        | `python scripts/ast_dead_code_scanner.py`                        |
| `scripts/create-dead-code-baseline.sh`                    | Create dead code baseline          | `bash scripts/create-dead-code-baseline.sh`                      |
| `scripts/create-duplicate-baseline.sh`                    | Create duplication baseline        | `bash scripts/create-duplicate-baseline.sh`                      |
| `scripts/create-duplicate-baseline-global.sh`             | Create global duplication baseline | `bash scripts/create-duplicate-baseline-global.sh`               |
| `scripts/create-duplicate-baseline-tests.sh`              | Create test duplication baseline   | `bash scripts/create-duplicate-baseline-tests.sh`                |
| `scripts/convert_aliases_to_inheritance.py`               | Convert aliases to inheritance     | `python scripts/convert_aliases_to_inheritance.py`               |
| `scripts/refactor_aliases_to_inheritance.py`              | Refactor aliases to inheritance    | `python scripts/refactor_aliases_to_inheritance.py`              |
| `scripts/content_optimizer.py`                            | Content optimization               | `python scripts/content_optimizer.py`                            |
| `scripts/fix_flext_core_unwrap.sh`                        | Fix flext-core unwrap calls        | `bash scripts/fix_flext_core_unwrap.sh`                          |
| `scripts/namespace_fix.py`                                | Fix namespace issues               | `python scripts/namespace_fix.py`                                |
| `scripts/unified_module_optimizer_simple.py`              | Unified module optimizer           | `python scripts/unified_module_optimizer_simple.py`              |
| `scripts/standardize_test_aliases.py`                     | Standardize test aliases           | `python scripts/standardize_test_aliases.py`                     |
| `scripts/standardize_tests.py`                            | Standardize test patterns          | `python scripts/standardize_tests.py`                            |
| `scripts/fix_examples_syntax.py`                          | Fix examples syntax                | `python scripts/fix_examples_syntax.py`                          |
| `scripts/flext_meltano_bridge.py`                         | Meltano bridge utility             | `python scripts/flext_meltano_bridge.py`                         |
