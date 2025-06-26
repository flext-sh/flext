#!/usr/bin/env python3
"""TARGETED ZERO TOLERANCE FIX SCRIPT
Focuses on fixing the most critical violations systematically.
"""

import ast
import logging
import re
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class TargetedFixer:
    """Targeted fixer for critical violations."""

    def __init__(self, base_path: str = "/home/marlonsc/pyauto"):
        self.base_path: Path = Path(base_path)
        self.fixes_applied: int = 0
        self.files_modified: set = set()

    def find_all_python_files(self) -> list[Path]:
        """Find all Python files in the workspace."""
        python_files: list[Path] = []
        for pattern in ["*.py", "**/*.py"]:
            python_files.extend(self.base_path.glob(pattern))
        return python_files

    def fix_print_statements_in_file(self, file_path: Path) -> bool:
        """Fix print statements in a single file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Skip test files
            if "test" in str(file_path).lower() or str(file_path).startswith(
                str(self.base_path / "tests"),
            ):
                return False

            lines = content.split("\n")
            modified = False

            # Check if logging is already imported
            has_logging = (
                "import logging" in content or "from loguru import logger" in content
            )

            new_lines: list[str] = []
            added_imports: bool = False

            for i, line in enumerate(lines):
                # Skip if it's already a logger call
                if "logger." in line or line.strip().startswith("#"):
                    new_lines.append(line)
                    continue

                # Find print statements
                if re.search(r"\bprint\s*\(", line):
                    # Extract indentation
                    indent = len(line) - len(line.lstrip())
                    indent_str = " " * indent

                    # Extract print content
                    print_match = re.search(r"print\s*\((.*?)\)\s*(?:#.*)?$", line)
                    if print_match:
                        content_inside = print_match.group(1).strip()

                        # Add imports if needed
                        if not has_logging and not added_imports:
                            # Find where to add imports
                            import_idx = 0
                            for j, l in enumerate(lines[:i]):
                                if l.strip().startswith(
                                    "import ",
                                ) or l.strip().startswith("from "):
                                    import_idx = j + 1
                                elif (
                                    import_idx > 0
                                    and l.strip()
                                    and not l.strip().startswith("import")
                                    and not l.strip().startswith("from")
                                ):
                                    break

                            # Add imports at the right position
                            if import_idx == 0:
                                # No imports found, add after module docstring
                                for j, l in enumerate(lines):
                                    if j < 3 and (
                                        l.strip().startswith('"""')
                                        or l.strip().startswith("'''")
                                    ):
                                        # Find end of docstring
                                        for k in range(j + 1, len(lines)):
                                            if lines[k].strip().endswith(
                                                '"""',
                                            ) or lines[k].strip().endswith("'''"):
                                                import_idx = k + 1
                                                break
                                        break

                            # Insert imports
                            new_lines.insert(import_idx, "")
                            new_lines.insert(import_idx + 1, "import logging")
                            new_lines.insert(import_idx + 2, "")
                            new_lines.insert(
                                import_idx + 3,
                                "logger = logging.getLogger(__name__)",
                            )
                            new_lines.insert(import_idx + 4, "")
                            added_imports = True
                            has_logging = True

                        # Convert print to logger
                        if content_inside:
                            new_line = f"{indent_str}logger.info({content_inside})"
                            new_line = f'{indent_str}logger.info("")'

                        new_lines.append(new_line)
                        modified = True
                        self.fixes_applied += 1
                        new_lines.append(line)
                    new_lines.append(line)

            if modified:
                # Write back
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(new_lines))
                self.files_modified.add(file_path)
                return True

            return False

        except Exception as e:
            logger.error(f"Error fixing {file_path}: {e}")
            return False

    def fix_undefined_names_in_file(self, file_path: Path) -> bool:
        """Fix undefined names in a single file using AST analysis."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Parse with AST to find undefined names
            try:
                tree = ast.parse(content)
            except SyntaxError:
                # Can't parse, skip
                return False

            # Common undefined names and their imports
            common_imports = {
                "Path": "from pathlib import Path",
                "datetime": "from datetime import datetime",
                "logger": "import logging\n\nlogger = logging.getLogger(__name__)",
            }

            # Find all names used
            class NameCollector(ast.NodeVisitor):
                def __init__(self) -> None:
                    self.names: set[str] = set()
                    self.defined: set[str] = set()

                def visit_name(self, node: ast.Name) -> None:
                    if isinstance(node.ctx, ast.Load):
                        self.names.add(node.id)
                    elif isinstance(node.ctx, ast.Store):
                        self.defined.add(node.id)
                    self.generic_visit(node)

                def visit_function_def(self, node: ast.FunctionDef) -> None:
                    self.defined.add(node.name)
                    self.generic_visit(node)

                def visit_class_def(self, node: ast.ClassDef) -> None:
                    self.defined.add(node.name)
                    self.generic_visit(node)

                def visit_import(self, node: ast.Import) -> None:
                    for alias in node.names:
                        self.defined.add(alias.asname or alias.name)
                    self.generic_visit(node)

                def visit_import_from(self, node: ast.ImportFrom) -> None:
                    for alias in node.names:
                        self.defined.add(alias.asname or alias.name)
                    self.generic_visit(node)

            collector = NameCollector()
            collector.visit(tree)

            # Find undefined names
            undefined = collector.names - collector.defined - set(dir(__builtins__))

            # Filter to only common undefined names we can fix
            to_import: set = set()
            for name in undefined:
                if name in common_imports:
                    to_import.add(name)

            if not to_import:
                return False

            # Add imports
            lines = content.split("\n")
            import_lines: list = []

            # Group typing imports
            typing_imports: list = []
            other_imports: list = []

            for name in to_import:
                import_stmt = common_imports[name]
                if import_stmt.startswith("from typing"):
                    typing_imports.append(name)
                else:
                    other_imports.append(import_stmt)

            # Create consolidated typing import
            if typing_imports:
                typing_import = f"from typing import {', '.join(typing_imports)}"
                import_lines.append(typing_import)

            import_lines.extend(other_imports)

            # Find where to insert imports
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.strip().startswith("import ") or line.strip().startswith(
                    "from ",
                ):
                    insert_idx = i + 1
                elif (
                    insert_idx > 0
                    and line.strip()
                    and not line.strip().startswith("import")
                    and not line.strip().startswith("from")
                ):
                    break

            # Insert imports
            for import_line in import_lines:
                lines.insert(insert_idx, import_line)
                insert_idx += 1
                self.fixes_applied += 1

            # Write back
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

            self.files_modified.add(file_path)
            return True

        except Exception as e:
            logger.error(f"Error fixing undefined names in {file_path}: {e}")
            return False

    def run_ruff_fix(self) -> None:
        """Run ruff with automatic fixes."""
        logger.info("Running ruff automatic fixes...")

        # Run ruff with all automatic fixes
        result = subprocess.run(
            ["ruff", "check", "--fix", "--unsafe-fixes", str(self.base_path)],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            logger.info("Ruff fixes applied successfully")
            logger.warning(f"Ruff fixes completed with warnings: {result.stderr}")

    def run_black(self) -> None:
        """Run black formatter."""
        logger.info("Running black formatter...")

        result = subprocess.run(
            ["black", "--quiet", str(self.base_path)],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            logger.info("Black formatting completed")
            logger.warning(f"Black formatting had issues: {result.stderr}")

    def run_isort(self) -> None:
        """Run isort to fix imports."""
        logger.info("Running isort...")

        result = subprocess.run(
            ["isort", "--quiet", str(self.base_path)],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            logger.info("Import sorting completed")
            logger.warning(f"Import sorting had issues: {result.stderr}")

    def check_violations(self) -> dict[str, int]:
        """Check current violations."""
        logger.info("Checking current violations...")

        # Count print statements
        print_count = 0
        result = subprocess.run(
            [
                "grep",
                "-r",
                "print(",
                str(self.base_path),
                "--include=*.py",
                "--exclude-dir=.git",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            print_count = len([l for l in result.stdout.split("\n") if l.strip()])

        # Run ruff check
        result = subprocess.run(
            ["ruff", "check", str(self.base_path), "--statistics"],
            capture_output=True,
            text=True,
            check=False,
        )

        # Parse statistics
        stats: dict = {}
        total_violations = 0

        for line in result.stdout.split("\n"):
            if line.strip():
                parts = line.strip().split()
                if (
                    len(parts) >= 2
                    and parts[1].startswith("(")
                    and parts[1].endswith(")")
                ):
                    count = int(parts[0])
                    code = parts[1][1:-1]
                    stats[code] = count
                    total_violations += count

        return {
            "print_statements": print_count,
            "total_violations": total_violations,
            "undefined_names": stats.get("F821", 0),
            "stats": stats,
        }

    def run(self) -> None:
        """Run the targeted fix process."""
        logger.info("=" * 80)
        logger.info("TARGETED ZERO TOLERANCE FIX")
        logger.info("=" * 80)

        # Initial check
        initial_stats = self.check_violations()
        logger.info("Initial violations:")
        logger.info(f"  - Print statements: {initial_stats['print_statements']}")
        logger.info(f"  - Undefined names (F821): {initial_stats['undefined_names']}")
        logger.info(f"  - Total violations: {initial_stats['total_violations']}")

        # Phase 1: Fix print statements
        logger.info("\nPhase 1: Fixing print statements...")
        python_files = self.find_all_python_files()

        for file_path in python_files:
            # Skip test files and scripts
            if "test" in str(file_path).lower() or "/scripts/" in str(file_path):
                continue

            self.fix_print_statements_in_file(file_path)

        logger.info(f"Fixed {self.fixes_applied} print statements")

        # Phase 2: Fix undefined names
        logger.info("\nPhase 2: Fixing undefined names...")
        fixes_before = self.fixes_applied

        for file_path in python_files:
            self.fix_undefined_names_in_file(file_path)

        logger.info(f"Fixed {self.fixes_applied - fixes_before} undefined names")

        # Phase 3: Run automatic tools
        logger.info("\nPhase 3: Running automatic formatting tools...")
        self.run_isort()
        self.run_black()
        self.run_ruff_fix()

        # Final check
        final_stats = self.check_violations()
        logger.info("\n" + "=" * 80)
        logger.info("FINAL REPORT")
        logger.info("=" * 80)
        logger.info(
            f"Print statements: {initial_stats['print_statements']} → {final_stats['print_statements']}",
        )
        logger.info(
            f"Undefined names: {initial_stats['undefined_names']} → {final_stats['undefined_names']}",
        )
        logger.info(
            f"Total violations: {initial_stats['total_violations']} → {final_stats['total_violations']}",
        )
        logger.info(f"Files modified: {len(self.files_modified)}")
        logger.info(f"Total fixes applied: {self.fixes_applied}")

        # Show top remaining violations
        if final_stats["stats"]:
            logger.info("\nTop remaining violations:")
            sorted_stats = sorted(
                final_stats["stats"].items(),
                key=lambda x: x[1],
                reverse=True,
            )
            for code, count in sorted_stats[:10]:
                logger.info(f"  - {code}: {count}")

        if final_stats["total_violations"] == 0:
            logger.info("\n✅ ZERO TOLERANCE ACHIEVED!")
            logger.info(f"\n❌ {final_stats['total_violations']} violations remain")

            # Show sample violations
            result = subprocess.run(
                ["ruff", "check", str(self.base_path), "--output-format", "concise"],
                capture_output=True,
                text=True,
                check=False,
            )

            logger.info("\nSample violations:")
            for _i, line in enumerate(result.stdout.split("\n")[:20]):
                if line.strip():
                    logger.info(f"  {line}")


if __name__ == "__main__":
    fixer = TargetedFixer()
    fixer.run()
