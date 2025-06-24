#!/usr/bin/env python3
"""Fix all undefined names with ZERO tolerance."""

import logging
import re
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class UndefinedNamesFixer:
    """Fix all undefined names systematically."""

    def __init__(self, base_path: str = "/home/marlonsc/pyauto"):
        self.base_path = Path(base_path)
        self.fixes_applied = 0

    def fix_exception_variables(self) -> None:
        """Fix undefined exception variables (most common F821)."""
        logger.info("Fixing undefined exception variables...")

        for py_file in self.base_path.rglob("*.py"):
            if any(
                part in str(py_file)
                for part in [".venv", "reference", "legacy-", "backup_", "archive"]
            ):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                original = content

                # Fix "except Exception:" followed by "from e" or "raise ... from e"
                # Pattern: except Exception: ... raise ... from e
                content = re.sub(
                    r"except\s+(\w+Exception[^:]*):([^}]+?)from\s+e",
                    r"except \1 as e:\2from e",
                    content,
                    flags=re.DOTALL,
                )

                # Fix "except ImportError as e:" followed by "from e"
                content = re.sub(
                    r"except\s+(ImportError|ValueError|TypeError|AttributeError):([^}]+?)from\s+e",
                    r"except \1 as e:\2from e",
                    content,
                    flags=re.DOTALL,
                )

                if content != original:
                    with open(py_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    self.fixes_applied += 1
                    logger.info("Fixed exception variables in %s", py_file)

            except Exception as e:
                logger.error("Error fixing %s: %s", py_file, e)

    def add_missing_imports(self) -> None:
        """Add missing imports for common undefined names."""
        logger.info("Adding missing imports...")

        for py_file in self.base_path.rglob("*.py"):
            if any(
                part in str(py_file)
                for part in [".venv", "reference", "legacy-", "backup_", "archive"]
            ):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                original = content

                # Check for common undefined names and add imports
                imports_to_add: list = []

                if (
                    "Optional" in content
                    and "Optional" not in content.split("import")[0]
                    if "import" in content
                    else True
                ):
                    imports_to_add.append("from typing import Optional")

                if (
                    "Dict" in content and "Dict" not in content.split("import")[0]
                    if "import" in content
                    else True
                ):
                    imports_to_add.append("from typing import Dict")

                if (
                    "List" in content and "List" not in content.split("import")[0]
                    if "import" in content
                    else True
                ):
                    imports_to_add.append("from typing import List")

                # Add imports at the top after existing imports
                if imports_to_add:
                    lines = content.split("\n")

                    # Find where to insert imports
                    insert_idx = 0
                    for i, line in enumerate(lines):
                        if line.strip().startswith("from ") or line.strip().startswith(
                            "import "
                        ):
                            insert_idx = i + 1
                        elif (
                            insert_idx > 0
                            and line.strip()
                            and not line.strip().startswith("from")
                            and not line.strip().startswith("import")
                        ):
                            break

                    # Insert new imports
                    for import_stmt in imports_to_add:
                        lines.insert(insert_idx, import_stmt)
                        insert_idx += 1

                    content = "\n".join(lines)

                if content != original:
                    with open(py_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    self.fixes_applied += 1
                    logger.info("Added imports to %s", py_file)

            except Exception as e:
                logger.error("Error adding imports to %s: %s", py_file, e)

    def fix_loop_variable_errors(self) -> None:
        """Fix undefined loop variables."""
        logger.info("Fixing undefined loop variables...")

        for py_file in self.base_path.rglob("*.py"):
            if any(
                part in str(py_file)
                for part in [".venv", "reference", "legacy-", "backup_", "archive"]
            ):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                original = content

                # Fix "for functions in data.values():" where file_path is used
                content = re.sub(
                    r"for\s+(\w+)\s+in\s+data\.values\(\):\s*\n(\s+).*rel_path.*Path\(file_path\)",
                    r"for file_path, \1 in data.items():\n\2rel_path = self._get_relative_path(Path(file_path))",
                    content,
                    flags=re.MULTILINE,
                )

                # Fix "for value in backend_data.values():" where key is used
                content = re.sub(
                    r"for\s+(\w+)\s+in\s+(\w+)\.values\(\):\s*\n(\s+).*if\s+key\s+!=",
                    r"for key, \1 in \2.items():\n\3if key !=",
                    content,
                    flags=re.MULTILINE,
                )

                if content != original:
                    with open(py_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    self.fixes_applied += 1
                    logger.info("Fixed loop variables in %s", py_file)

            except Exception as e:
                logger.error("Error fixing loop variables in %s: %s", py_file, e)

    def run(self) -> None:
        """Run all undefined name fixes."""
        logger.info("=" * 80)
        logger.info("FIXING ALL UNDEFINED NAMES - ZERO TOLERANCE")
        logger.info("=" * 80)

        # Apply all fixes
        self.fix_exception_variables()
        self.add_missing_imports()
        self.fix_loop_variable_errors()

        logger.info("\n✅ Total fixes applied: %s", self.fixes_applied)
        logger.info("Undefined names fix completed!")


if __name__ == "__main__":
    fixer = UndefinedNamesFixer()
    fixer.run()
