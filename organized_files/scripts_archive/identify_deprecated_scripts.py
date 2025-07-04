#!/usr/bin/env python3
"""Identify deprecated scripts that can be removed after CLI migration."""

import re
from pathlib import Path
from typing import Dict, List

from rich.console import Console
from rich.table import Table

console = Console()


class DeprecatedScriptIdentifier:
    """Identify scripts that are now replaced by the unified CLI."""

    def __init__(self):
        self.workspace_root = Path(__file__).parent

    def identify_deprecated_scripts(self) -> dict[str, list[str]]:
        """Identify all deprecated scripts categorized by type."""
        deprecated = {
            "quality_scripts": [],
            "migration_scripts": [],
            "temp_scripts": [],
            "test_scripts": [],
            "analysis_scripts": []
        }

        # Quality/fix scripts pattern
        quality_patterns = [
            r"^achieve.*compliance.*\.py$",
            r"^fix_.*\.py$",
            r".*quality.*\.py$",
            r".*mypy.*\.py$",
            r".*syntax.*\.py$",
            r".*ruff.*\.py$"
        ]

        # Migration scripts pattern
        migration_patterns = [
            r"^analyze_.*\.py$",
            r"^complete_.*\.py$",
            r"^create_.*\.py$",
            r"^debug_.*\.py$",
            r"^final_.*\.py$",
            r"^import_.*\.py$",
            r"^production_.*\.py$",
            r"^validate_.*\.py$",
            r"^verify_.*\.py$"
        ]

        # Temporary/test scripts
        temp_patterns = [
            r"^test_(?!.*test\.py$).*\.py$",  # test_* but not actual test files
            r"^temp_.*\.py$",
            r"^mock_.*\.py$",
            r"^check_.*\.py$",
            r"^optimize_.*\.py$"
        ]

        # Analysis/reporting scripts
        analysis_patterns = [
            r"^system_.*\.py$",
            r".*_analysis.*\.py$",
            r".*_report.*\.py$",
            r".*benchmark.*\.py$"
        ]

        # Scan workspace for Python scripts
        for py_file in self._find_python_scripts():
            relative_path = str(py_file.relative_to(self.workspace_root))
            filename = py_file.name

            # Skip actual test files and important scripts
            if self._should_keep_script(py_file):
                continue

            # Categorize deprecated scripts
            if any(re.match(pattern, filename) for pattern in quality_patterns):
                deprecated["quality_scripts"].append(relative_path)
            elif any(re.match(pattern, filename) for pattern in migration_patterns):
                deprecated["migration_scripts"].append(relative_path)
            elif any(re.match(pattern, filename) for pattern in temp_patterns):
                deprecated["temp_scripts"].append(relative_path)
            elif any(re.match(pattern, filename) for pattern in analysis_patterns):
                deprecated["analysis_scripts"].append(relative_path)

        return deprecated

    def _find_python_scripts(self) -> list[Path]:
        """Find all Python scripts in the workspace."""
        scripts = []

        # Search patterns
        patterns = ["*.py"]

        for pattern in patterns:
            # Search in root
            scripts.extend(self.workspace_root.glob(pattern))

            # Search in project directories
            for project_dir in self.workspace_root.iterdir():
                if project_dir.is_dir() and not project_dir.name.startswith("."):
                    scripts.extend(project_dir.rglob(pattern))

        return sorted(set(scripts))

    def _should_keep_script(self, script_path: Path) -> bool:
        """Determine if a script should be kept."""
        filename = script_path.name

        # Keep important scripts
        keep_patterns = [
            r"^__.*__\.py$",      # Python special files
            r"^setup\.py$",       # Setup scripts
            r"^conftest\.py$",    # Pytest configuration
            r"^manage\.py$",      # Django management
            r"tests/test_.*\.py$",  # Actual test files
        ]

        # Keep scripts in certain directories
        keep_dirs = [
            "src/",
            ".venv/",
            "node_modules/",
            ".git/",
            "__pycache__/",
            "dist/",
            "build/"
        ]

        relative_path = str(script_path.relative_to(self.workspace_root))

        # Check patterns
        for pattern in keep_patterns:
            if re.search(pattern, relative_path):
                return True

        # Check directories
        for keep_dir in keep_dirs:
            if keep_dir in relative_path:
                return True

        # Keep if it's the CLI itself
        return filename in {"flx", "identify_deprecated_scripts.py"}

    def generate_cleanup_script(self, deprecated: dict[str, list[str]]) -> str:
        """Generate a script to safely remove deprecated files."""
        script_lines = [
            "#!/bin/bash",
            "# Auto-generated script to remove deprecated files",
            "# Generated by identify_deprecated_scripts.py",
            "",
            "echo '🧹 Cleaning up deprecated scripts...'",
            "echo 'This will remove scripts replaced by the unified CLI'",
            "echo ''",
            "read -p 'Continue? (y/N): ' -n 1 -r",
            "echo",
            "if [[ ! $REPLY =~ ^[Yy]$ ]]; then",
            "    echo 'Cleanup cancelled'",
            "    exit 0",
            "fi",
            "",
            "# Create backup directory",
            'backup_dir="deprecated_scripts_backup_$(date +%Y%m%d_%H%M%S)"',
            'mkdir -p "$backup_dir"',
            'echo "📦 Creating backup in $backup_dir/"',
            ""
        ]

        total_files = 0
        for category, files in deprecated.items():
            if files:
                script_lines.append(f"# {category.replace('_', ' ').title()}")
                for file_path in files:
                    script_lines.extend((f'if [ -f "{file_path}" ]; then', f'    cp "{file_path}" "$backup_dir/"', f'    rm "{file_path}"', f'    echo "✅ Removed {file_path}"', "fi"))
                    total_files += 1
                script_lines.append("")

        script_lines.extend([
            "echo ''",
            "echo '🎉 Cleanup complete!'",
            f"echo 'Removed {total_files} deprecated scripts'",
            "echo 'Backup available in: $backup_dir/'",
            "echo ''",
            "echo 'Use the unified CLI instead:'",
            "echo '  ./flx --help'",
            "echo '  ./flx quality check'",
            "echo '  ./flx migration status <project>'",
        ])

        return "\n".join(script_lines)


def main():
    """Main execution."""
    identifier = DeprecatedScriptIdentifier()

    console.print("🔍 Identifying deprecated scripts...", style="blue")
    deprecated = identifier.identify_deprecated_scripts()

    # Create summary table
    table = Table(title="Deprecated Scripts Summary")
    table.add_column("Category", style="cyan")
    table.add_column("Count", style="green")
    table.add_column("CLI Replacement", style="yellow")

    replacements = {
        "quality_scripts": "./flx quality check/compliance",
        "migration_scripts": "./flx migration run <project>",
        "temp_scripts": "Remove (temporary)",
        "test_scripts": "Keep test files, remove others",
        "analysis_scripts": "./flx workspace status"
    }

    total_deprecated = 0
    for category, files in deprecated.items():
        count = len(files)
        total_deprecated += count
        if count > 0:
            table.add_row(
                category.replace("_", " ").title(),
                str(count),
                replacements.get(category, "Manual review")
            )

    console.print(table)
    console.print(f"\n📊 Total deprecated scripts: {total_deprecated}")

    # Show detailed lists
    for category, files in deprecated.items():
        if files:
            console.print(f"\n[bold]{category.replace('_', ' ').title()}:[/bold]")
            for file_path in sorted(files)[:10]:  # Show first 10
                console.print(f"  • {file_path}")
            if len(files) > 10:
                console.print(f"  ... and {len(files) - 10} more")

    # Generate cleanup script
    cleanup_script = identifier.generate_cleanup_script(deprecated)
    cleanup_path = Path("cleanup_deprecated_scripts.sh")

    with open(cleanup_path, "w", encoding="utf-8") as f:
        f.write(cleanup_script)

    cleanup_path.chmod(0o755)  # Make executable

    console.print(f"\n🧹 Cleanup script generated: {cleanup_path}")
    console.print("Review the script before running:")
    console.print(f"  cat {cleanup_path}")
    console.print(f"  ./{cleanup_path}")

    console.print("\n✅ Analysis complete! Use the unified CLI:")
    console.print("  ./flx --help")
    console.print("  ./flx info")


if __name__ == "__main__":
    main()
