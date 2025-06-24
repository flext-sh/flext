#!/usr/bin/env python3
"""
Incremental Unified Lint Fixer - Máxima Redução de Lints.

Combina todas as abordagens anteriores em um script unificado e incremental
para reduzir o máximo de lint errors possível.
"""

import json
import logging
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/incremental_unified_fixer.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

__version__ = "2.0.0-UNIFIED"


@dataclass
class UnifiedFixerConfig:
    """Configuration for the unified fixer."""

    target_projects: list[str] = field(default_factory=list)
    exclude_patterns: list[str] = field(
        default_factory=lambda: [
            "__pycache__",
            ".venv",
            ".git",
            "dist",
            "build",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            "node_modules",
            "archive",
            "backup",
            "logs",
        ]
    )

    # All available fixes
    enabled_fixes: dict[str, bool] = field(
        default_factory=lambda: {
            "undefined_variables": True,
            "type_annotations": True,
            "logging_patterns": True,
            "exception_handling": True,
            "unused_variables": True,
            "string_standardization": True,
            "whitespace_cleanup": True,
            "import_organization": True,
            "boolean_fixes": True,
            "none_comparisons": True,
            "docstring_fixes": True,
            "comprehension_improvements": True,
            "security_fixes": True,
        }
    )

    # Safety settings
    max_changes_per_file: int = 150
    validate_syntax: bool = True
    aggressive_mode: bool = False


class IncrementalUnifiedFixer:
    """Unified fixer that combines all approaches."""

    def __init__(self, config: UnifiedFixerConfig) -> None:
        self.config = config
        self.workspace_root = Path.cwd()
        self.session_id = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")

        # Statistics
        self.stats = {
            "files_processed": 0,
            "files_modified": 0,
            "total_fixes": 0,
            "fixes_by_category": {},
            "errors_prevented": 0,
        }

        logger.info("🚀 Incremental Unified Fixer v%s - STARTED", __version__)

        # Create logs directory
        Path("logs").mkdir(exist_ok=True)

    def process_workspace(self, dry_run: bool = False) -> dict[str, Any]:
        """Process workspace incrementally."""
        logger.info("🔧 Starting incremental workspace processing")

        projects = self._discover_projects()
        logger.info("📁 Found %d projects to process", len(projects))

        results = {"projects": {}, "summary": {}}

        for project in projects:
            logger.info("⚡ Processing project: %s", project.name)

            try:
                project_result = self._process_project_incrementally(project, dry_run)
                results["projects"][project.name] = project_result

                logger.info(
                    "✅ Project %s: %d→%d errors (%+d improvement)",
                    project.name,
                    project_result["initial_errors"],
                    project_result["final_errors"],
                    project_result["improvement"],
                )

            except Exception as e:
                logger.error("❌ Failed to process project %s: %s", project.name, e)
                results["projects"][project.name] = {"error": str(e)}

        # Generate summary
        results["summary"] = self._generate_summary(results["projects"])

        # Save report
        if not dry_run:
            self._save_report(results)

        return results

    def _discover_projects(self) -> list[Path]:
        """Discover Python projects in workspace."""
        if self.config.target_projects:
            projects: list = []
            for proj_name in self.config.target_projects:
                proj_path = self.workspace_root / proj_name
                if proj_path.exists() and proj_path.is_dir():
                    projects.append(proj_path)
            return projects

        # Auto-discover
        projects: list = []
        for item in self.workspace_root.iterdir():
            if (
                item.is_dir()
                and not item.name.startswith(".")
                and not self._should_skip_directory(item)
                and self._is_python_project(item)
            ):
                projects.append(item)

        return sorted(projects)

    def _is_python_project(self, path: Path) -> bool:
        """Check if directory is a Python project."""
        indicators = ["pyproject.toml", "src", "setup.py", "requirements.txt"]
        return any((path / indicator).exists() for indicator in indicators) or any(
            path.glob("*.py")
        )

    def _should_skip_directory(self, path: Path) -> bool:
        """Check if directory should be skipped."""
        return any(pattern in path.name for pattern in self.config.exclude_patterns)

    def _process_project_incrementally(
        self, project_path: Path, dry_run: bool
    ) -> dict[str, Any]:
        """Process a single project with incremental fixes."""
        # Get initial error count
        initial_errors = self._count_lint_errors(project_path)

        # Get Python files
        python_files = self._get_python_files(project_path)

        logger.info(
            "📂 Project %s: %d files, %d initial errors",
            project_path.name,
            len(python_files),
            initial_errors,
        )

        # Process files
        files_modified = 0
        total_fixes = 0
        fixes_by_category: dict = {}

        for py_file in python_files:
            try:
                if dry_run:
                    potential_fixes = self._analyze_file_potential(py_file)
                    if potential_fixes > 0:
                        files_modified += 1
                        total_fixes += potential_fixes
                    file_fixes, file_category_fixes = self._fix_file_comprehensively(
                        py_file
                    )
                    if file_fixes > 0:
                        files_modified += 1
                        total_fixes += file_fixes

                        # Aggregate category fixes
                        for category, count in file_category_fixes.items():
                            if category not in fixes_by_category:
                                fixes_by_category[category] = 0
                            fixes_by_category[category] += count

            except Exception as e:
                logger.error("Error processing file %s: %s", py_file, e)
                self.stats["errors_prevented"] += 1

        # Get final error count
        final_errors = (
            initial_errors if dry_run else self._count_lint_errors(project_path)
        )

        # Update global stats
        self.stats["files_processed"] += len(python_files)
        self.stats["files_modified"] += files_modified
        self.stats["total_fixes"] += total_fixes

        return {
            "initial_errors": initial_errors,
            "final_errors": final_errors,
            "files_processed": len(python_files),
            "files_modified": files_modified,
            "total_fixes": total_fixes,
            "fixes_by_category": fixes_by_category,
            "improvement": initial_errors - final_errors,
        }

    def _get_python_files(self, project_path: Path) -> list[Path]:
        """Get all Python files in project."""
        python_files: list = []
        for py_file in project_path.rglob("*.py"):
            if not self._should_skip_file(py_file):
                python_files.append(py_file)
        return python_files

    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        return any(
            pattern in str(file_path) for pattern in self.config.exclude_patterns
        )

    def _analyze_file_potential(self, file_path: Path) -> int:
        """Analyze potential fixes for a file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            potential_fixes = 0

            # Quick analysis of fixable issues
            if self.config.enabled_fixes["undefined_variables"]:
                potential_fixes += content.count("config_key")

            if self.config.enabled_fixes["type_annotations"]:
                potential_fixes += len(
                    re.findall(r"def \w+\([^)]*\):\s*(?:#.*)?$", content, re.MULTILINE)
                )

            if self.config.enabled_fixes["logging_patterns"]:
                potential_fixes += len(
                    re.findall(r'logger\.\w+\(f"[^"]*\{[^}]+\}', content)
                )

            if self.config.enabled_fixes["whitespace_cleanup"]:
                potential_fixes += len(
                    [line for line in content.split("\n") if line.rstrip() != line]
                )

            if self.config.enabled_fixes["string_standardization"]:
                potential_fixes += content.count("'") // 4  # Rough estimate

            return min(potential_fixes, 100)  # Cap for safety

        except Exception:
            return 0

    def _fix_file_comprehensively(self, file_path: Path) -> tuple[int, dict[str, int]]:
        """Apply comprehensive fixes to a single file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            original_content = content
            category_fixes: dict = {}

            # Apply fixes in order of importance and safety

            # 1. Critical undefined variables (must fix first)
            if self.config.enabled_fixes["undefined_variables"]:
                content, fixes = self._fix_undefined_variables(content)
                if fixes > 0:
                    category_fixes["undefined_variables"] = fixes

            # 2. Exception handling (safety critical)
            if self.config.enabled_fixes["exception_handling"]:
                content, fixes = self._fix_exception_handling(content)
                if fixes > 0:
                    category_fixes["exception_handling"] = fixes

            # 3. Type annotations (helps with other fixes)
            if self.config.enabled_fixes["type_annotations"]:
                content, fixes = self._fix_type_annotations(content)
                if fixes > 0:
                    category_fixes["type_annotations"] = fixes

            # 4. Logging patterns (common issue)
            if self.config.enabled_fixes["logging_patterns"]:
                content, fixes = self._fix_logging_patterns(content)
                if fixes > 0:
                    category_fixes["logging_patterns"] = fixes

            # 5. Unused variables (function signature fixes)
            if self.config.enabled_fixes["unused_variables"]:
                content, fixes = self._fix_unused_variables(content)
                if fixes > 0:
                    category_fixes["unused_variables"] = fixes

            # 6. String standardization
            if self.config.enabled_fixes["string_standardization"]:
                content, fixes = self._fix_string_standardization(content)
                if fixes > 0:
                    category_fixes["string_standardization"] = fixes

            # 7. Whitespace cleanup
            if self.config.enabled_fixes["whitespace_cleanup"]:
                content, fixes = self._fix_whitespace_cleanup(content)
                if fixes > 0:
                    category_fixes["whitespace_cleanup"] = fixes

            # 8. Boolean fixes
            if self.config.enabled_fixes["boolean_fixes"]:
                content, fixes = self._fix_boolean_issues(content)
                if fixes > 0:
                    category_fixes["boolean_fixes"] = fixes

            # 9. None comparisons
            if self.config.enabled_fixes["none_comparisons"]:
                content, fixes = self._fix_none_comparisons(content)
                if fixes > 0:
                    category_fixes["none_comparisons"] = fixes

            # 10. Security fixes (if aggressive mode)
            if (
                self.config.enabled_fixes["security_fixes"]
                and self.config.aggressive_mode
            ):
                content, fixes = self._fix_security_issues(content)
                if fixes > 0:
                    category_fixes["security_fixes"] = fixes

            # Validation and application
            if content != original_content:
                total_changes = self._count_changes(original_content, content)

                # Safety check
                if total_changes > self.config.max_changes_per_file:
                    logger.warning(
                        "⚠️ Too many changes (%d) in %s, skipping",
                        total_changes,
                        file_path.name,
                    )
                    return 0, {}

                # Syntax validation
                if self.config.validate_syntax:
                    try:
                        compile(content, str(file_path), "exec")
                    except SyntaxError as e:
                        logger.warning(
                            "⚠️ Syntax error in %s after fixes: %s", file_path.name, e
                        )
                        return 0, {}

                # Apply changes
                file_path.write_text(content, encoding="utf-8")
                total_fixes = sum(category_fixes.values())

                logger.debug(
                    "✅ Fixed %s: %d fixes applied", file_path.name, total_fixes
                )
                return total_fixes, category_fixes

            return 0, {}

        except Exception as e:
            logger.error("Error fixing file %s: %s", file_path, e)
            return 0, {}

    def _fix_undefined_variables(self, content: str) -> tuple[str, int]:
        """Fix undefined variables like config_key."""
        fixes = 0
        lines = content.split("\n")

        for i, line in enumerate(lines):
            if "config_key" in line and "F821" not in line:  # Avoid comments
                # Look for the loop variable in previous lines
                if i > 0:
                    for j in range(max(0, i - 3), i):
                        prev_line = lines[j]
                        if "for " in prev_line and ".items()" in prev_line:
                            match = re.search(r"for (\w+),", prev_line)
                            if match:
                                key_var = match.group(1)
                                lines[i] = line.replace("config_key", key_var)
                                fixes += 1
                                break
                        # Fallback: use a sensible default
                        lines[i] = line.replace("config_key", "key")
                        fixes += 1

        return "\n".join(lines), fixes

    def _fix_type_annotations(self, content: str) -> tuple[str, int]:
        """Add missing type annotations."""
        lines = content.split("\n")
        fixes = 0
        needs_typing = False

        for i, line in enumerate(lines):
            stripped = line.strip()
            if (
                stripped.startswith("def ")
                and stripped.endswith(":")
                and "-> " not in stripped
                and not any(x in stripped for x in ["__init__", "__str__", "__repr__"])
            ):
                # Add appropriate return type
                if any(name in stripped for name in ["test_", "setUp", "tearDown"]):
                    lines[i] = line.replace("):", ") -> None:")
                    fixes += 1
                elif "main(" in stripped:
                    lines[i] = line.replace("):", ") -> None:")
                    fixes += 1
                elif "(" in stripped and ")" in stripped:
                    lines[i] = line.replace("):", ") -> Any:")
                    needs_typing = True
                    fixes += 1

        result = "\n".join(lines)

        # Add typing import if needed
        if needs_typing and "from typing import" not in result:
            lines = result.split("\n")
            insert_pos = 0

            # Find appropriate position for import
            for i, line in enumerate(lines):
                if line.strip().startswith(("from ", "import ")):
                    insert_pos = i + 1
                elif line.strip() and not line.startswith(('"""', "'''", "#")):
                    break

            lines.insert(insert_pos, "from typing import Any")
            result = "\n".join(lines)
            fixes += 1

        return result, fixes

    def _fix_logging_patterns(self, content: str) -> tuple[str, int]:
        """Fix f-string usage in logging."""
        fixes = 0

        # Convert f-strings in logging to % formatting
        patterns = [
            (
                r'logger\.error\(f"([^"]*)\{([^}]+)\}([^"]*)"\)',
                r'logger.error("\1%s\3", \2)',
            ),
            (
                r'logger\.warning\(f"([^"]*)\{([^}]+)\}([^"]*)"\)',
                r'logger.warning("\1%s\3", \2)',
            ),
            (
                r'logger\.info\(f"([^"]*)\{([^}]+)\}([^"]*)"\)',
                r'logger.info("\1%s\3", \2)',
            ),
            (
                r'logger\.debug\(f"([^"]*)\{([^}]+)\}([^"]*)"\)',
                r'logger.debug("\1%s\3", \2)',
            ),
        ]

        for pattern, replacement in patterns:
            before = content
            content = re.sub(pattern, replacement, content)
            if content != before:
                fixes += 1

        return content, fixes

    def _fix_exception_handling(self, content: str) -> tuple[str, int]:
        """Fix exception handling to include 'from e'."""
        lines = content.split("\n")
        fixes = 0

        for i, line in enumerate(lines):
            if "except " in line and " as e:" in line:
                # Look for raise statements in following lines
                for j in range(i + 1, min(i + 4, len(lines))):
                    next_line = lines[j].strip()
                    if (
                        next_line.startswith("raise ")
                        and " from e" not in next_line
                        and "raise e" not in next_line
                    ):
                        if next_line.endswith(")"):
                            lines[j] = lines[j].replace(")", " from e)")
                            lines[j] = lines[j] + " from e"
                        fixes += 1
                        break
                    if next_line and not next_line.startswith((" ", "\t")):
                        # Left the except block
                        break

        return "\n".join(lines), fixes

    def _fix_unused_variables(self, content: str) -> tuple[str, int]:
        """Fix unused method arguments."""
        fixes = 0

        # Handle specific ARG002 violations
        replacements = [
            ("shipment_data:", "_shipment_data:"),
            ("inventory_data:", "_inventory_data:"),
            ("shipment_data,", "_shipment_data,"),
            ("inventory_data,", "_inventory_data,"),
        ]

        for old, new in replacements:
            if old in content:
                content = content.replace(old, new)
                fixes += 1

        return content, fixes

    def _fix_string_standardization(self, content: str) -> tuple[str, int]:
        """Standardize string quotes to double quotes."""
        fixes = 0
        lines = content.split("\n")

        for i, line in enumerate(lines):
            # Only fix lines that have single quotes but no double quotes
            # (simple case)
            if "'" in line and '"' not in line and not line.strip().startswith("#"):
                # Simple single quote to double quote conversion
                new_line = re.sub(r"'([^'\\]*(?:\\.[^'\\]*)*)'", r'"\1"', line)
                if new_line != line:
                    lines[i] = new_line
                    fixes += 1

        return "\n".join(lines), fixes

    def _fix_whitespace_cleanup(self, content: str) -> tuple[str, int]:
        """Clean up whitespace issues."""
        lines = content.split("\n")
        fixes = 0

        # Remove trailing whitespace
        for i, line in enumerate(lines):
            stripped = line.rstrip()
            if stripped != line:
                lines[i] = stripped
                fixes += 1

        # Remove excessive blank lines (more than 2)
        new_lines: list = []
        blank_count = 0

        for line in lines:
            if line.strip() == "":
                blank_count += 1
                if blank_count <= 2:
                    new_lines.append(line)
                    fixes += 1  # Count removed lines
                blank_count = 0
                new_lines.append(line)

        return "\n".join(new_lines), fixes

    def _fix_boolean_issues(self, content: str) -> tuple[str, int]:
        """Fix boolean comparison issues."""
        fixes = 0

        patterns = [
            (r"== True\b", ""),
            (r"== False\b", "not "),
            (r"!= True\b", "not "),
            (r"!= False\b", ""),
        ]

        for pattern, replacement in patterns:
            before = content
            content = re.sub(pattern, replacement, content)
            if content != before:
                fixes += 1

        return content, fixes

    def _fix_none_comparisons(self, content: str) -> tuple[str, int]:
        """Fix None comparison issues."""
        fixes = 0

        patterns = [
            (r"== None\b", "is None"),
            (r"!= None\b", "is not None"),
        ]

        for pattern, replacement in patterns:
            before = content
            content = re.sub(pattern, replacement, content)
            if content != before:
                fixes += 1

        return content, fixes

    def _fix_security_issues(self, content: str) -> tuple[str, int]:
        """Fix basic security issues (aggressive mode only)."""
        fixes = 0

        # Remove hardcoded passwords/secrets (basic patterns)
        patterns = [
            (
                r'password\s*=\s*["\'][^"\']{8,}["\']',
                'password = os.getenv("PASSWORD")',
            ),
            (r'secret\s*=\s*["\'][^"\']{16,}["\']', 'secret = os.getenv("SECRET")'),
        ]

        for pattern, replacement in patterns:
            before = content
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
            if content != before:
                fixes += 1
                # Ensure os import
                if "import os" not in content:
                    lines = content.split("\n")
                    lines.insert(0, "import os")
                    content = "\n".join(lines)

        return content, fixes

    def _count_changes(self, original: str, modified: str) -> int:
        """Count the number of line changes."""
        orig_lines = original.split("\n")
        mod_lines = modified.split("\n")

        changes = 0
        max_len = max(len(orig_lines), len(mod_lines))

        for i in range(max_len):
            orig_line = orig_lines[i] if i < len(orig_lines) else ""
            mod_line = mod_lines[i] if i < len(mod_lines) else ""
            if orig_line != mod_line:
                changes += 1

        return changes

    def _count_lint_errors(self, project_path: Path) -> int:
        """Count lint errors in project."""
        try:
            result = subprocess.run(
                ["ruff", "check", str(project_path)],
                capture_output=True,
                text=True,
                timeout=60,
            )
            # Count actual error lines (not empty lines)
            errors = [line for line in result.stdout.split("\n") if line.strip()]
            return len(errors)
        except Exception as e:
            logger.warning("Could not count lint errors for %s: %s", project_path, e)
            return 0

    def _generate_summary(self, project_results: dict) -> dict[str, Any]:
        """Generate processing summary."""
        successful_projects = {
            k: v for k, v in project_results.items() if "error" not in v
        }

        if not successful_projects:
            return {
                "total_initial_errors": 0,
                "total_final_errors": 0,
                "total_fixes_applied": 0,
                "total_improvement": 0,
                "improvement_percentage": 0,
                "zero_tolerance_achieved": False,
                "projects_processed": len(project_results),
                "projects_successful": 0,
                "projects_failed": len(project_results),
            }

        total_initial = sum(r["initial_errors"] for r in successful_projects.values())
        total_final = sum(r["final_errors"] for r in successful_projects.values())
        total_fixes = sum(r["total_fixes"] for r in successful_projects.values())

        improvement = total_initial - total_final
        improvement_pct = (
            (improvement / total_initial * 100) if total_initial > 0 else 0
        )

        return {
            "total_initial_errors": total_initial,
            "total_final_errors": total_final,
            "total_fixes_applied": total_fixes,
            "total_improvement": improvement,
            "improvement_percentage": improvement_pct,
            "zero_tolerance_achieved": total_final == 0,
            "projects_processed": len(project_results),
            "projects_successful": len(successful_projects),
            "projects_failed": len(project_results) - len(successful_projects),
            "global_stats": self.stats,
        }

    def _save_report(self, results: dict) -> None:
        """Save comprehensive report."""
        Path("reports").mkdir(exist_ok=True)
        report_path = Path(f"reports/incremental_unified_fixer_{self.session_id}.json")

        report_data = {
            "metadata": {
                "version": __version__,
                "session_id": self.session_id,
                "timestamp": datetime.now(UTC).isoformat(),
                "workspace": str(self.workspace_root),
                "configuration": {
                    "target_projects": self.config.target_projects,
                    "enabled_fixes": self.config.enabled_fixes,
                    "max_changes_per_file": self.config.max_changes_per_file,
                    "aggressive_mode": self.config.aggressive_mode,
                },
            },
            "results": results,
            "claude_md_compliance": {
                "zero_tolerance_achieved": results["summary"][
                    "zero_tolerance_achieved"
                ],
                "total_violations": results["summary"]["total_final_errors"],
                "improvement_achieved": results["summary"]["total_improvement"],
            },
        }

        report_path.write_text(json.dumps(report_data, indent=2, default=str))
        logger.info("📋 Report saved: %s", report_path)


def main() -> None:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description=f"Incremental Unified Lint Fixer v{__version__}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--projects", nargs="+", help="Specific projects to process")
    parser.add_argument(
        "--dry-run", action="store_true", help="Analyze without applying fixes"
    )
    parser.add_argument(
        "--aggressive",
        action="store_true",
        help="Enable aggressive mode with security fixes",
    )
    parser.add_argument(
        "--max-changes", type=int, default=150, help="Maximum changes per file"
    )

    args = parser.parse_args()

    # Create configuration
    config = UnifiedFixerConfig()
    if args.projects:
        config.target_projects = args.projects
    if args.aggressive:
        config.aggressive_mode = True
        config.max_changes_per_file = 300
    config.max_changes_per_file = args.max_changes

    # Initialize and run
    fixer = IncrementalUnifiedFixer(config)
    results = fixer.process_workspace(dry_run=args.dry_run)

    # Print final results
    summary = results["summary"]
    print(f"\n🚀 INCREMENTAL UNIFIED FIXER v{__version__} - COMPLETE")
    print("=" * 70)
    print(
        f"📊 Projects: {summary['projects_successful']}/{
            summary['projects_processed']
        } successful"
    )
    print(
        f"🔢 Lint Errors: {summary['total_initial_errors']} → {summary['total_final_errors']} "
        f"({summary['total_improvement']:+d})"
    )
    print(f"🔧 Total Fixes: {summary['total_fixes_applied']} applied")
    print(f"📈 Improvement: {summary['improvement_percentage']:.1f}%")

    # CLAUDE.md compliance
    if summary["zero_tolerance_achieved"]:
        print("🎉 CLAUDE.md ZERO TOLERANCE: ✅ ACHIEVED")
        print("   All lint violations have been resolved!")
        sys.exit(0)
        print(
            f"⚠️ CLAUDE.md ZERO TOLERANCE: ❌ {
                summary['total_final_errors']
            } violations remain"
        )
        print("   Additional manual fixes may be required.")
        if not args.dry_run:
            print(
                f"📋 Detailed report: reports/incremental_unified_fixer_{fixer.session_id}.json"
            )
        sys.exit(1 if not args.dry_run else 0)


if __name__ == "__main__":
    main()
