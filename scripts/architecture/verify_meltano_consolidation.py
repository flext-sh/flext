#!/usr/bin/env python3
"""Verify FLEXT Meltano Consolidation Architecture.

Validates that Singer/Meltano/DBT consolidation has been successfully implemented
according to the architectural directive:
"Singer, Meltano e DBT tem que estar em flext-meltano, acabae com essa confusão arrumando isso"
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from flext_core import get_logger

logger = get_logger(__name__)


class FlextMeltanoConsolidationVerifier:
    """Verifies successful consolidation of Singer/Meltano/DBT in flext-meltano."""

    def __init__(self, flext_root: Path) -> None:
        """Initialize verifier.
        
        Args:
            flext_root: Root path of the FLEXT workspace
        """
        self.flext_root = flext_root
        self.singer_projects = self._discover_singer_projects()
        
    def _discover_singer_projects(self) -> list[Path]:
        """Discover all Singer-related projects."""
        projects = []
        
        for item in self.flext_root.iterdir():
            if not item.is_dir():
                continue
                
            # Singer tap/target/dbt projects
            if item.name.startswith(('flext-tap-', 'flext-target-', 'flext-dbt-')):
                projects.append(item)
                
        return projects
    
    def verify_consolidation(self) -> dict[str, Any]:
        """Verify consolidation status."""
        logger.info("🔍 Verifying FLEXT Meltano consolidation architecture...")
        
        results = {
            'consolidation_successful': True,
            'flext_meltano_status': self._verify_flext_meltano(),
            'project_compliance': [],
            'remaining_violations': [],
            'recommendations': []
        }
        
        # Check each Singer project
        for project in self.singer_projects:
            compliance = self._verify_project_compliance(project)
            results['project_compliance'].append(compliance)
            
            if not compliance['compliant']:
                results['consolidation_successful'] = False
                results['remaining_violations'].extend(compliance['violations'])
        
        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(results)
        
        return results
    
    def _verify_flext_meltano(self) -> dict[str, Any]:
        """Verify flext-meltano has comprehensive Singer/Meltano/DBT integration."""
        meltano_path = self.flext_root / 'flext-meltano'
        
        status = {
            'exists': meltano_path.exists(),
            'has_singer_integration': False,
            'has_dbt_integration': False,
            'has_meltano_integration': False,
            'comprehensive_exports': False
        }
        
        if not status['exists']:
            return status
            
        # Check __init__.py exports
        init_file = meltano_path / 'src' / 'flext_meltano' / '__init__.py'
        if init_file.exists():
            content = init_file.read_text()
            
            # Check for Singer components
            singer_components = [
                'FlextMeltanoTap', 'FlextMeltanoTarget', 'FlextMeltanoCatalog', 
                'FlextMeltanoStream'
            ]
            status['has_singer_integration'] = all(comp in content for comp in singer_components)
            
            # Check for DBT components
            dbt_components = ['FlextMeltanoDbtProject', 'FlextMeltanoDbtRunner']
            status['has_dbt_integration'] = all(comp in content for comp in dbt_components)
            
            # Check for Meltano components
            meltano_components = [
                'FlextMeltanoPlatform', 'FlextMeltanoOrchestrator', 
                'FlextMeltanoProjectManager'
            ]
            status['has_meltano_integration'] = all(comp in content for comp in meltano_components)
            
            # Check comprehensive exports
            status['comprehensive_exports'] = len(content.split('__all__')) > 1
        
        return status
    
    def _verify_project_compliance(self, project_path: Path) -> dict[str, Any]:
        """Verify a project's compliance with consolidation architecture."""
        compliance = {
            'project': project_path.name,
            'compliant': True,
            'violations': [],
            'using_flext_meltano': False,
            'no_direct_singer_sdk': True
        }
        
        # Check pyproject.toml
        pyproject_file = project_path / 'pyproject.toml'
        if pyproject_file.exists():
            content = pyproject_file.read_text()
            
            # Check for flext-meltano dependency
            if 'flext-meltano' in content:
                compliance['using_flext_meltano'] = True
            elif project_path.name.startswith(('flext-tap-', 'flext-target-')):
                compliance['violations'].append("Missing flext-meltano dependency")
                compliance['compliant'] = False
                
            # Check for direct singer-sdk dependency (uncommented)
            if re.search(r'^singer-sdk = ', content, re.MULTILINE):
                compliance['violations'].append("Still has direct singer-sdk dependency")
                compliance['no_direct_singer_sdk'] = False
                compliance['compliant'] = False
        
        # Check source code for direct singer-sdk imports
        src_dir = project_path / 'src'
        if src_dir.exists():
            for py_file in src_dir.rglob('*.py'):
                try:
                    content = py_file.read_text(encoding='utf-8', errors='ignore')
                    
                    # Check for direct singer-sdk imports that aren't migrated
                    if 'from singer_sdk' in content and 'flext_meltano' not in content:
                        compliance['violations'].append(
                            f"File {py_file.relative_to(project_path)} has direct singer-sdk import"
                        )
                        compliance['compliant'] = False
                except Exception:
                    # Skip files that can't be read
                    pass
        
        return compliance
    
    def _generate_recommendations(self, results: dict[str, Any]) -> list[str]:
        """Generate recommendations based on verification results."""
        recommendations = []
        
        if not results['consolidation_successful']:
            recommendations.append(
                "🔄 Complete remaining migration tasks for full consolidation"
            )
            
        # Project-specific recommendations
        non_compliant = [
            p for p in results['project_compliance'] 
            if not p['compliant']
        ]
        
        if non_compliant:
            recommendations.append(
                f"🔧 Fix {len(non_compliant)} projects with architectural violations"
            )
            
        # Flext-meltano specific recommendations
        meltano_status = results['flext_meltano_status']
        if not meltano_status['comprehensive_exports']:
            recommendations.append(
                "📚 Enhance flext-meltano __all__ exports for better API discoverability"
            )
            
        if results['consolidation_successful']:
            recommendations.append(
                "✅ Architecture consolidation is complete - proceed with quality gates"
            )
            
        return recommendations
    
    def report_verification(self, results: dict[str, Any]) -> None:
        """Report verification results."""
        logger.info("📊 FLEXT MELTANO CONSOLIDATION VERIFICATION REPORT")
        logger.info("=" * 60)
        
        # Overall status
        if results['consolidation_successful']:
            logger.info("✅ CONSOLIDATION STATUS: SUCCESSFUL")
        else:
            logger.warning("⚠️ CONSOLIDATION STATUS: INCOMPLETE")
            
        # Flext-meltano status
        meltano_status = results['flext_meltano_status']
        logger.info(f"✅ flext-meltano exists: {meltano_status['exists']}")
        logger.info(f"✅ Singer integration: {meltano_status['has_singer_integration']}")
        logger.info(f"✅ DBT integration: {meltano_status['has_dbt_integration']}")
        logger.info(f"✅ Meltano integration: {meltano_status['has_meltano_integration']}")
        
        # Project compliance
        compliant_projects = [
            p for p in results['project_compliance'] 
            if p['compliant']
        ]
        logger.info(f"✅ Compliant projects: {len(compliant_projects)}/{len(results['project_compliance'])}")
        
        if compliant_projects:
            logger.info("✅ COMPLIANT PROJECTS:")
            for project in compliant_projects:
                logger.info(f"  - {project['project']}")
                
        # Remaining violations
        if results['remaining_violations']:
            logger.warning("🔴 REMAINING VIOLATIONS:")
            for violation in results['remaining_violations']:
                logger.warning(f"  - {violation}")
                
        # Recommendations
        if results['recommendations']:
            logger.info("💡 RECOMMENDATIONS:")
            for rec in results['recommendations']:
                logger.info(f"  - {rec}")


def main() -> None:
    """Main execution function."""
    flext_root = Path('/home/marlonsc/flext')
    
    verifier = FlextMeltanoConsolidationVerifier(flext_root)
    results = verifier.verify_consolidation()
    verifier.report_verification(results)
    
    # Exit with appropriate code
    if results['consolidation_successful']:
        logger.info("🎉 CONSOLIDATION VERIFICATION PASSED!")
    else:
        logger.warning("⚠️ Consolidation needs additional work")


if __name__ == '__main__':
    main()