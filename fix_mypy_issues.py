#!/usr/bin/env python3
"""
FLEXT MyPy Issues Fix Script

This script systematically fixes common MyPy issues across all FLEXT projects.
"""

import re
import subprocess
from pathlib import Path


class MyPyFixer:
    """Fix common MyPy issues across FLEXT projects."""

    def __init__(self, workspace_root: str = "/home/marlonsc/flext"):
        self.workspace_root = Path(workspace_root)
        self.fixes_applied = []

    def find_python_files(self, project_path: Path) -> list[Path]:
        """Find all Python files in a project."""
        python_files = []
        src_path = project_path / "src"
        if src_path.exists():
            python_files.extend(src_path.rglob("*.py"))
        return python_files

    def fix_typealias_imports(self, file_path: Path) -> bool:
        """Fix TypeAlias import issues for Python version compatibility."""
        try:
            content = file_path.read_text()

            # Check if file has TypeAlias import
            if "from typing import" in content and "TypeAlias" in content:
                # Pattern to match existing TypeAlias import
                pattern = r"from typing import ([^\\n]*TypeAlias[^\\n]*)"

                if re.search(pattern, content):
                    # Replace with version-compatible import
                    new_import = """try:
    from typing import TypeAlias
except ImportError:
    from typing_extensions import TypeAlias

from typing import """

                    # Extract other imports
                    match = re.search(pattern, content)
                    if match:
                        imports = match.group(1)
                        other_imports = imports.replace("TypeAlias", "").strip(", ")
                        if other_imports:
                            new_import += other_imports
                        else:
                            new_import = new_import.rstrip("from typing import ")

                        content = re.sub(pattern, new_import, content)
                        file_path.write_text(content)
                        self.fixes_applied.append(
                            f"Fixed TypeAlias import in {file_path}"
                        )
                        return True
        except Exception:
            pass
        return False

    def fix_missing_return_annotations(self, file_path: Path) -> bool:
        """Fix missing return type annotations for __post_init__ and other methods."""
        try:
            content = file_path.read_text()

            # Fix __post_init__ methods
            pattern = r"def __post_init__\\(self\\):"
            if re.search(pattern, content):
                content = re.sub(pattern, r"def __post_init__(self) -> None:", content)
                file_path.write_text(content)
                self.fixes_applied.append(
                    f"Fixed __post_init__ return annotation in {file_path}"
                )
                return True
        except Exception:
            pass
        return False

    def fix_generic_type_parameters(self, file_path: Path) -> bool:
        """Fix missing generic type parameters for dict and list."""
        try:
            content = file_path.read_text()
            changes_made = False

            # Fix dict without type parameters in annotations
            patterns = [
                (r": dict = \\{\\}", r": dict[str, Any] = {}"),
                (r": dict = None", r": dict[str, Any] = None"),
                (r": list = \\[\\]", r": list[Any] = []"),
                (r": list = None", r": list[Any] = None"),
            ]

            for pattern, replacement in patterns:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    changes_made = True

            if changes_made:
                # Ensure Any is imported
                if "from typing import" in content and "Any" not in content:
                    content = re.sub(
                        r"from typing import ([^\\n]*)",
                        r"from typing import \\1, Any",
                        content,
                    )

                file_path.write_text(content)
                self.fixes_applied.append(
                    f"Fixed generic type parameters in {file_path}"
                )
                return True
        except Exception:
            pass
        return False

    def fix_unused_type_ignores(self, file_path: Path) -> bool:
        """Remove unused type: ignore comments."""
        try:
            content = file_path.read_text()

            # Common unused type ignore patterns
            patterns = [
                r"  # type: ignore\[no-untyped-call\]",
                r"  # type: ignore\[unused-ignore\]",
            ]

            changes_made = False
            for pattern in patterns:
                if re.search(pattern, content):
                    content = re.sub(pattern, "", content)
                    changes_made = True

            if changes_made:
                file_path.write_text(content)
                self.fixes_applied.append(f"Removed unused type ignores in {file_path}")
                return True
        except Exception:
            pass
        return False

    def fix_project(self, project_name: str) -> None:
        """Fix MyPy issues in a specific project."""
        project_path = self.workspace_root / project_name
        if not project_path.exists():
            return

        python_files = self.find_python_files(project_path)

        for file_path in python_files:
            self.fix_typealias_imports(file_path)
            self.fix_missing_return_annotations(file_path)
            self.fix_generic_type_parameters(file_path)
            self.fix_unused_type_ignores(file_path)

    def run_mypy_check(self, project_name: str) -> tuple[bool, str]:
        """Run MyPy on a project and return success status and output."""
        project_path = self.workspace_root / project_name
        try:
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "mypy",
                    "src/",
                    "--ignore-missing-imports",
                    "--no-strict-optional",
                ],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=60,
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "MyPy check timed out"
        except Exception as e:
            return False, f"Error running MyPy: {e}"

    def generate_report(self) -> str:
        """Generate a comprehensive report of all fixes applied."""
        report = [
            "# FLEXT MyPy Fixes Report",
            f"Total fixes applied: {len(self.fixes_applied)}\\n",
            "## Fixes Applied:",
        ]

        for fix in self.fixes_applied:
            report.append(f"- {fix}")

        return "\\n".join(report)


def main():
    """Main execution function."""
    fixer = MyPyFixer()

    # List of FLEXT projects to fix
    projects = [
        "flext-ldap",
        "flext-tap-ldap",
        "flext-target-ldap",
        "flext-db-oracle",
        "flext-plugin",
        "flext-core",
        "flext-api",
        "flext-auth",
        "flext-cli",
        "flext-web",
        "flext-grpc",
        "flext-meltano",
        "flext-observability",
        "flext-tap-oracle-oic",
        "flext-tap-oracle-wms",
        "flext-target-oracle-oic",
        "flext-target-oracle-wms",
        "flext-oracle-oic-ext",
        "flext-dbt-ldap",
    ]

    for project in projects:
        fixer.fix_project(project)

    # Generate and save report
    report = fixer.generate_report()
    report_path = Path("/home/marlonsc/flext/mypy_fixes_report.md")
    report_path.write_text(report)


if __name__ == "__main__":
    main()
