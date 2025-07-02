#!/usr/bin/env python3
"""Organize deprecated scripts into structured backup directories."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from rich.console import Console
from rich.progress import track
from rich.table import Table

console = Console()

class ScriptOrganizer:
    """Organize deprecated scripts into categorized backup directories."""

    def __init__(self):
        self.workspace_root = Path(__file__).parent
        self.backup_root = self.workspace_root / "deprecated_scripts_backup"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def create_backup_structure(self) -> dict[str, Path]:
        """Create organized backup directory structure."""
        backup_base = self.backup_root / self.timestamp

        categories = {
            "quality_scripts": backup_base / "01_quality_management",
            "migration_scripts": backup_base / "02_migration_operations",
            "temp_scripts": backup_base / "03_temporary_scripts",
            "test_scripts": backup_base / "04_test_scripts",
            "analysis_scripts": backup_base / "05_analysis_reporting"
        }

        # Create directories
        for category_path in categories.values():
            category_path.mkdir(parents=True, exist_ok=True)

        # Create documentation
        self._create_backup_documentation(backup_base, categories)

        return categories

    def _create_backup_documentation(self, backup_base: Path, categories: dict[str, Path]):
        """Create documentation for the backup."""
        # Main README
        readme_content = f"""# Deprecated Scripts Backup - {self.timestamp}

## Overview

This backup contains scripts that were replaced by the unified FLX CLI interface.
These scripts are preserved for reference but should no longer be used.

## Replacement Commands

### Quality Management Scripts → `./flx quality`
```bash
# Old: python achieve_100_percent_compliance.py
./flx quality compliance --target 100

# Old: python fix_all_quality_issues.py  
./flx quality check --auto-fix

# Old: python fix_mypy_issues.py
./flx quality check --category ANN --auto-fix
```

### Migration Scripts → `./flx migration`
```bash
# Old: cd client-a-oud-mig && python analyze_hierarchy_errors.py
./flx migration run client-a-oud --dry-run

# Old: cd client-a-oud-mig && python complete_groups_migration.py
./flx migration run client-a-oud

# Old: cd client-b-meltano-native && python production_meltano_test.py
./flx migration run client-b
```

### Development Scripts → `./flx dev` / `make`
```bash
# Old: Various test/validation scripts
./flx dev test --coverage
./flx dev validate
./flx workspace status
```

## Directory Structure

- `01_quality_management/` - Scripts for code quality, linting, fixing
- `02_migration_operations/` - Data migration and transformation scripts
- `03_temporary_scripts/` - Temporary/experimental scripts  
- `04_test_scripts/` - Test and validation scripts
- `05_analysis_reporting/` - Analysis and reporting scripts

## CLI Documentation

For complete CLI documentation:
```bash
./flx --help
./flx info
```

## Restoration

If you need to restore any script:
```bash
# Copy back to workspace
cp path/to/script.py /home/marlonsc/flext/

# Make executable if needed
chmod +x script.py
```

**Note**: The unified CLI is the recommended approach. Only restore scripts if absolutely necessary.
"""

        with open(backup_base / "README.md", "w") as f:
            f.write(readme_content)

    def organize_scripts(self, deprecated_scripts: dict[str, list[str]]) -> dict[str, int]:
        """Organize scripts into backup directories."""
        categories = self.create_backup_structure()
        moved_counts = {}

        console.print(f"📦 Creating organized backup in: {self.backup_root / self.timestamp}")

        for category, script_paths in deprecated_scripts.items():
            if not script_paths:
                moved_counts[category] = 0
                continue

            category_dir = categories[category]
            moved_count = 0

            console.print(f"\n📂 Processing {category.replace('_', ' ').title()}...")

            for script_path in track(script_paths, description=f"Moving {category}"):
                source_path = self.workspace_root / script_path

                if not source_path.exists():
                    continue

                # Preserve directory structure in backup
                relative_path = Path(script_path)
                if relative_path.parent != Path():
                    # Create subdirectory structure
                    target_dir = category_dir / relative_path.parent
                    target_dir.mkdir(parents=True, exist_ok=True)
                    target_path = target_dir / relative_path.name
                else:
                    target_path = category_dir / relative_path.name

                try:
                    # Move file to backup
                    shutil.move(str(source_path), str(target_path))
                    moved_count += 1

                except Exception as e:
                    console.print(f"⚠️ Failed to move {script_path}: {e}", style="yellow")

            moved_counts[category] = moved_count
            console.print(f"✅ Moved {moved_count} {category.replace('_', ' ')}")

        return moved_counts

    def create_restoration_script(self, moved_counts: dict[str, int]):
        """Create a script to restore files if needed."""
        backup_path = self.backup_root / self.timestamp

        restore_script = f"""#!/bin/bash
# Restoration script for deprecated scripts backup {self.timestamp}
# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

echo "🔄 Deprecated Scripts Restoration Tool"
echo "======================================"
echo ""
echo "This script can restore scripts from backup:"
echo "  {backup_path}"
echo ""
echo "Available categories:"
echo "  1) Quality Management Scripts ({moved_counts.get('quality_scripts', 0)} files)"
echo "  2) Migration Operations Scripts ({moved_counts.get('migration_scripts', 0)} files)"  
echo "  3) Temporary Scripts ({moved_counts.get('temp_scripts', 0)} files)"
echo "  4) Test Scripts ({moved_counts.get('test_scripts', 0)} files)"
echo "  5) Analysis Scripts ({moved_counts.get('analysis_scripts', 0)} files)"
echo "  6) All scripts"
echo "  7) Exit"
echo ""

read -p "Select category to restore (1-7): " choice

backup_base="{backup_path}"
workspace_root="{self.workspace_root}"

case $choice in
    1)
        echo "🔧 Restoring quality management scripts..."
        if [ -d "$backup_base/01_quality_management" ]; then
            cp -r "$backup_base/01_quality_management"/* "$workspace_root/" 2>/dev/null || true
            echo "✅ Quality scripts restored"
        else
            echo "❌ No quality scripts found"
        fi
        ;;
    2)
        echo "📦 Restoring migration scripts..."
        if [ -d "$backup_base/02_migration_operations" ]; then
            cp -r "$backup_base/02_migration_operations"/* "$workspace_root/" 2>/dev/null || true
            echo "✅ Migration scripts restored"
        else
            echo "❌ No migration scripts found"
        fi
        ;;
    3)
        echo "⚡ Restoring temporary scripts..."
        if [ -d "$backup_base/03_temporary_scripts" ]; then
            cp -r "$backup_base/03_temporary_scripts"/* "$workspace_root/" 2>/dev/null || true
            echo "✅ Temporary scripts restored"
        else
            echo "❌ No temporary scripts found"
        fi
        ;;
    4)
        echo "🧪 Restoring test scripts..."
        if [ -d "$backup_base/04_test_scripts" ]; then
            cp -r "$backup_base/04_test_scripts"/* "$workspace_root/" 2>/dev/null || true
            echo "✅ Test scripts restored"
        else
            echo "❌ No test scripts found"
        fi
        ;;
    5)
        echo "📊 Restoring analysis scripts..."
        if [ -d "$backup_base/05_analysis_reporting" ]; then
            cp -r "$backup_base/05_analysis_reporting"/* "$workspace_root/" 2>/dev/null || true
            echo "✅ Analysis scripts restored"
        else
            echo "❌ No analysis scripts found"
        fi
        ;;
    6)
        echo "🔄 Restoring all scripts..."
        for category in "$backup_base"/*; do
            if [ -d "$category" ] && [ "$(basename "$category")" != "README.md" ]; then
                cp -r "$category"/* "$workspace_root/" 2>/dev/null || true
            fi
        done
        echo "✅ All scripts restored"
        ;;
    7)
        echo "👋 Exiting without restoration"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "⚠️ IMPORTANT: Use the unified CLI instead:"
echo "  ./flx --help"
echo "  ./flx quality check"
echo "  ./flx migration run <project>"
echo "  ./flx dev start"
"""

        restore_script_path = backup_path / "restore_scripts.sh"
        with open(restore_script_path, "w") as f:
            f.write(restore_script)

        restore_script_path.chmod(0o755)
        return restore_script_path

def main():
    """Main execution."""
    # Import the deprecated scripts identification
    import sys
    sys.path.append(str(Path(__file__).parent))

    from identify_deprecated_scripts import DeprecatedScriptIdentifier

    organizer = ScriptOrganizer()
    identifier = DeprecatedScriptIdentifier()

    console.print("🔍 Identifying deprecated scripts for organized backup...", style="blue")
    deprecated_scripts = identifier.identify_deprecated_scripts()

    total_scripts = sum(len(scripts) for scripts in deprecated_scripts.values())

    if total_scripts == 0:
        console.print("✅ No deprecated scripts found!", style="green")
        return

    # Show what will be moved
    table = Table(title="Scripts to be Moved to Backup")
    table.add_column("Category", style="cyan")
    table.add_column("Count", style="green")
    table.add_column("Backup Location", style="yellow")

    backup_base = organizer.backup_root / organizer.timestamp
    category_mapping = {
        "quality_scripts": "01_quality_management/",
        "migration_scripts": "02_migration_operations/",
        "temp_scripts": "03_temporary_scripts/",
        "test_scripts": "04_test_scripts/",
        "analysis_scripts": "05_analysis_reporting/"
    }

    for category, scripts in deprecated_scripts.items():
        if scripts:
            table.add_row(
                category.replace("_", " ").title(),
                str(len(scripts)),
                str(backup_base / category_mapping[category])
            )

    console.print(table)
    console.print(f"\n📊 Total scripts to move: {total_scripts}")

    # Auto-proceed with backup
    console.print("\n🚀 Proceeding with organized backup...", style="green")

    # Perform the organization
    moved_counts = organizer.organize_scripts(deprecated_scripts)
    total_moved = sum(moved_counts.values())

    # Create restoration script
    restore_script = organizer.create_restoration_script(moved_counts)

    # Summary
    console.print("\n🎉 Backup complete!", style="green")
    console.print(f"📦 Backup location: {backup_base}")
    console.print(f"📊 Total scripts moved: {total_moved}")
    console.print(f"🔄 Restoration script: {restore_script}")

    console.print("\n📚 Backup structure:")
    for category, count in moved_counts.items():
        if count > 0:
            console.print(f"  📂 {category.replace('_', ' ').title()}: {count} scripts")

    console.print("\n✅ Use the unified CLI instead:")
    console.print("  ./flx --help")
    console.print("  ./flx quality check")
    console.print("  ./flx migration run <project>")
    console.print("  ./flx workspace status")

if __name__ == "__main__":
    main()
