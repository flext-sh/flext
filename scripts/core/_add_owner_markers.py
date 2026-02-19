#!/usr/bin/env python3
# Owner-Skill: .claude/skills/scripts-infra/SKILL.md
"""One-shot script to insert Owner-Skill markers into all tracked scripts.

Run once to add markers, then delete this script.
Usage: python scripts/core/_add_owner_markers.py [--dry-run]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# ── Skill assignment map ──────────────────────────────────────────────────────
# Key: script path (relative to repo root)
# Value: skill directory name under .claude/skills/
#
# Categories:
#   scripts-infra: shared libs, core infra, config, makefiles, setup, git push/deploy/release
#   scripts-validation: all validation, linting, quality gates, baseline checks
#   scripts-security: security audit, secrets, vault
#   scripts-architecture: architecture analysis, refactoring, import reordering, standardization
#   scripts-testing: test runners, pytest analysis, stress tests
#   scripts-dependencies: dependency analysis, sync, consolidation
#   scripts-maintenance: cleanup, health checks, workspace status, git cleanup, docs maintenance

SKILL_MAP: dict[str, str] = {
    # ── scripts-infra (shared libs, core, config, setup, monorepo management) ──
    "scripts/common.py": "scripts-infra",
    "scripts/lib/common.sh": "scripts-infra",
    "scripts/lib/message_formatter.sh": "scripts-infra",
    "scripts/lib/runtime_detector.sh": "scripts-infra",
    "scripts/lib/artifact_naming.sh": "scripts-infra",  # already has marker
    "scripts/core/artifact_naming.py": "scripts-infra",  # already has marker
    ".claude/skills/scripts-infra/validate_ownership.py": "scripts-infra",  # already has marker
    ".claude/skills/scripts-infra/validate_artifact_naming.py": "scripts-infra",  # already has marker
    "scripts/core/script_registry.py": "scripts-infra",
    "scripts/core/script_runner.py": "scripts-infra",
    "scripts/config/load_staging_config.py": "scripts-infra",
    "scripts/config/setup_workspace_links.py": "scripts-infra",
    "scripts/config/standardize_pyproject.py": "scripts-infra",
    "scripts/makefiles/simplify_makefiles.py": "scripts-infra",
    "scripts/add-project.sh": "scripts-infra",
    "scripts/remove-project.sh": "scripts-infra",
    "scripts/deploy.sh": "scripts-infra",
    "scripts/release.sh": "scripts-infra",
    "scripts/commit.sh": "scripts-infra",
    "scripts/setup.sh": "scripts-infra",
    "scripts/setup_env.sh": "scripts-infra",
    "scripts/flext-constants.sh": "scripts-infra",
    "scripts/file_lock.sh": "scripts-infra",
    "scripts/safe_command.sh": "scripts-infra",
    "scripts/pre_command_validate.sh": "scripts-infra",
    "scripts/push_all_repos.sh": "scripts-infra",
    "scripts/push_repos_parallel.sh": "scripts-infra",
    "scripts/push_submodules.sh": "scripts-infra",
    "scripts/generate_all_reports.sh": "scripts-infra",
    "scripts/web_scrape_local.py": "scripts-infra",
    "scripts/standardize_version.py": "scripts-infra",
    # ── scripts-validation (linting, quality gates, baselines) ──
    "scripts/validation/run_automated_validation.sh": "scripts-validation",
    "scripts/core/skill_validate.py": "scripts-infra",
    "scripts/singer_protocol_validator.sh": "scripts-validation",
    # ── scripts-security ──
    "scripts/security/_base_security_script.py": "scripts-security",
    "scripts/security/decrypt_secrets_vault.py": "scripts-security",
    "scripts/security/example_usage.py": "scripts-security",
    "scripts/security/generate_production_secrets.py": "scripts-security",
    "scripts/security/security_audit.py": "scripts-security",
    # ── scripts-architecture (analysis, refactoring, codemods) ──
    "scripts/analysis/find_dead_code.py": "scripts-architecture",
    "scripts/architecture/analyze_violations.py": "scripts-architecture",
    "scripts/architecture/correct_syntax_errors.py": "scripts-architecture",
    "scripts/architecture/diagnostic_check.py": "scripts-architecture",
    "scripts/architecture/fix_violations.sh": "scripts-architecture",
    "scripts/architecture/refactor_imports.py": "scripts-architecture",
    "scripts/architecture/remove_ignore_comments.sh": "scripts-architecture",
    "scripts/architecture/reorder_imports.py": "scripts-architecture",
    "scripts/architecture/reorganize_di_container.py": "scripts-architecture",
    "scripts/architecture/simple_analyze.py": "scripts-architecture",
    "scripts/architecture/standardize_serviceresult.py": "scripts-architecture",
    "scripts/architecture/standardize_singer_architecture.py": "scripts-architecture",
    "scripts/architecture/test_all_projects.sh": "scripts-architecture",
    "scripts/architecture/test_cross_project_imports.py": "scripts-architecture",
    "scripts/architecture/verify_meltano_consolidation.py": "scripts-architecture",
    "scripts/analyze-duplication.sh": "scripts-architecture",
    "scripts/ast_dead_code_scanner.py": "scripts-architecture",
    "scripts/create-dead-code-baseline.sh": "scripts-architecture",
    "scripts/create-duplicate-baseline.sh": "scripts-architecture",
    "scripts/create-duplicate-baseline-global.sh": "scripts-architecture",
    "scripts/create-duplicate-baseline-tests.sh": "scripts-architecture",
    "scripts/convert_aliases_to_inheritance.py": "scripts-architecture",
    "scripts/refactor_aliases_to_inheritance.py": "scripts-architecture",
    "scripts/content_optimizer.py": "scripts-architecture",
    "scripts/fix_flext_core_unwrap.sh": "scripts-architecture",
    "scripts/namespace_fix.py": "scripts-architecture",
    "scripts/unified_module_optimizer_simple.py": "scripts-architecture",
    "scripts/standardize_test_aliases.py": "scripts-architecture",
    "scripts/standardize_tests.py": "scripts-architecture",
    "scripts/fix_examples_syntax.py": "scripts-architecture",
    "scripts/flext_meltano_bridge.py": "scripts-architecture",
    # ── scripts-testing ──
    "scripts/testing/quick_pytest_analysis.py": "scripts-testing",
    "scripts/testing/run-all-tests.sh": "scripts-testing",
    "scripts/testing/run_comprehensive_pytest_analysis.py": "scripts-testing",
    "scripts/testing/run_pytest_all_projects.py": "scripts-testing",
    "scripts/testing/run_tests.py": "scripts-testing",
    "scripts/testing/stress-test.sh": "scripts-testing",
    "scripts/testing/test-distributed.sh": "scripts-testing",
    "scripts/testing/test-end-to-end-pipeline.sh": "scripts-testing",
    "scripts/testing/testing_metrics_dashboard.sh": "scripts-testing",
    "scripts/testing/testing_quality_gates.sh": "scripts-testing",
    "scripts/run_all_examples.py": "scripts-testing",
    # ── scripts-dependencies ──
    "scripts/dependencies/analyze_dependencies.py": "scripts-dependencies",
    "scripts/dependencies/consolidate_dependencies.py": "scripts-dependencies",
    "scripts/dependencies/dependency_cache.py": "scripts-dependencies",
    "scripts/dependencies/discover_missing_deps.py": "scripts-dependencies",
    "scripts/dependencies/sync_dependencies.py": "scripts-dependencies",
    # ── scripts-maintenance (cleanup, health, docs maintenance, git ops) ──
    "scripts/maintenance/health_check_service.py": "scripts-maintenance",
    "scripts/maintenance/workspace_status.py": "scripts-maintenance",
    "scripts/git/git_ultimate_cleanup.py": "scripts-maintenance",
    "scripts/cleanup_local_venvs.sh": "scripts-maintenance",
    "scripts/cleanup_project_makefiles.py": "scripts-maintenance",
    "scripts/clean_git_ignored_files.py": "scripts-maintenance",
    "scripts/create_aggressive_gitignore.py": "scripts-maintenance",
    "scripts/merge_aggressive_gitignore.py": "scripts-maintenance",
    "scripts/add_missing_clean_targets.py": "scripts-maintenance",
    "scripts/update_clean_targets.py": "scripts-maintenance",
    "scripts/documentation/audit.py": "scripts-maintenance",
    "scripts/documentation/fix.py": "scripts-maintenance",
    "scripts/documentation/build.py": "scripts-maintenance",
    "scripts/documentation/generate.py": "scripts-maintenance",
    "scripts/documentation/validate.py": "scripts-maintenance",
    "scripts/documentation/readme_standardizer.py": "scripts-maintenance",
}


def read_lines(path: Path) -> list[str]:
    """Read file as list of lines (preserving line endings)."""
    with path.open("r", encoding="utf-8") as f:
        return f.readlines()


def write_lines(path: Path, lines: list[str]) -> None:
    """Write list of lines back to file."""
    with path.open("w", encoding="utf-8") as f:
        f.writelines(lines)


def has_marker(lines: list[str]) -> bool:
    """Check if any of the first 10 lines has an Owner-Skill marker."""
    return any(line.startswith("# Owner-Skill:") for line in lines[:10])


def insert_marker(path: Path, skill: str, dry_run: bool) -> str:
    """Insert Owner-Skill marker into a script. Returns status string."""
    full_path = REPO_ROOT / path
    if not full_path.exists():
        return f"SKIP (not found): {path}"

    lines = read_lines(full_path)
    if not lines:
        return f"SKIP (empty): {path}"

    if has_marker(lines):
        return f"SKIP (already has marker): {path}"

    marker_line = f"# Owner-Skill: .claude/skills/{skill}/SKILL.md\n"

    # Determine insertion point:
    # - If line 0 is a shebang (#!), insert at line 1
    # - Otherwise insert at line 0
    insert_at = 1 if lines[0].startswith("#!") else 0

    lines.insert(insert_at, marker_line)

    if dry_run:
        return f"DRY-RUN: {path} -> {skill} (insert at line {insert_at})"

    write_lines(full_path, lines)
    return f"ADDED: {path} -> {skill}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Add Owner-Skill markers to all scripts"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print what would be done"
    )
    args = parser.parse_args()

    added = 0
    skipped = 0
    errors = 0

    for script_path_str, skill in sorted(SKILL_MAP.items()):
        script_path = Path(script_path_str)
        result = insert_marker(script_path, skill, args.dry_run)
        print(result)

        if result.startswith(("ADDED", "DRY-RUN")):
            added += 1
        elif result.startswith("SKIP"):
            skipped += 1
        else:
            errors += 1

    print(f"\nSummary: added={added} skipped={skipped} errors={errors}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
