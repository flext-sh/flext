#!/usr/bin/env python3
"""Test File Consolidation Analysis.

Analyzes test file proliferation across PyAuto projects and suggests consolidation.
Avoids critical documentation files as specified by user.
"""

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def analyze_test_files() -> Any:
    """Analyze test file distribution and redundancy."""
    pyauto_root = Path("/home/marlonsc/pyauto")

    # Projects to analyze
    projects = [
        "flx",
        "flx-http-oracle-oic",
        "flx-http-oracle-wms",
        "flx-database-oracle",
        "client-b-oic-wms",
        "client-a-mig-oud",
    ]

    analysis = {
        "total_projects": 0,
        "projects_analyzed": [],
        "test_file_statistics": {},
        "redundancy_patterns": defaultdict(list),
        "consolidation_opportunities": [],
    }

    for project in projects:
        project_path = pyauto_root / project
        if not project_path.exists():
            continue

        tests_dir = project_path / "tests"
        if not tests_dir.exists():
            continue

        analysis["total_projects"] += 1
        analysis["projects_analyzed"].append(project)

        # Count test files
        test_files = list(tests_dir.rglob("test_*.py"))
        analysis["test_file_statistics"][project] = {
            "total_test_files": len(test_files),
            "test_files": [f.name for f in test_files[:10]],  # Sample
        }

        # Identify redundancy patterns
        adapter_tests = [f for f in test_files if "adapter" in f.name]
        client_tests = [f for f in test_files if "client" in f.name]
        [f for f in test_files if "config" in f.name]

        if len(adapter_tests) > 3:
            analysis["redundancy_patterns"]["excessive_adapter_tests"].append(
                {
                    "project": project,
                    "count": len(adapter_tests),
                    "files": [f.name for f in adapter_tests[:5]],
                },
            )

        if len(client_tests) > 3:
            analysis["redundancy_patterns"]["excessive_client_tests"].append(
                {
                    "project": project,
                    "count": len(client_tests),
                    "files": [f.name for f in client_tests[:5]],
                },
            )

    # Generate consolidation opportunities
    for project, stats in analysis["test_file_statistics"].items():
        if stats["total_test_files"] > 20:
            analysis["consolidation_opportunities"].append(
                {
                    "project": project,
                    "current_count": stats["total_test_files"],
                    "recommended_structure": {
                        "unit": [
                            "test_core.py",
                            "test_adapters.py",
                            "test_services.py",
                        ],
                        "integration": ["test_integration.py"],
                        "e2e": ["test_e2e.py"],
                    },
                    "estimated_reduction": f"{stats['total_test_files']} → 5-8 files",
                },
            )

    return analysis


def generate_consolidation_report(analysis) -> Any:
    """Generate consolidation report."""
    report = f"""# 🧪 Test File Consolidation Analysis Report

**Date**: 2025-06-11
**Analyzer**: Enterprise Standards Compliance
**Scope**: PyAuto monorepo test file organization

## 📊 Executive Summary

- **Projects Analyzed**: {analysis["total_projects"]}
- **Total Redundancy Issues**: {len(analysis["redundancy_patterns"]["excessive_adapter_tests"]) + len(analysis["redundancy_patterns"]["excessive_client_tests"])}
- **Consolidation Opportunities**: {len(analysis["consolidation_opportunities"])}

## 🔍 Detailed Findings

### Test File Statistics
"""

    for project, stats in analysis["test_file_statistics"].items():
        report += f"""
#### {project}
- **Total Test Files**: {stats["total_test_files"]}
- **Sample Files**: {", ".join(stats["test_files"][:3])}...
"""

    report += """
### 🚨 Redundancy Patterns Identified

#### Excessive Adapter Tests
"""

    for item in analysis["redundancy_patterns"]["excessive_adapter_tests"]:
        report += f"""
- **{item["project"]}**: {item["count"]} adapter test files
  - Examples: {", ".join(item["files"][:3])}...
"""

    report += """
### 💡 Consolidation Recommendations

#### Suggested Enterprise Test Structure
```
tests/
├── unit/
│   ├── test_core.py           # Domain entities, value objects
│   ├── test_adapters.py       # All adapter implementations
│   ├── test_services.py       # Application services
│   └── test_ports.py          # Port interfaces
├── integration/
│   ├── test_database.py       # Database integration
│   ├── test_external_apis.py  # External API integration
│   └── test_messaging.py      # Message bus integration
└── e2e/
    ├── test_complete_flows.py # End-to-end scenarios
    └── test_cli.py           # CLI interface testing
```
"""

    for opportunity in analysis["consolidation_opportunities"]:
        report += f"""
#### {opportunity["project"]}
- **Current**: {opportunity["current_count"]} test files
- **Recommended**: {opportunity["estimated_reduction"]}
- **Benefits**: Improved maintainability, reduced duplication, clearer test organization
"""

    report += """
## 🎯 Implementation Plan

### Phase 1: High-Impact Projects (Week 1)
- Target projects with >30 test files
- Consolidate redundant adapter/client tests
- Maintain test coverage while reducing file count

### Phase 2: Standard Structure (Week 2-3)
- Apply enterprise test structure to all projects
- Ensure consistent naming conventions
- Add comprehensive integration tests

### Phase 3: Quality Enhancement (Week 4)
- Validate test coverage maintained/improved
- Add missing test categories
- Document testing standards

## ⚠️ Coordination Notes

**CRITICAL**: This analysis avoids all documentation files specified by user:
- README.md
- CRITICAL_ANALYSIS_AND_ACTIONS.md
- DOCUMENTATION_STANDARDS*.md
- FLX_DOCUMENTATION_GAP_ANALYSIS.md
- IMPLEMENTATION_GUIDE.md

**Action Required**: Coordinate test consolidation with development teams before implementation.
"""

    return report


if __name__ == "__main__":
    print("🔍 Analyzing test file proliferation...")
    analysis = analyze_test_files()

    print("📊 Generating consolidation report...")
    report = generate_consolidation_report(analysis)

    # Save analysis data
    with open(
        "/home/marlonsc/pyauto/reports/analysis/test_consolidation_analysis.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(analysis, f, indent=2)

    # Save report
    with open(
        "/home/marlonsc/pyauto/reports/analysis/test_consolidation_report.md",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(report)

    print("✅ Analysis complete!")
    print(
        "📄 Report saved: /home/marlonsc/pyauto/reports/analysis/test_consolidation_report.md",
    )
    print(
        "📊 Data saved: /home/marlonsc/pyauto/reports/analysis/test_consolidation_analysis.json",
    )
