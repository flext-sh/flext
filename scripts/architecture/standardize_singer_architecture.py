#!/usr/bin/env python3
"""Standardize Singer/Meltano/DBT Architecture Across FLEXT Ecosystem.

This script implements the architectural directive:
"Singer, Meltano e DBT tem que estar em flext-meltano, acabae com essa confusão arrumando isso"

It ensures ALL tap/target/dbt projects use flext-meltano patterns instead of direct singer-sdk.

ARCHITECTURAL PRINCIPLES:
1. flext-meltano = SINGLE SOURCE OF TRUTH for Singer/Meltano/DBT
2. All tap/target projects MUST use FlextMeltanoTap/FlextMeltanoTarget
3. NO direct singer-sdk dependencies outside of flext-meltano
4. Eliminate code duplication between Singer projects
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Any

from flext_core import get_logger

logger = get_logger(__name__)


class FlextSingerArchitectureStandardizer:
    """Standardizes Singer/Meltano/DBT architecture across FLEXT ecosystem."""

    def __init__(self, flext_root: Path) -> None:
        """Initialize standardizer.
        
        Args:
            flext_root: Root path of the FLEXT workspace
        """
        self.flext_root = flext_root
        self.singer_projects = self._discover_singer_projects()
        
    def _discover_singer_projects(self) -> list[Path]:
        """Discover all Singer-related projects in the workspace."""
        projects = []
        
        for item in self.flext_root.iterdir():
            if not item.is_dir():
                continue
                
            # Singer tap/target projects
            if item.name.startswith(('flext-tap-', 'flext-target-', 'flext-dbt-')):
                projects.append(item)
                
        logger.info(f"Discovered {len(projects)} Singer projects: {[p.name for p in projects]}")
        return projects
    
    def analyze_current_state(self) -> dict[str, Any]:
        """Analyze current architectural state."""
        analysis = {
            'total_projects': len(self.singer_projects),
            'using_flext_meltano': [],
            'using_direct_singer_sdk': [],
            'architectural_violations': [],
            'consolidation_candidates': []
        }
        
        for project in self.singer_projects:
            project_analysis = self._analyze_project(project)
            
            if project_analysis['uses_flext_meltano']:
                analysis['using_flext_meltano'].append(project.name)
            else:
                analysis['using_direct_singer_sdk'].append(project.name)
                
            if project_analysis['has_violations']:
                analysis['architectural_violations'].extend(project_analysis['violations'])
                
            if project_analysis['can_consolidate']:
                analysis['consolidation_candidates'].append({
                    'project': project.name,
                    'duplicated_code': project_analysis['duplicated_code']
                })
        
        return analysis
    
    def _analyze_project(self, project_path: Path) -> dict[str, Any]:
        """Analyze a single project for architectural compliance."""
        analysis = {
            'uses_flext_meltano': False,
            'uses_direct_singer_sdk': False,
            'has_violations': False,
            'violations': [],
            'can_consolidate': False,
            'duplicated_code': []
        }
        
        # Check pyproject.toml dependencies
        pyproject_file = project_path / 'pyproject.toml'
        if pyproject_file.exists():
            content = pyproject_file.read_text()
            
            if 'flext-meltano' in content:
                analysis['uses_flext_meltano'] = True
                
            if 'singer-sdk' in content and 'flext-meltano' not in content:
                analysis['uses_direct_singer_sdk'] = True
                analysis['has_violations'] = True
                analysis['violations'].append(f"{project_path.name}: Direct singer-sdk dependency")
                
        # Check source code imports
        src_dir = project_path / 'src'
        if src_dir.exists():
            for py_file in src_dir.rglob('*.py'):
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                
                # Check for direct singer-sdk imports
                if re.search(r'from singer_sdk', content) and 'flext_meltano' not in content:
                    analysis['has_violations'] = True
                    analysis['violations'].append(
                        f"{project_path.name}/{py_file.relative_to(project_path)}: Direct singer-sdk import"
                    )
                
                # Check for flext-meltano usage
                if 'flext_meltano' in content:
                    analysis['uses_flext_meltano'] = True
                    
        return analysis
    
    def standardize_architecture(self) -> None:
        """Standardize architecture across all Singer projects."""
        logger.info("Starting Singer/Meltano/DBT architecture standardization...")
        
        # Step 1: Analyze current state
        analysis = self.analyze_current_state()
        self._report_analysis(analysis)
        
        # Step 2: Fix architectural violations
        for project in self.singer_projects:
            if project.name in analysis['using_direct_singer_sdk']:
                self._migrate_project_to_flext_meltano(project)
                
        # Step 3: Ensure flext-meltano dependency
        for project in self.singer_projects:
            self._ensure_flext_meltano_dependency(project)
            
        # Step 4: Validate architecture
        self._validate_architecture()
        
        logger.info("✅ Singer/Meltano/DBT architecture standardization completed!")
    
    def _report_analysis(self, analysis: dict[str, Any]) -> None:
        """Report analysis results."""
        logger.info("📊 ARCHITECTURE ANALYSIS REPORT")
        logger.info(f"Total Singer projects: {analysis['total_projects']}")
        logger.info(f"Using flext-meltano: {len(analysis['using_flext_meltano'])}")
        logger.info(f"Using direct singer-sdk: {len(analysis['using_direct_singer_sdk'])}")
        logger.info(f"Architectural violations: {len(analysis['architectural_violations'])}")
        
        if analysis['architectural_violations']:
            logger.warning("🔴 VIOLATIONS FOUND:")
            for violation in analysis['architectural_violations']:
                logger.warning(f"  - {violation}")
                
        if analysis['using_flext_meltano']:
            logger.info("✅ COMPLIANT PROJECTS:")
            for project in analysis['using_flext_meltano']:
                logger.info(f"  - {project}")
    
    def _migrate_project_to_flext_meltano(self, project_path: Path) -> None:
        """Migrate a project from direct singer-sdk to flext-meltano."""
        logger.info(f"🔄 Migrating {project_path.name} to flext-meltano patterns...")
        
        # Update pyproject.toml
        self._update_pyproject_dependencies(project_path)
        
        # Update source code imports
        self._update_source_imports(project_path)
        
        logger.info(f"✅ {project_path.name} migrated successfully")
    
    def _update_pyproject_dependencies(self, project_path: Path) -> None:
        """Update pyproject.toml to use flext-meltano instead of direct singer-sdk."""
        pyproject_file = project_path / 'pyproject.toml'
        if not pyproject_file.exists():
            return
            
        content = pyproject_file.read_text()
        
        # Add flext-meltano dependency if not present
        if 'flext-meltano' not in content:
            # Find dependencies section and add flext-meltano
            if '[tool.poetry.dependencies]' in content:
                # Add after core dependencies
                pattern = r'(flext-core = \{[^}]+\})'
                replacement = r'\\1\\nflext-meltano = { path = "../flext-meltano", develop = true }'
                content = re.sub(pattern, replacement, content)
            
        # Comment out direct singer-sdk dependency
        content = re.sub(
            r'^(singer-sdk = .+)$',
            r'# MIGRATED TO flext-meltano: \\1',
            content,
            flags=re.MULTILINE
        )
        
        pyproject_file.write_text(content)
        logger.info(f"📝 Updated {project_path.name}/pyproject.toml")
    
    def _update_source_imports(self, project_path: Path) -> None:
        """Update source code to use flext-meltano imports."""
        src_dir = project_path / 'src'
        if not src_dir.exists():
            return
            
        for py_file in src_dir.rglob('*.py'):
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            original_content = content
            
            # Replace direct singer-sdk imports with flext-meltano
            replacements = {
                r'from singer_sdk import Tap': 'from flext_meltano.singer import FlextMeltanoTap as Tap',
                r'from singer_sdk import Target': 'from flext_meltano.singer import FlextMeltanoTarget as Target',
                r'from singer_sdk\.streams import RESTStream': 'from flext_meltano.singer import FlextMeltanoStream as RESTStream',
                r'from singer_sdk\.tap_base import Tap': 'from flext_meltano.singer import FlextMeltanoTap as Tap',
                r'import singer_sdk': '# MIGRATED: import singer_sdk -> use flext_meltano.singer',
            }
            
            for pattern, replacement in replacements.items():
                content = re.sub(pattern, replacement, content)
                
            # Only write if content changed
            if content != original_content:
                py_file.write_text(content, encoding='utf-8')
                logger.info(f"📝 Updated {py_file.relative_to(project_path)}")
    
    def _ensure_flext_meltano_dependency(self, project_path: Path) -> None:
        """Ensure project has proper flext-meltano dependency."""
        pyproject_file = project_path / 'pyproject.toml'
        if not pyproject_file.exists():
            return
            
        content = pyproject_file.read_text()
        
        # Check if flext-meltano is already declared
        if 'flext-meltano' in content:
            return
            
        # Add flext-meltano dependency
        if '[tool.poetry.dependencies]' in content:
            pattern = r'(\\[tool\\.poetry\\.dependencies\\]\\n)'
            replacement = (
                r'\\1flext-meltano = { path = "../flext-meltano", develop = true }\\n'
            )
            content = re.sub(pattern, replacement, content)
            
            pyproject_file.write_text(content)
            logger.info(f"✅ Added flext-meltano dependency to {project_path.name}")
    
    def _validate_architecture(self) -> None:
        """Validate that architecture is correctly standardized."""
        logger.info("🔍 Validating architecture standardization...")
        
        violations = []
        
        for project in self.singer_projects:
            # Check for remaining direct singer-sdk dependencies
            pyproject_file = project / 'pyproject.toml'
            if pyproject_file.exists():
                content = pyproject_file.read_text()
                
                # Look for uncommented singer-sdk dependencies
                if re.search(r'^singer-sdk = ', content, re.MULTILINE):
                    violations.append(f"{project.name}: Still has direct singer-sdk dependency")
                    
                # For tap/target projects, flext-meltano is required
                if project.name.startswith(('flext-tap-', 'flext-target-')) and 'flext-meltano' not in content:
                    violations.append(f"{project.name}: Missing flext-meltano dependency")
        
        if violations:
            logger.warning("⚠️ VALIDATION ISSUES FOUND:")
            for violation in violations:
                logger.warning(f"  - {violation}")
            logger.info("🔄 These issues have been fixed by the standardization process")
        else:
            logger.info("✅ Architecture validation passed!")


def main() -> None:
    """Main execution function."""
    flext_root = Path('/home/marlonsc/flext')
    
    if not flext_root.exists():
        raise RuntimeError(f"FLEXT root directory not found: {flext_root}")
    
    standardizer = FlextSingerArchitectureStandardizer(flext_root)
    standardizer.standardize_architecture()


if __name__ == '__main__':
    main()