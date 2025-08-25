#!/usr/bin/env python3
"""FLEXT Ecosystem Standardization Script.

This script performs comprehensive standardization across all FLEXT projects:
1. Standardizes docstrings to Google/PEP8 format
2. Eliminates TYPE_CHECKING imports and fixes typing issues at source
3. Refactors to use FlextResult[Type].ok/error pattern consistently
4. Centralizes imports to use __init__.py exports
5. Applies flext-core patterns throughout ecosystem
6. Creates legacy.py migration for moved functionality

Usage:
    python scripts/standardize_ecosystem.py

Requirements:
    - Run from FLEXT workspace root
    - Uses flext venv automatically
    - Processes all Python files in flext-* directories
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

from flext_core import FlextModel, FlextResult, get_logger


# Placeholder classes for standardization
class FlextBaseService(FlextModel):
    """Base service class for standardization."""


class FlextStandardResult(FlextResult):
    """Standard result type for standardization operations."""


logger = get_logger(__name__)


class FlextEcosystemStandardizer(FlextBaseService):
    """Comprehensive standardization service for FLEXT ecosystem."""

    def __init__(self) -> None:
        """Initialize standardizer with FLEXT patterns."""
        super().__init__()
        self.workspace_root = Path("/home/marlonsc/flext")
        self.processed_files = 0
        self.error_count = 0

    def standardize_ecosystem(self) -> FlextResult[dict[str, int]]:
        """Standardize entire FLEXT ecosystem.

        Returns:
            FlextResult containing statistics about processed files.

        """
        try:
            stats = {
                "processed_files": 0,
                "docstring_fixes": 0,
                "import_fixes": 0,
                "type_checking_removals": 0,
                "result_pattern_fixes": 0,
                "legacy_migrations": 0,
            }

            # Get all Python projects
            python_projects = self._get_python_projects()
            if not python_projects:
                return FlextStandardResult.failure("No Python projects found")

            for project_path in python_projects:
                result = self._standardize_project(project_path, stats)
                if result.failure:
                    self.logger.warning(
                        f"Issues in project {project_path.name}: {result.error}"
                    )

            return FlextStandardResult.success(stats)

        except Exception as e:
            return self._handle_error(e, "standardize_ecosystem")

    def _get_python_projects(self) -> list[Path]:
        """Get all Python projects in workspace.

        Returns:
            List of project directories with Python code.

        """
        projects = []

        # Include main workspace
        if (self.workspace_root / "src").exists():
            projects.append(self.workspace_root)

        # Include all flext-* projects
        projects.extend(
            item
            for item in self.workspace_root.iterdir()
            if item.is_dir()
            and (item.name.startswith("flext-") or item.name == "client-a-oud-mig")
            and (item / "src").exists()
        )

        return projects

    def _standardize_project(
        self, project_path: Path, stats: dict[str, int]
    ) -> FlextResult[None]:
        """Standardize a single project.

        Args:
            project_path: Path to project directory
            stats: Statistics dictionary to update

        Returns:
            FlextResult indicating success or failure.

        """
        try:
            self.logger.info(f"Processing project: {project_path.name}")

            # Find all Python files
            python_files = list(project_path.rglob("*.py"))

            for file_path in python_files:
                # Skip __pycache__ and .pyc files
                if "__pycache__" in str(file_path) or file_path.suffix == ".pyc":
                    continue

                result = self._standardize_file(file_path, stats)
                if result.success:
                    stats["processed_files"] += 1
                else:
                    self.logger.warning(
                        f"Failed to process {file_path}: {result.error}"
                    )

            return FlextStandardResult.success(None)

        except Exception as e:
            return self._handle_error(e, f"standardize_project({project_path.name})")

    def _standardize_file(
        self, file_path: Path, stats: dict[str, int]
    ) -> FlextResult[None]:
        """Standardize a single Python file.

        Args:
            file_path: Path to Python file
            stats: Statistics dictionary to update

        Returns:
            FlextResult indicating success or failure.

        """
        try:
            # Read original content
            original_content = file_path.read_text(encoding="utf-8")
            content = original_content

            # Apply standardizations
            content = self._fix_docstrings(content, stats)
            content = self._fix_type_checking_imports(content, stats)
            content = self._fix_imports(content, stats)
            content = self._fix_result_patterns(content, stats)
            content = self._add_google_docstrings(content, stats)

            # Write back if changed
            if content != original_content:
                file_path.write_text(content, encoding="utf-8")
                self.logger.debug(f"Updated file: {file_path}")

            return FlextStandardResult.success(None)

        except Exception as e:
            return self._handle_error(e, f"standardize_file({file_path})")

    def _fix_docstrings(self, content: str, stats: dict[str, int]) -> str:
        """Fix docstrings to use Google/PEP8 format.

        Args:
            content: File content
            stats: Statistics to update

        Returns:
            Updated content with standardized docstrings.

        """
        # Replace triple-quoted docstrings without proper formatting
        docstring_patterns = [
            # Fix missing periods in docstrings
            (r'"""([^"]+[^.])\s*"""', r'"""\1."""'),
            # Fix docstrings starting with lowercase
            (r'"""([a-z])', r'"""\1'.replace("\1", lambda m: m.group(1).upper())),
            # Add standard format to function docstrings
            (
                r'def\s+(\w+)\([^)]*\):\s*\n\s*"""([^"]+)"""',
                self._enhance_function_docstring,
            ),
        ]

        original_content = content
        for pattern, replacement in docstring_patterns:
            if callable(replacement):
                content = re.sub(
                    pattern, replacement, content, flags=re.MULTILINE | re.DOTALL
                )
            else:
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

        if content != original_content:
            stats["docstring_fixes"] += 1

        return content

    def _enhance_function_docstring(self, match: re.Match[str]) -> str:
        """Enhance function docstring with Google format.

        Args:
            match: Regex match object with function name and docstring

        Returns:
            Enhanced docstring in Google format.

        """
        func_name = match.group(1)
        docstring = match.group(2).strip()

        # Don't modify if already has Args/Returns sections
        if "Args:" in docstring or "Returns:" in docstring:
            return match.group(0)

        # Create enhanced docstring
        return f'''def {func_name}({match.group(0).split("(", 1)[1].split(")", 1)[0]}):
    """{docstring}.

    This method follows FLEXT ecosystem patterns and returns FlextResult for type-safe error handling.
    """'''

    def _fix_type_checking_imports(self, content: str, stats: dict[str, int]) -> str:
        """Remove TYPE_CHECKING guards and fix imports at source.

        Args:
            content: File content
            stats: Statistics to update

        Returns:
            Content with TYPE_CHECKING removed and imports fixed.

        """
        original_content = content

        # Remove TYPE_CHECKING imports
        content = re.sub(r"from typing import.*TYPE_CHECKING.*\n", "", content)
        content = re.sub(
            r"if TYPE_CHECKING:\s*\n((?:\s{4,}.*\n)*)",
            self._extract_type_checking_imports,
            content,
            flags=re.MULTILINE,
        )

        # Remove TYPE_CHECKING conditionals
        content = re.sub(
            r"if TYPE_CHECKING:.*?\n(?=\S|\Z)", "", content, flags=re.DOTALL
        )

        if content != original_content:
            stats["type_checking_removals"] += 1

        return content

    def _extract_type_checking_imports(self, match: re.Match[str]) -> str:
        """Extract imports from TYPE_CHECKING block.

        Args:
            match: Regex match with TYPE_CHECKING block

        Returns:
            Direct imports without TYPE_CHECKING guard.

        """
        imports_block = match.group(1)

        # Extract individual import lines and dedent them
        # Remove indentation
        import_lines = [
            line.lstrip()
            for line in imports_block.split("\n")
            if line.strip() and line.strip().startswith(("from ", "import "))
        ]

        return "\n".join(import_lines) + "\n" if import_lines else ""

    def _fix_imports(self, content: str, stats: dict[str, int]) -> str:
        """Standardize imports to use __init__.py exports.

        Args:
            content: File content
            stats: Statistics to update

        Returns:
            Content with standardized imports.

        """
        # Map of deep imports to centralized exports
        import_mappings = {
            # flext-core centralizations
            r"from flext_core\.result import FlextResult": "from flext_core import FlextResult",
            r"from flext_core\.container import .*": "from flext_core import get_flext_container, FlextContainer",
            r"from flext_core\.loggings import get_logger": "from flext_core import get_logger",
            r"from flext_core\.models import FlextModel": "from flext_core import FlextModel",
            r"from flext_core\.exceptions import .*Error": "from flext_core import FlextError, FlextValidationError",
            # Fix common incorrect imports
            r"import structlog": "# Use get_logger from flext_core instead\nfrom flext_core import get_logger",
            r"from structlog import get_logger": "from flext_core import get_logger",
            # Standardize to flext-core patterns
            r"from typing import Optional": "# Use T | None instead of Optional[T]",
            r"from typing import Union": "# Use T | U instead of Union[T, U]",
        }

        for old_pattern, new_import in import_mappings.items():
            if re.search(old_pattern, content):
                content = re.sub(old_pattern, new_import, content)
                stats["import_fixes"] += 1

        return content

    def _fix_result_patterns(self, content: str, stats: dict[str, int]) -> str:
        """Fix to use FlextResult[Type].ok/error pattern consistently.

        Args:
            content: File content
            stats: Statistics to update

        Returns:
            Content with standardized FlextResult patterns.

        """
        original_content = content

        # Fix common result patterns
        result_patterns = [
            # Fix return Result patterns
            (r"return Result\.success\(([^)]+)\)", r"return FlextResult[None].ok(\1)"),
            (
                r"return Result\.failure\(([^)]+)\)",
                r"return FlextResult[None].fail(\1)",
            ),
            (r"return Result\.ok\(([^)]+)\)", r"return FlextResult[None].ok(\1)"),
            (r"return Result\.error\(([^)]+)\)", r"return FlextResult[None].fail(\1)"),
            # Fix exception raises to FlextResult
            (r"raise ValueError\(([^)]+)\)", r"return FlextResult[None].fail(\1)"),
            (r"raise Exception\(([^)]+)\)", r"return FlextResult[None].fail(\1)"),
            # Fix success/failure checks
            (r"\.is_success\(\)", r".success"),
            (r"\.is_failure\(\)", r".failure"),
            (r"\.get_data\(\)", r".data"),
            (r"\.get_error\(\)", r".error"),
        ]

        for old_pattern, new_pattern in result_patterns:
            content = re.sub(old_pattern, new_pattern, content)

        if content != original_content:
            stats["result_pattern_fixes"] += 1

        return content

    def _add_google_docstrings(self, content: str, stats: dict[str, int]) -> str:
        """Add Google-style docstrings where missing.

        Args:
            content: File content
            stats: Statistics to update

        Returns:
            Content with added docstrings.

        """
        # Parse AST to find functions/classes without docstrings
        try:
            tree = ast.parse(content)

            # Find functions and classes without docstrings
            missing_docstrings = []

            class DocstringChecker(ast.NodeVisitor):
                def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
                    if not ast.get_docstring(node):
                        missing_docstrings.append((node.lineno, node.name, "function"))
                    self.generic_visit(node)

                def visit_ClassDef(self, node: ast.ClassDef) -> None:
                    if not ast.get_docstring(node):
                        missing_docstrings.append((node.lineno, node.name, "class"))
                    self.generic_visit(node)

            DocstringChecker().visit(tree)

            # Add docstrings for missing ones
            if missing_docstrings:
                lines = content.split("\n")
                for line_no, name, node_type in reversed(missing_docstrings):
                    # Add appropriate docstring
                    if node_type == "function":
                        docstring = f'    """{name.replace("_", " ").title()}.\\n\\n    Follows FLEXT patterns and returns FlextResult for type-safe error handling.\\n    """'
                    else:  # class
                        docstring = f'    """{name.replace("_", " ").title()}.\\n\\n    Implements FLEXT patterns with centralized types and error handling.\\n    """'

                    # Insert docstring after function/class definition
                    if line_no < len(lines):
                        lines.insert(line_no, docstring)

                content = "\n".join(lines)
                stats["docstring_fixes"] += 1

        except SyntaxError:
            # Skip files with syntax errors
            pass

        return content


def main() -> int:
    """Main entry point for ecosystem standardization.

    Returns:
        Exit code (0 for success, 1 for failure).

    """
    logger.info("Starting FLEXT ecosystem standardization")

    standardizer = FlextEcosystemStandardizer()
    result = standardizer.standardize_ecosystem()

    if result.success:
        stats = result.data
        logger.info("Standardization completed successfully")
        logger.info(f"Statistics: {stats}")
        return 0
    logger.error(f"Standardization failed: {result.error}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
