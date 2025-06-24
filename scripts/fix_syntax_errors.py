#!/usr/bin/env python3
"""Fix critical syntax errors that prevent parsing."""

import logging
import subprocess
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SyntaxErrorFixer:
    """Fix critical syntax errors."""

    def __init__(self, base_path: str = "/home/marlonsc/pyauto"):
        self.base_path = Path(base_path)
        self.fixes_applied = 0
        self.files_modified = set()

    def fix_broken_imports(self) -> None:
        """Fix broken import statements."""
        logger.info("Fixing broken import statements...")

        for py_file in self.base_path.rglob("*.py"):
            if any(
                part in str(py_file)
                for part in [".venv", "reference", "legacy-", "backup_", "archive"]
            ):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                lines = content.split("\n")
                fixed_lines = []

                i = 0
                while i < len(lines):
                    line = lines[i]

                    # Fix broken import statements
                    if (
                        line.strip().startswith("from ")
                        and "(" in line
                        and ")" not in line
                    ):
                        # Multi-line import that got corrupted
                        import_lines = [line]
                        j = i + 1
                        while j < len(lines) and ")" not in lines[j]:
                            import_lines.append(lines[j])
                            j += 1
                        if j < len(lines):
                            import_lines.append(lines[j])

                        # Check if typing import got mixed in
                        fixed_import = self._fix_corrupted_import(import_lines)
                        if fixed_import:
                            fixed_lines.extend(fixed_import)
                            i = j + 1
                            self.fixes_applied += 1
                            continue

                    # Fix hanging else/if statements
                    elif line.strip() in ["else:", "if:"] and i > 0:
                        # Remove orphaned else/if
                        i += 1
                        self.fixes_applied += 1
                        continue

                    fixed_lines.append(line)
                    i += 1

                if fixed_lines != lines:
                    with open(py_file, "w", encoding="utf-8") as f:
                        f.write("\n".join(fixed_lines))
                    self.files_modified.add(py_file)
                    logger.info("Fixed syntax errors in %s", py_file)

            except Exception as e:
                logger.error("Error fixing %s: %s", py_file, e)

    def _fix_corrupted_import(self, import_lines: list[str]) -> list[str] | None:
        """Fix corrupted multi-line import."""
        try:
            # Join all lines
            full_import = " ".join(line.strip() for line in import_lines)

            # Check if typing import got mixed in
            if (
                "from typing import" in full_import
                and "from " in full_import
                and " import (" in full_import
            ):
                # Extract the original import
                if " import (" in full_import:
                    parts = full_import.split(" import (")
                    if len(parts) >= 2:
                        module = (
                            parts[0]
                            .replace("from typing import List, Dict, Optional, Any", "")
                            .strip()
                        )
                        if module.startswith("from "):
                            imports = parts[1].split(")")[0].strip()
                            if imports:
                                # Reconstruct the import
                                return [f"{module} import (", f"    {imports}", ")"]

            return None
        except Exception:
            return None

    def fix_incomplete_files(self) -> None:
        """Fix files that end without proper closure."""
        logger.info("Fixing incomplete files...")

        for py_file in self.base_path.rglob("*.py"):
            if any(
                part in str(py_file)
                for part in [".venv", "reference", "legacy-", "backup_", "archive"]
            ):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                if not content.strip():
                    continue

                # Add missing newline at end
                if not content.endswith("\n"):
                    content += "\n"

                    with open(py_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    self.fixes_applied += 1
                    self.files_modified.add(py_file)

            except Exception as e:
                logger.error("Error fixing incomplete file %s: %s", py_file, e)

    def check_syntax_errors(self) -> int:
        """Check remaining syntax errors."""
        logger.info("Checking remaining syntax errors...")

        result = subprocess.run(
            ["ruff", "check", str(self.base_path), "--select", "E999", "--statistics"],
            capture_output=True,
            text=True,
        )

        syntax_errors = 0
        for line in result.stdout.split("\n"):
            if "syntax-error" in line:
                parts = line.strip().split()
                if parts and parts[0].isdigit():
                    syntax_errors = int(parts[0])
                    break

        return syntax_errors

    def run(self) -> None:
        """Run all syntax error fixes."""
        logger.info("=" * 80)
        logger.info("FIXING CRITICAL SYNTAX ERRORS")
        logger.info("=" * 80)

        # Initial check
        initial_errors = self.check_syntax_errors()
        logger.info("Initial syntax errors: %s", initial_errors)

        # Apply fixes
        self.fix_broken_imports()
        self.fix_incomplete_files()

        # Final check
        final_errors = self.check_syntax_errors()
        logger.info("\n" + "=" * 80)
        logger.info("SYNTAX ERROR FIX RESULTS")
        logger.info("=" * 80)
        logger.info("Syntax errors: %s → %s", initial_errors, final_errors)
        logger.info("Files modified: %s", len(self.files_modified))
        logger.info("Total fixes applied: %s", self.fixes_applied)

        if final_errors == 0:
            logger.info("\n✅ ALL SYNTAX ERRORS FIXED!")
            logger.info("\n❌ %s syntax errors remain", final_errors)


if __name__ == "__main__":
    fixer = SyntaxErrorFixer()
    fixer.run()
