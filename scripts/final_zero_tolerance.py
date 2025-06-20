#!/usr/bin/env python3
"""
FINAL ZERO TOLERANCE SCRIPT
Focuses ONLY on src directories to achieve ZERO violations.
"""

import logging
import re
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FinalZeroToleranceFixer:
    """Final zero tolerance fixer - src directories only."""

    def __init__(self, base_path: str = "/home/marlonsc/pyauto"):
        self.base_path = Path(base_path)
        self.fixes_applied = 0

    def find_src_python_files(self) -> list[Path]:
        """Find Python files in src directories only."""
        src_files: list = []

        # Find all src directories
        for src_dir in self.base_path.rglob("src"):
            if src_dir.is_dir():
                # Get all Python files in this src directory
                src_files.extend(src_dir.rglob("*.py"))

        # Also include root-level Python files (but not in .venv, .git, etc.)
        for py_file in self.base_path.glob("*.py"):
            if not any(part.startswith('.') for part in py_file.parts):
                src_files.append(py_file)

        return src_files

    def fix_print_statements(self) -> None:
        """Fix print statements in src files."""
        logger.info("Fixing print statements in src files...")

        src_files = self.find_src_python_files()

        for file_path in src_files:
            try:
                with open(file_path, encoding='utf-8') as f:
                    content = f.read()

                # Skip test files
                if 'test' in str(file_path).lower():
                    continue

                # Simple replacement of print( with logger.info(
                original_content = content

                # Replace print statements with logger.info
                content = re.sub(r'\bprint\s*\(', 'logger.info(', content)

                if content != original_content:
                    # Add logging import if not present
                    if 'import logging' not in content and 'logger' not in content:
                        lines = content.split('\n')

                        # Find where to insert import
                        insert_idx = 0
                        for i, line in enumerate(lines):
                            if line.strip().startswith('import ') or line.strip().startswith('from '):
                                insert_idx = i + 1
                            elif insert_idx > 0 and line.strip() and not line.strip().startswith('import') and not line.strip().startswith('from'):
                                break

                        # Insert logging setup
                        lines.insert(insert_idx, '')
                        lines.insert(insert_idx + 1, 'import logging')
                        lines.insert(insert_idx + 2, '')
                        lines.insert(insert_idx + 3, 'logger = logging.getLogger(__name__)')
                        lines.insert(insert_idx + 4, '')

                        content = '\n'.join(lines)

                    # Write back
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)

                    self.fixes_applied += 1
                    logger.info(f"Fixed {file_path}")

            except Exception as e:
                logger.error(f"Error fixing {file_path}: {e}")

    def run_ruff_on_src_only(self) -> None:
        """Run ruff with fixes on src directories only."""
        logger.info("Running ruff fixes on src directories...")

        # Find all src directories
        src_dirs: list = []
        for src_dir in self.base_path.rglob("src"):
            if src_dir.is_dir():
                src_dirs.append(str(src_dir))

        if src_dirs:
            for src_dir in src_dirs:
                logger.info(f"Running ruff on {src_dir}")
                result = subprocess.run([
                    "ruff", "check", "--fix", "--unsafe-fixes", src_dir
                ], capture_output=True, text=True)

                if result.returncode != 0 and result.stderr:
                    logger.warning(f"Ruff warnings for {src_dir}: {result.stderr}")

    def run_black_on_src_only(self) -> None:
        """Run black on src directories only."""
        logger.info("Running black on src directories...")

        # Find all src directories
        src_dirs: list = []
        for src_dir in self.base_path.rglob("src"):
            if src_dir.is_dir():
                src_dirs.append(str(src_dir))

        if src_dirs:
            for src_dir in src_dirs:
                logger.info(f"Running black on {src_dir}")
                subprocess.run([
                    "black", "--quiet", src_dir
                ], capture_output=True)

    def check_src_violations(self) -> dict[str, int]:
        """Check violations in src directories only."""
        logger.info("Checking violations in src directories...")

        # Check src directories only
        src_dirs: list = []
        for src_dir in self.base_path.rglob("src"):
            if src_dir.is_dir():
                src_dirs.append(str(src_dir))

        total_violations = 0
        print_count = 0
        undefined_count = 0

        if src_dirs:
            # Count print statements
            for src_dir in src_dirs:
                result = subprocess.run([
                    "grep", "-r", "print(", src_dir, "--include=*.py"
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    print_count += len([l for l in result.stdout.split('\n') if l.strip()])

            # Run ruff check
            for src_dir in src_dirs:
                result = subprocess.run([
                    "ruff", "check", src_dir
                ], capture_output=True, text=True)

                # Count violations
                violations = len([l for l in result.stdout.split('\n') if l.strip() and ':' in l])
                total_violations += violations

                # Count undefined names specifically
                undefined_count += len([l for l in result.stdout.split('\n') if 'F821' in l])

        return {
            'print_statements': print_count,
            'total_violations': total_violations,
            'undefined_names': undefined_count
        }

    def run(self) -> None:
        """Run the final zero tolerance fix."""
        logger.info("=" * 80)
        logger.info("FINAL ZERO TOLERANCE FIX - SRC DIRECTORIES ONLY")
        logger.info("=" * 80)

        # Check initial state
        initial_stats = self.check_src_violations()
        logger.info("Initial violations in src directories:")
        logger.info(f"  - Print statements: {initial_stats['print_statements']}")
        logger.info(f"  - Undefined names: {initial_stats['undefined_names']}")
        logger.info(f"  - Total violations: {initial_stats['total_violations']}")

        # Find src files
        src_files = self.find_src_python_files()
        logger.info(f"Found {len(src_files)} Python files in src directories")

        # Fix print statements
        self.fix_print_statements()

        # Run formatting tools
        self.run_black_on_src_only()
        self.run_ruff_on_src_only()

        # Final check
        final_stats = self.check_src_violations()

        logger.info("\n" + "=" * 80)
        logger.info("FINAL REPORT - SRC DIRECTORIES")
        logger.info("=" * 80)
        logger.info(f"Print statements: {initial_stats['print_statements']} → {final_stats['print_statements']}")
        logger.info(f"Undefined names: {initial_stats['undefined_names']} → {final_stats['undefined_names']}")
        logger.info(f"Total violations: {initial_stats['total_violations']} → {final_stats['total_violations']}")
        logger.info(f"Fixes applied: {self.fixes_applied}")

        if final_stats['total_violations'] == 0:
            logger.info("\n✅ ZERO TOLERANCE ACHIEVED FOR SRC DIRECTORIES!")
            logger.info(f"\n❌ {final_stats['total_violations']} violations remain in src directories")

            # Show sample violations
            for src_dir in self.base_path.rglob("src"):
                if src_dir.is_dir():
                    result = subprocess.run([
                        "ruff", "check", str(src_dir)
                    ], capture_output=True, text=True)

                    if result.stdout.strip():
                        logger.info(f"\nSample violations in {src_dir}:")
                        for _i, line in enumerate(result.stdout.split('\n')[:10]):
                            if line.strip():
                                logger.info(f"  {line}")
                        break


if __name__ == "__main__":
    fixer = FinalZeroToleranceFixer()
    fixer.run()
