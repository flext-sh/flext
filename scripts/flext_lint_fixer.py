#!/usr/bin/env python3
"""FLEXT Automated Linting Fix Script.

Systematically fixes common linting issues across the FLEXT workspace:
- E402: Import ordering issues
- D107: Missing docstrings in __init__ methods
- ARG001/ARG002/ARG003: Unused arguments
- F821: Undefined names that need imports
- EXE002: Executable files without shebang
- D205: Missing blank lines after docstrings

Follows FLEXT workspace standards and CLAUDE.md guidelines.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import TypedDict, cast


class ProjectFixesDict(TypedDict):
    """TypedDict for tracking project-level fix statistics."""

    files_processed: int
    files_modified: int
    fixes: dict[str, int]


class ProjectProcessedDict(TypedDict):
    """TypedDict for tracking processed project information."""

    name: str
    path: str
    stats: ProjectFixesDict


# Core fix patterns
class FlextLintFixer:
    """Automated linting fixes for FLEXT workspace."""

    def __init__(self, workspace_root: Path) -> None:
        """Initialize the fixer with workspace root."""
        self.workspace_root = Path(workspace_root)
        self.fixes_applied = {
            "E402": 0,  # Import ordering
            "D107": 0,  # Missing __init__ docstrings
            "ARG001": 0,  # Unused function args
            "ARG002": 0,  # Unused method args
            "ARG003": 0,  # Unused class args
            "F821": 0,  # Undefined names
            "EXE002": 0,  # Missing shebang
            "D205": 0,  # Missing blank after docstring
        }
        self.projects_processed: list[ProjectProcessedDict] = []
        self.errors_encountered: list[str] = []

    def find_flext_projects(self) -> list[Path]:
        """Find all FLEXT projects in workspace."""
        projects = [
            item
            for item in self.workspace_root.iterdir()
            if item.is_dir()
            and item.name.startswith("flext-")
            and ((item / "src").exists() or any(item.glob("*.py")))
        ]
        return sorted(projects)

    def get_python_files(self, project_path: Path) -> list[Path]:
        """Get all Python files in a project."""
        python_files: list[Path] = []
        for pattern in ["src/**/*.py", "*.py", "tests/**/*.py"]:
            python_files.extend(project_path.glob(pattern))
        return [f for f in python_files if f.is_file()]

    def fix_import_ordering(self, file_path: Path) -> bool:
        """Fix E402 import ordering issues."""
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.splitlines()

            # Find first import line and module docstring end
            first_import_idx = -1
            docstring_end_idx = -1
            in_module_docstring = False

            for i, line in enumerate(lines):
                stripped = line.strip()

                # Track module docstring
                if i < 5 and (stripped.startswith(('"""', "'''"))):
                    if not in_module_docstring:
                        in_module_docstring = True
                        if stripped.count('"""') == 2 or stripped.count("'''") == 2:
                            docstring_end_idx = i
                            in_module_docstring = False
                    else:
                        docstring_end_idx = i
                        in_module_docstring = False

                # Find first import
                if (
                    stripped.startswith(("import ", "from "))
                ) and first_import_idx == -1:
                    first_import_idx = i
                    break

            # Fix: Move imports after __future__ and docstring
            if first_import_idx > 0:
                future_imports: list[str] = []
                regular_imports: list[str] = []
                other_lines: list[str] = []
                # Separate different types of content
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if stripped.startswith("from __future__"):
                        future_imports.append(line)
                    elif stripped.startswith(
                        ("import ", "from "),
                    ) and not stripped.startswith("from __future__"):
                        regular_imports.append(line)
                    elif i <= docstring_end_idx:
                        other_lines.append(line)
                    else:
                        other_lines.append(line)

                # Reconstruct with proper ordering
                new_lines: list[str] = []
                # Add module docstring and metadata
                doc_lines = [
                    line for i, line in enumerate(lines) if i <= docstring_end_idx
                ]
                new_lines.extend(doc_lines)

                # Add __future__ imports
                if future_imports:
                    new_lines.append("")
                    new_lines.extend(future_imports)

                # Add regular imports
                if regular_imports:
                    new_lines.append("")
                    new_lines.extend(regular_imports)

                # Add rest of the file
                rest_lines = [
                    line
                    for i, line in enumerate(lines)
                    if i
                    > max(docstring_end_idx, len(future_imports) + len(regular_imports))
                ]
                if rest_lines:
                    new_lines.append("")
                    new_lines.extend(rest_lines)

                # Write back if changed
                new_content = "\n".join(new_lines) + "\n"
                if new_content != content:
                    file_path.write_text(new_content, encoding="utf-8")
                    self.fixes_applied["E402"] += 1
                    return True

        except Exception as e:
            self.errors_encountered.append(f"E402 fix failed for {file_path}: {e}")

        return False

    def fix_missing_init_docstrings(self, file_path: Path) -> bool:
        """Fix D107 missing docstrings in __init__ methods."""
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.splitlines()
            modified = False

            # Find __init__ methods without docstrings
            i = 0
            while i < len(lines):
                line = lines[i].strip()

                if line.startswith("def __init__("):
                    # Check if next non-empty line is a docstring
                    j = i + 1
                    has_docstring = False

                    while j < len(lines) and not lines[j].strip():
                        j += 1

                    if j < len(lines):
                        next_line = lines[j].strip()
                        if next_line.startswith(('"""', "'''")):
                            has_docstring = True

                    if not has_docstring:
                        # Add docstring after the __init__ line
                        indent = len(lines[i]) - len(lines[i].lstrip())
                        docstring = (
                            " " * (indent + 4) + '"""Initialize the instance."""'
                        )
                        lines.insert(i + 1, docstring)
                        modified = True
                        self.fixes_applied["D107"] += 1

                i += 1

            if modified:
                file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
                return True

        except Exception as e:
            self.errors_encountered.append(f"D107 fix failed for {file_path}: {e}")

        return False

    def fix_unused_arguments(self, file_path: Path) -> bool:
        """Fix ARG001/ARG002/ARG003 unused arguments."""
        try:
            content = file_path.read_text(encoding="utf-8")

            # Use ast to find unused arguments
            tree = ast.parse(content)

            class ArgumentAnalyzer(ast.NodeVisitor):
                def __init__(self) -> None:
                    self.unused_args: list[tuple[int, set[str]]] = []

                def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
                    # Get all argument names
                    arg_names: set[str] = set()
                    if hasattr(node.args, "args") and node.args.args:
                        arg_names.update(arg.arg for arg in node.args.args)

                    # Check for usage in function body
                    used_names = set()
                    for child in ast.walk(node):
                        if isinstance(child, ast.Name) and isinstance(
                            child.ctx,
                            ast.Load,
                        ):
                            used_names.add(child.id)

                    # Find unused arguments (except 'self' and 'cls')
                    unused = arg_names - used_names - {"self", "cls"}
                    if unused:
                        self.unused_args.append((node.lineno, unused))

                    self.generic_visit(node)

            analyzer = ArgumentAnalyzer()
            analyzer.visit(tree)

            # Fix by prefixing with underscore
            lines = content.splitlines()
            modified = False

            for line_no, unused_names in analyzer.unused_args:
                if line_no - 1 < len(lines):
                    line = lines[line_no - 1]
                    for arg_name in unused_names:
                        if (
                            f"{arg_name}:" in line
                            or f"{arg_name}," in line
                            or f"{arg_name})" in line
                        ):
                            lines[line_no - 1] = line.replace(arg_name, f"_{arg_name}")
                            modified = True
                            self.fixes_applied["ARG001"] += 1

            if modified:
                file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
                return True

        except Exception as e:
            self.errors_encountered.append(f"ARG fix failed for {file_path}: {e}")

        return False

    def fix_undefined_names(self, file_path: Path) -> bool:
        """Fix F821 undefined names by adding common imports."""
        try:
            content = file_path.read_text(encoding="utf-8")

            # Common undefined names and their imports
            import_map = {
                "Path": "from pathlib import Path",
                "Dict": "from typing import Dict",
                "List": "from typing import List",
                "Optional": "from typing import Optional",
                "Union": "from typing import Union",
                "Type": "from typing import Type",
                "Callable": "from typing import Callable",
                "Iterator": "from typing import Iterator",
                "Generator": "from typing import Generator",
                "FlextResult": "from flext_core import FlextResult",
                "FlextLogger": "from flext_core import FlextLogger",
                "FlextModels": "from flext_core import FlextModels",
            }

            lines = content.splitlines()
            needed_imports = set()

            # Find undefined names
            for line in lines:
                for name, import_stmt in import_map.items():
                    if (
                        re.search(rf"\b{name}\b", line)
                        and not line.strip().startswith("#")
                        and not any(import_stmt in line_item for line_item in lines)
                    ):
                        needed_imports.add(import_stmt)

            if needed_imports:
                # Find where to insert imports (after existing imports)
                import_insert_idx = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith(("import ", "from ")):
                        import_insert_idx = i + 1

                # Insert new imports
                for import_stmt in sorted(needed_imports):
                    lines.insert(import_insert_idx, import_stmt)
                    import_insert_idx += 1
                    self.fixes_applied["F821"] += 1

                file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
                return True

        except Exception as e:
            self.errors_encountered.append(f"F821 fix failed for {file_path}: {e}")

        return False

    def fix_missing_shebang(self, file_path: Path) -> bool:
        """Fix EXE002 missing shebang in executable files."""
        try:
            # Check if file is executable
            if not os.access(file_path, os.X_OK):
                return False

            content = file_path.read_text(encoding="utf-8")

            if not content.startswith("#!"):
                # Add shebang
                shebang = "#!/usr/bin/env python3\n"
                new_content = shebang + content
                file_path.write_text(new_content, encoding="utf-8")
                self.fixes_applied["EXE002"] += 1
                return True

        except Exception as e:
            self.errors_encountered.append(f"EXE002 fix failed for {file_path}: {e}")

        return False

    def fix_missing_blank_after_docstring(self, file_path: Path) -> bool:
        """Fix D205 missing blank line after docstring."""
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.splitlines()
            modified = False

            i = 0
            while i < len(lines) - 1:
                line = lines[i].strip()

                # Find end of docstring
                if line.endswith(('"""', "'''")):
                    next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""

                    # Add blank line if next line is not empty and not already blank
                    if next_line and not next_line.startswith(('"""', "'''")):
                        lines.insert(i + 1, "")
                        modified = True
                        self.fixes_applied["D205"] += 1
                        i += 1  # Skip the inserted line

                i += 1

            if modified:
                file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
                return True

        except Exception as e:
            self.errors_encountered.append(f"D205 fix failed for {file_path}: {e}")

        return False

    def process_file(self, file_path: Path) -> dict[str, bool]:
        """Process a single Python file with all fixes."""
        return {
            "E402": self.fix_import_ordering(file_path),
            "D107": self.fix_missing_init_docstrings(file_path),
            "ARG001": self.fix_unused_arguments(file_path),
            "F821": self.fix_undefined_names(file_path),
            "EXE002": self.fix_missing_shebang(file_path),
            "D205": self.fix_missing_blank_after_docstring(file_path),
        }

    def process_project(self, project_path: Path) -> ProjectFixesDict:
        """Process all Python files in a project."""
        print(f"\n🔍 Processing project: {project_path.name}")

        python_files = self.get_python_files(project_path)
        project_fixes: ProjectFixesDict = {
            "files_processed": 0,
            "files_modified": 0,
            "fixes": {},
        }

        for fix_type in self.fixes_applied:
            project_fixes["fixes"][fix_type] = 0

        for py_file in python_files:
            try:
                print(f"  📝 {py_file.relative_to(self.workspace_root)}")
                fixes_result = self.process_file(py_file)

                project_fixes["files_processed"] += 1
                if any(fixes_result.values()):
                    project_fixes["files_modified"] += 1

                for fix_type, applied in fixes_result.items():
                    if applied:
                        project_fixes["fixes"][fix_type] += 1

            except Exception as e:
                self.errors_encountered.append(f"Error processing {py_file}: {e}")

        self.projects_processed.append(
            cast(
                "ProjectProcessedDict",
                {
                    "name": project_path.name,
                    "path": str(project_path),
                    "stats": project_fixes,
                },
            ),
        )

        return project_fixes

    def run_validation(self, project_path: Path) -> tuple[bool, str]:
        """Run ruff validation on a project."""
        try:
            result = subprocess.run(
                ["/usr/bin/ruff", "check", str(project_path)],
                check=False,
                capture_output=True,
                shell=False,
                text=True,
                cwd=project_path,
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, f"Validation failed: {e}"

    def generate_report(self) -> str:
        """Generate comprehensive report of all fixes applied."""
        report: list[str] = []
        report.extend(
            (
                "# FLEXT Automated Linting Fix Report",
                f"**Generated**: {Path().cwd()}",
                f"**Workspace**: {self.workspace_root}",
                "",
            ),
        )

        # Summary
        total_fixes = sum(self.fixes_applied.values())
        total_projects = len(self.projects_processed)

        report.extend([
            "## 📊 Summary",
            f"- **Projects processed**: {total_projects}",
            f"- **Total fixes applied**: {total_fixes}",
            "",
            "## 🔧 Fixes Applied",
        ])
        for fix_type, count in self.fixes_applied.items():
            if count > 0:
                description = {
                    "E402": "Import ordering fixes",
                    "D107": "Added __init__ docstrings",
                    "ARG001": "Fixed unused function arguments",
                    "ARG002": "Fixed unused method arguments",
                    "ARG003": "Fixed unused class arguments",
                    "F821": "Added missing imports",
                    "EXE002": "Added shebang to executable files",
                    "D205": "Added blank lines after docstrings",
                }
                report.append(
                    f"- **{fix_type}**: {count} - {description.get(fix_type, 'Unknown fix')}",
                )

        report.extend(["", "## 📁 Project Details"])
        for project in self.projects_processed:
            stats = project["stats"]
            report.extend(
                (
                    f"### {project['name']}",
                    f"- Files processed: {stats['files_processed']}",
                    f"- Files modified: {stats['files_modified']}",
                ),
            )

            for fix_type, count in stats["fixes"].items():
                if count > 0:
                    report.append(f"  - {fix_type}: {count}")
            report.append("")

        # Errors
        if self.errors_encountered:
            report.append("## ⚠️ Errors Encountered")
            report.extend(f"- {error}" for error in self.errors_encountered)
            report.append("")

        report.extend(
            (
                "## 🎯 Next Steps",
                "1. Run `make validate` in each project to verify fixes",
                "2. Run tests to ensure functionality is preserved",
                "3. Commit changes with descriptive messages",
                "4. Consider running additional quality checks",
            ),
        )

        return "\n".join(report)


def main() -> None:
    """Main entry point for the linting fixer."""
    if len(sys.argv) > 1:
        workspace_root = Path(sys.argv[1])
    else:
        workspace_root = (
            Path.cwd().parent if Path.cwd().name.startswith("flext-") else Path.cwd()
        )

    print("🚀 FLEXT Automated Linting Fixer")
    print(f"📂 Workspace: {workspace_root}")
    print("=" * 60)

    fixer = FlextLintFixer(workspace_root)
    projects = fixer.find_flext_projects()

    print(f"Found {len(projects)} FLEXT projects:")
    for project in projects:
        print(f"  - {project.name}")
    print()

    # Process all projects
    for project in projects:
        fixer.process_project(project)

    # Generate and save report
    report = fixer.generate_report()
    report_file = workspace_root / "flext_lint_fix_report.md"
    report_file.write_text(report, encoding="utf-8")

    print("\n" + "=" * 60)
    print("✅ Processing complete!")
    print(f"📊 Total fixes applied: {sum(fixer.fixes_applied.values())}")
    print(f"📋 Report saved to: {report_file}")
    print("\n🔍 Fix Summary:")
    for fix_type, count in fixer.fixes_applied.items():
        if count > 0:
            print(f"  {fix_type}: {count}")


if __name__ == "__main__":
    main()
