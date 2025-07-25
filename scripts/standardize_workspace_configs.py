#!/usr/bin/env python3
"""
FLEXT Workspace Configuration Standardization Script

This script standardizes configuration across all FLEXT subprojects:
1. Updates line-length to 88 characters (Python community standard)
2. Ensures consistent coverage thresholds (90%)
3. Updates projects to use shared configurations
4. Maintains project-specific settings where appropriate

Usage:
    python scripts/standardize_workspace_configs.py [--dry-run] [--project PROJECT_NAME]
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

import tomlkit


class FlextConfigStandardizer:
    """Standardizes FLEXT workspace configurations professionally."""
    
    def __init__(self, workspace_root: Path, dry_run: bool = False):
        self.workspace_root = workspace_root
        self.dry_run = dry_run
        self.changes_made = 0
        
        # Projects that should maintain special configurations
        self.special_configs = {
            "flext-core": {
                "line_length": 88,  # Upgrade from 79 to modern standard
                "coverage_threshold": 90,  # Increase from 80 for foundation
                "reason": "Foundation library - upgraded to modern standards"
            },
            "flext-quality": {
                "line_length": 88,
                "coverage_threshold": 90,  # Increase from 85
                "reason": "Quality analysis tool - requires high standards"
            }
        }
        
    def find_subprojects(self) -> List[Path]:
        """Find all FLEXT subprojects with pyproject.toml files."""
        projects = []
        
        for path in self.workspace_root.iterdir():
            if (path.is_dir() and 
                path.name.startswith(('flext-', 'flexcore', 'algar-', 'gruponos-')) and
                (path / 'pyproject.toml').exists()):
                projects.append(path)
                
        return sorted(projects)
    
    def load_pyproject(self, project_path: Path) -> Optional[Dict]:
        """Load pyproject.toml file safely."""
        pyproject_file = project_path / 'pyproject.toml'
        if not pyproject_file.exists():
            return None
            
        try:
            with open(pyproject_file, 'r', encoding='utf-8') as f:
                return tomlkit.load(f)
        except Exception as e:
            print(f"❌ Error loading {pyproject_file}: {e}")
            return None
    
    def save_pyproject(self, project_path: Path, content: Dict) -> bool:
        """Save pyproject.toml file safely."""
        if self.dry_run:
            return True
            
        pyproject_file = project_path / 'pyproject.toml'
        try:
            with open(pyproject_file, 'w', encoding='utf-8') as f:
                tomlkit.dump(content, f)
            return True
        except Exception as e:
            print(f"❌ Error saving {pyproject_file}: {e}")
            return False
    
    def standardize_ruff_config(self, project_name: str, config: Dict) -> bool:
        """Standardize Ruff configuration."""
        changed = False
        
        if 'tool' not in config:
            config['tool'] = {}
        if 'ruff' not in config['tool']:
            config['tool']['ruff'] = {}
            
        ruff_config = config['tool']['ruff']
        
        # Get target line length for this project
        target_length = self.special_configs.get(project_name, {}).get('line_length', 88)
        
        # Update line-length
        if ruff_config.get('line-length') != target_length:
            old_length = ruff_config.get('line-length', 'unset')
            ruff_config['line-length'] = target_length
            print(f"  📏 Updated line-length: {old_length} → {target_length}")
            changed = True
            
        # Ensure extend reference to shared config
        if 'extend' not in ruff_config or ruff_config['extend'] != '../.ruff-shared.toml':
            ruff_config['extend'] = '../.ruff-shared.toml'
            print(f"  🔗 Added reference to shared Ruff config")
            changed = True
            
        # Keep project-specific overrides
        project_specific_ignores = {
            'flext-quality': ['DJ001', 'DJ008'],  # Django-specific rules
            'flext-auth': ['S105', 'S106'],       # Security rules for auth
        }
        
        if project_name in project_specific_ignores:
            if 'lint' not in ruff_config:
                ruff_config['lint'] = {}
            if 'ignore' not in ruff_config['lint']:
                ruff_config['lint']['ignore'] = []
                
            for ignore in project_specific_ignores[project_name]:
                if ignore not in ruff_config['lint']['ignore']:
                    ruff_config['lint']['ignore'].append(ignore)
                    print(f"  🎯 Added project-specific ignore: {ignore}")
                    changed = True
        
        return changed
    
    def standardize_pytest_config(self, project_name: str, config: Dict) -> bool:
        """Standardize pytest configuration."""
        changed = False
        
        if 'tool' not in config:
            config['tool'] = {}
        if 'pytest' not in config['tool']:
            config['tool']['pytest'] = {}
        if 'ini_options' not in config['tool']['pytest']:
            config['tool']['pytest']['ini_options'] = {}
            
        pytest_config = config['tool']['pytest']['ini_options']
        
        # Get target coverage threshold
        target_coverage = self.special_configs.get(project_name, {}).get('coverage_threshold', 90)
        
        # Update coverage threshold in addopts
        if 'addopts' in pytest_config:
            addopts = pytest_config['addopts']
            if isinstance(addopts, list):
                # Find and update --cov-fail-under
                for i, opt in enumerate(addopts):
                    if opt.startswith('--cov-fail-under='):
                        old_threshold = opt.split('=')[1]
                        if int(old_threshold) != target_coverage:
                            addopts[i] = f'--cov-fail-under={target_coverage}'
                            print(f"  📊 Updated coverage threshold: {old_threshold}% → {target_coverage}%")
                            changed = True
                        break
                else:
                    # Add coverage threshold if not present
                    addopts.append(f'--cov-fail-under={target_coverage}')
                    print(f"  ➕ Added coverage threshold: {target_coverage}%")
                    changed = True
        
        # Add reference to shared pytest config
        # Note: pytest doesn't support extend like ruff, so we document the shared standards
        if 'minversion' not in pytest_config or pytest_config['minversion'] != '8.0':
            pytest_config['minversion'] = '8.0'
            print(f"  🔧 Standardized pytest minversion to 8.0")
            changed = True
            
        return changed
    
    def standardize_mypy_config(self, project_name: str, config: Dict) -> bool:
        """Standardize MyPy configuration."""
        changed = False
        
        if 'tool' not in config:
            config['tool'] = {}
        if 'mypy' not in config['tool']:
            config['tool']['mypy'] = {}
            
        mypy_config = config['tool']['mypy']
        
        # Ensure strict mode is enabled
        if mypy_config.get('strict') is not True:
            mypy_config['strict'] = True
            print(f"  🔒 Enabled MyPy strict mode")
            changed = True
            
        # Ensure Python 3.13
        if mypy_config.get('python_version') != '3.13':
            mypy_config['python_version'] = '3.13'
            print(f"  🐍 Set Python version to 3.13")
            changed = True
            
        return changed
    
    def standardize_project(self, project_path: Path) -> bool:
        """Standardize a single project."""
        project_name = project_path.name
        print(f"\n🔧 Standardizing: {project_name}")
        
        # Load current configuration
        config = self.load_pyproject(project_path)
        if not config:
            print(f"  ❌ Could not load pyproject.toml")
            return False
            
        total_changes = 0
        
        # Standardize each configuration section
        if self.standardize_ruff_config(project_name, config):
            total_changes += 1
            
        if self.standardize_pytest_config(project_name, config):
            total_changes += 1
            
        if self.standardize_mypy_config(project_name, config):
            total_changes += 1
        
        # Save changes
        if total_changes > 0:
            if self.save_pyproject(project_path, config):
                print(f"  ✅ Applied {total_changes} configuration changes")
                self.changes_made += total_changes
                return True
            else:
                print(f"  ❌ Failed to save changes")
                return False
        else:
            print(f"  ✨ Already up to date")
            return True
    
    def run_standardization(self, specific_project: Optional[str] = None) -> bool:
        """Run standardization on all or specific project."""
        print("🚀 FLEXT Workspace Configuration Standardization")
        print("=" * 50)
        
        if self.dry_run:
            print("🔍 DRY RUN MODE - No changes will be made")
        
        projects = self.find_subprojects()
        
        if specific_project:
            projects = [p for p in projects if p.name == specific_project]
            if not projects:
                print(f"❌ Project '{specific_project}' not found")
                return False
        
        print(f"📦 Found {len(projects)} projects to standardize")
        
        success_count = 0
        for project_path in projects:
            if self.standardize_project(project_path):
                success_count += 1
        
        print(f"\n📊 Standardization Results:")
        print(f"  ✅ Successful: {success_count}/{len(projects)} projects")
        print(f"  🔧 Total changes: {self.changes_made}")
        
        if not self.dry_run and self.changes_made > 0:
            print(f"\n💡 Next steps:")
            print(f"  1. Run: cd /home/marlonsc/flext && poetry install")
            print(f"  2. Test: make validate-all-projects")
            print(f"  3. Format: ruff format . --config .ruff-shared.toml")
        
        return success_count == len(projects)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Standardize FLEXT workspace configurations")
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    parser.add_argument('--project', help='Standardize specific project only')
    
    args = parser.parse_args()
    
    workspace_root = Path('/home/marlonsc/flext')
    if not workspace_root.exists():
        print(f"❌ Workspace root not found: {workspace_root}")
        sys.exit(1)
    
    standardizer = FlextConfigStandardizer(workspace_root, dry_run=args.dry_run)
    
    try:
        success = standardizer.run_standardization(args.project)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Standardization cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()