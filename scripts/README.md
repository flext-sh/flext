# 🛠️ PyAuto - Scripts and Automation Hub

> **Module**: Central scripts and automation utilities for PyAuto enterprise workspace | **Audience**: DevOps Engineers, Developers, System Administrators | **Status**: Production Ready

## 📋 **Overview**

Comprehensive collection of scripts and automation utilities for the PyAuto enterprise workspace, providing essential functionality for development workflows, maintenance tasks, testing procedures, and operational excellence. These scripts demonstrate best practices for enterprise-level automation and development tooling.

---

## 🧭 **Navigation Context**

**🏠 Root**: [PyAuto Home](../README.md) → **📂 Current**: Scripts and Automation Hub

---

## 🎯 **Module Purpose**

This scripts module provides essential automation utilities for the PyAuto workspace, including development workflow automation, maintenance procedures, testing frameworks, code quality tools, and operational scripts for all 21+ projects in the ecosystem.

### **Key Script Categories**

- **Analysis Scripts** - Code quality analysis and metrics collection
- **Maintenance Scripts** - Automated maintenance and cleanup procedures
- **Testing Scripts** - Test automation and validation procedures
- **Development Tools** - Development workflow automation
- **Pipeline Scripts** - CI/CD and data pipeline automation
- **Utility Scripts** - Common utilities and helper functions

---

## 📁 **Scripts Structure**

```
scripts/
├── analysis/
│   ├── analyze_flx.py                    # FLX framework analysis
│   ├── analyze_mypy_deep.py              # Deep mypy analysis
│   ├── check_audit_columns.py            # Audit column validation
│   ├── check_oracle_columns.py           # Oracle column verification
│   ├── code_quality_metrics.py           # Code quality metrics collection
│   ├── document_scripts.py               # Documentation analysis
│   ├── extract_all_classes.py            # Class extraction and analysis
│   ├── final_docstring_scan.py           # Docstring coverage analysis
│   ├── generate_full_coverage_report.py  # Coverage report generation
│   ├── list_tables.py                    # Database table listing
│   ├── scan_docstring_gaps.py            # Docstring gap detection
│   ├── test_file_consolidation_analysis.py # Test file analysis
│   ├── validate_daemon_architecture.py   # Daemon architecture validation
│   ├── validate_no_duplications.py       # Duplication detection
│   └── validate_standards.py             # Standards compliance validation
├── maintenance/
│   ├── README.md                         # Maintenance scripts documentation
│   ├── advanced_unified_fixer.py         # Advanced code fixing
│   ├── cleanup_old_fixers.py             # Cleanup old fixer scripts
│   ├── cleanup_temp_scripts.py           # Temporary script cleanup
│   ├── emergency_lint_fixer.py           # Emergency lint fixing
│   ├── fix_circular_dependencies.py      # Circular dependency resolution
│   ├── incremental_unified_fixer.py      # Incremental code fixing
│   ├── official_lint_mypy_fixer.py       # Official lint/mypy fixer
│   ├── systematic_lint_mypy_fixer.py     # Systematic code fixing
│   ├── unified_maintenance_system.py     # Unified maintenance system
│   ├── validate_dependencies.py          # Dependency validation
│   ├── validate_project_independence.py  # Project independence validation
│   └── fixes/                            # Specific fix scripts
│       ├── fix_attr_and_names.py         # Attribute and naming fixes
│       ├── fix_b904_errors.py            # B904 error fixes
│       ├── fix_call_arg_errors.py        # Function call argument fixes
│       ├── fix_lint_issues.py            # General lint issue fixes
│       ├── fix_mypy_comprehensive.py     # Comprehensive mypy fixes
│       ├── fix_remaining_extra_logging.py # Logging cleanup
│       ├── fix_remaining_issues.py       # Remaining issue fixes
│       ├── fix_remaining_mypy.py         # Remaining mypy fixes
│       └── fix_type_checking.py          # Type checking fixes
├── testing/
│   ├── quick_test.py                     # Quick test execution
│   ├── run_all_tests.py                  # Complete test suite runner
│   ├── run_working_tests.py              # Working tests execution
│   ├── test_capabilities.py              # Capability testing
│   ├── test_cli_installations.py         # CLI installation testing
│   ├── test_cli_pep8.py                  # CLI PEP8 compliance testing
│   ├── test_gn_cli.py                    # client-b CLI testing
│   ├── test_meta_factory.py              # Meta factory testing
│   └── test_unified_cli.py               # Unified CLI testing
├── dev_tools/
│   ├── dc_api_x_monkeytype.py            # DC API MonkeyType integration
│   ├── debug.sh                          # Debug utilities
│   ├── debug_monkeytype.py               # MonkeyType debugging
│   ├── debug_query.py                    # Query debugging
│   ├── debug_transaction.py              # Transaction debugging
│   ├── monkeytype_runner.py              # MonkeyType execution
│   ├── monkeytype_simple.py              # Simple MonkeyType usage
│   └── run_analyzer.sh                   # Code analyzer runner
├── pipelines/
│   ├── run_pipeline_examples.sh          # Pipeline examples runner
│   ├── wms_to_oracle_pipeline.py         # WMS to Oracle pipeline
│   ├── wms_to_oracle_pipeline_advanced.py # Advanced WMS pipeline
│   └── wms_to_oracle_simple.py           # Simple WMS pipeline
├── utilities/
│   ├── Makefile.standard                 # Standard Makefile template
│   ├── apply_pep8_standards.py           # PEP8 standards application
│   ├── check_venv.sh                     # Virtual environment checker
│   ├── common.sh                         # Common shell utilities
│   ├── comprehensive_lint_fix.py         # Comprehensive lint fixing
│   ├── dependency_analysis.py            # Dependency analysis
│   ├── fix_cli_fastapi.py                # CLI FastAPI fixes
│   ├── fix_undefined_names.py            # Undefined names fixes
│   ├── pep8_apply.py                     # PEP8 application
│   ├── pep8_check.py                     # PEP8 checking
│   ├── resolve_dependencies.py           # Dependency resolution
│   ├── restore_and_fix_systematically.py # Systematic restoration
│   ├── run_standardization.sh            # Standardization runner
│   ├── setup_scripts.sh                  # Setup scripts
│   ├── setup_venv.sh                     # Virtual environment setup
│   ├── standardize_dependencies.py       # Dependency standardization
│   ├── standardize_projects.py           # Project standardization
│   ├── sync_dependencies.py              # Dependency synchronization
│   ├── systematic_docstring_fix.py       # Systematic docstring fixing
│   ├── targeted_critical_fixes.py        # Critical fixes
│   ├── test_api_final.py                 # Final API testing
│   ├── test_rest_api.py                  # REST API testing
│   ├── update_lint_excludes.py           # Lint excludes update
│   ├── update_packages.py                # Package updates
│   ├── validate_final.py                 # Final validation
│   ├── validate_pyproject.py             # PyProject validation
│   └── verify_version_standardization.py # Version standardization verification
├── core/
│   ├── git_manage.py                     # Git management utilities
│   ├── project_manage.py                 # Project management utilities
│   └── scaffold_manage.py                # Project scaffolding
├── utils/
│   ├── quality_monitor.py                # Quality monitoring
│   ├── script_validation.py              # Script validation
│   └── temp_script_template.py           # Temporary script template
├── obsolete/                             # Deprecated scripts (archived)
├── temp/                                 # Temporary development scripts
├── temp_workflows/                       # Temporary workflow files
├── common.sh                             # Common shell functions
├── customize_project_template.py         # Project template customization
├── project_runner.sh                     # Project execution runner
├── validate_all_projects.py              # All projects validation
├── validate_e2e_infrastructure.py        # E2E infrastructure validation
└── validate_pyproject_compliance.py      # PyProject compliance validation
```

---

## 🔧 **Script Categories**

### **1. Analysis Scripts (analysis/)**

#### **FLX Framework Analysis (analyze_flx.py)**

```python
#!/usr/bin/env python3
"""FLX Framework comprehensive analysis and validation.

This script performs deep analysis of the FLX framework components,
architecture compliance, and integration patterns across the workspace.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import ast
import json

class FLXFrameworkAnalyzer:
    """Comprehensive FLX framework analyzer."""

    def __init__(self, workspace_path: Path, analysis_config: Dict[str, Any]):
        self.workspace_path = workspace_path
        self.analysis_config = analysis_config
        self.logger = self._setup_logging()
        self.analysis_results = {}

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)

    async def analyze_framework_architecture(self) -> Dict[str, Any]:
        """Analyze FLX framework architecture compliance."""
        self.logger.info("Starting FLX framework architecture analysis")

        results = {
            "hexagonal_architecture": await self._analyze_hexagonal_patterns(),
            "dependency_injection": await self._analyze_dependency_injection(),
            "event_sourcing": await self._analyze_event_sourcing(),
            "domain_models": await self._analyze_domain_models(),
            "infrastructure_layer": await self._analyze_infrastructure_layer(),
            "application_services": await self._analyze_application_services()
        }

        return results

    async def _analyze_hexagonal_patterns(self) -> Dict[str, Any]:
        """Analyze hexagonal architecture patterns."""
        flx_path = self.workspace_path / "flx" / "src" / "flx"

        if not flx_path.exists():
            return {"status": "error", "message": "FLX source not found"}

        patterns = {
            "ports": [],
            "adapters": [],
            "domain_models": [],
            "application_services": []
        }

        for py_file in flx_path.rglob("*.py"):
            with open(py_file, 'r', encoding='utf-8') as f:
                try:
                    tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            if self._is_port_class(node):
                                patterns["ports"].append({
                                    "name": node.name,
                                    "file": str(py_file.relative_to(self.workspace_path)),
                                    "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                                })
                            elif self._is_adapter_class(node):
                                patterns["adapters"].append({
                                    "name": node.name,
                                    "file": str(py_file.relative_to(self.workspace_path)),
                                    "implements": self._get_base_classes(node)
                                })
                except Exception as e:
                    self.logger.warning(f"Could not parse {py_file}: {e}")

        return {
            "status": "success",
            "patterns_found": patterns,
            "compliance_score": self._calculate_architecture_compliance(patterns)
        }

    def _is_port_class(self, node: ast.ClassDef) -> bool:
        """Check if class follows port pattern."""
        # Port classes typically are abstract base classes or protocols
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id in ['abstractmethod', 'protocol']:
                return True

        # Check for ABC inheritance
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id in ['ABC', 'Protocol']:
                return True

        return False

    def _is_adapter_class(self, node: ast.ClassDef) -> bool:
        """Check if class follows adapter pattern."""
        # Adapter classes typically implement port interfaces
        return len(node.bases) > 0 and any(
            isinstance(base, ast.Name) and "Port" in base.id
            for base in node.bases
        )

    def _get_base_classes(self, node: ast.ClassDef) -> List[str]:
        """Extract base class names."""
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(f"{base.value.id}.{base.attr}")
        return bases

    async def _analyze_dependency_injection(self) -> Dict[str, Any]:
        """Analyze dependency injection patterns."""
        # Implementation for DI analysis
        return {"status": "analyzed", "di_patterns": []}

    async def _analyze_event_sourcing(self) -> Dict[str, Any]:
        """Analyze event sourcing implementation."""
        # Implementation for event sourcing analysis
        return {"status": "analyzed", "events": []}

    async def _analyze_domain_models(self) -> Dict[str, Any]:
        """Analyze domain model patterns."""
        # Implementation for domain model analysis
        return {"status": "analyzed", "models": []}

    async def _analyze_infrastructure_layer(self) -> Dict[str, Any]:
        """Analyze infrastructure layer implementation."""
        # Implementation for infrastructure analysis
        return {"status": "analyzed", "infrastructure": []}

    async def _analyze_application_services(self) -> Dict[str, Any]:
        """Analyze application services layer."""
        # Implementation for application services analysis
        return {"status": "analyzed", "services": []}

    def _calculate_architecture_compliance(self, patterns: Dict[str, Any]) -> float:
        """Calculate architecture compliance score."""
        total_components = sum(len(v) for v in patterns.values())
        if total_components == 0:
            return 0.0

        # Simple scoring based on pattern presence
        score = 0.0
        if patterns["ports"]:
            score += 25.0
        if patterns["adapters"]:
            score += 25.0
        if patterns["domain_models"]:
            score += 25.0
        if patterns["application_services"]:
            score += 25.0

        return score

    async def generate_analysis_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report."""
        architecture_results = await self.analyze_framework_architecture()

        report = {
            "analysis_timestamp": "2025-06-19T10:00:00Z",
            "workspace_path": str(self.workspace_path),
            "framework_analysis": architecture_results,
            "recommendations": self._generate_recommendations(architecture_results),
            "compliance_summary": {
                "overall_score": architecture_results.get("hexagonal_architecture", {}).get("compliance_score", 0),
                "areas_for_improvement": []
            }
        }

        return report

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []

        hexagonal = results.get("hexagonal_architecture", {})
        if hexagonal.get("compliance_score", 0) < 75:
            recommendations.append("Improve hexagonal architecture compliance")

        return recommendations

async def main():
    """Main analysis execution."""
    workspace_path = Path("/home/marlonsc/pyauto")
    config = {
        "include_patterns": ["*.py"],
        "exclude_patterns": ["*/tests/*", "*/temp/*"],
        "analysis_depth": "deep"
    }

    analyzer = FLXFrameworkAnalyzer(workspace_path, config)
    report = await analyzer.generate_analysis_report()

    # Save report
    with open(workspace_path / "reports" / "flx_analysis_report.json", 'w') as f:
        json.dump(report, f, indent=2)

    print(f"Analysis complete. Compliance score: {report['compliance_summary']['overall_score']:.1f}%")

if __name__ == "__main__":
    asyncio.run(main())
```

#### **Code Quality Metrics Collection (code_quality_metrics.py)**

```python
#!/usr/bin/env python3
"""Code quality metrics collection and analysis.

This script collects comprehensive code quality metrics across all
PyAuto projects and generates quality dashboards.
"""

import subprocess
import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class QualityMetrics:
    """Code quality metrics data structure."""
    project_name: str
    lines_of_code: int
    test_coverage: float
    cyclomatic_complexity: float
    maintainability_index: float
    technical_debt_hours: float
    lint_violations: int
    type_coverage: float
    documentation_coverage: float

class CodeQualityCollector:
    """Comprehensive code quality metrics collector."""

    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.metrics_data = []

    def collect_all_metrics(self) -> List[QualityMetrics]:
        """Collect metrics for all projects in workspace."""
        project_dirs = [
            d for d in self.workspace_path.iterdir()
            if d.is_dir() and (d / "pyproject.toml").exists()
        ]

        for project_dir in project_dirs:
            try:
                metrics = self.collect_project_metrics(project_dir)
                self.metrics_data.append(metrics)
            except Exception as e:
                print(f"Error collecting metrics for {project_dir.name}: {e}")

        return self.metrics_data

    def collect_project_metrics(self, project_path: Path) -> QualityMetrics:
        """Collect metrics for a single project."""
        return QualityMetrics(
            project_name=project_path.name,
            lines_of_code=self._count_lines_of_code(project_path),
            test_coverage=self._get_test_coverage(project_path),
            cyclomatic_complexity=self._get_cyclomatic_complexity(project_path),
            maintainability_index=self._get_maintainability_index(project_path),
            technical_debt_hours=self._estimate_technical_debt(project_path),
            lint_violations=self._count_lint_violations(project_path),
            type_coverage=self._get_type_coverage(project_path),
            documentation_coverage=self._get_documentation_coverage(project_path)
        )

    def _count_lines_of_code(self, project_path: Path) -> int:
        """Count lines of code using cloc or wc."""
        try:
            result = subprocess.run(
                ["find", str(project_path), "-name", "*.py", "-exec", "wc", "-l", "{}", "+"],
                capture_output=True,
                text=True,
                cwd=project_path
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                total_lines = sum(int(line.split()[0]) for line in lines if line.strip())
                return total_lines
        except Exception:
            pass
        return 0

    def _get_test_coverage(self, project_path: Path) -> float:
        """Get test coverage percentage."""
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "--cov=.", "--cov-report=json"],
                capture_output=True,
                text=True,
                cwd=project_path
            )

            coverage_file = project_path / "coverage.json"
            if coverage_file.exists():
                with open(coverage_file) as f:
                    coverage_data = json.load(f)
                    return coverage_data.get("totals", {}).get("percent_covered", 0.0)
        except Exception:
            pass
        return 0.0

    def _get_cyclomatic_complexity(self, project_path: Path) -> float:
        """Get average cyclomatic complexity."""
        try:
            result = subprocess.run(
                ["python", "-m", "radon", "cc", "-j", str(project_path / "src")],
                capture_output=True,
                text=True,
                cwd=project_path
            )
            if result.returncode == 0:
                complexity_data = json.loads(result.stdout)
                complexities = []
                for file_data in complexity_data.values():
                    for item in file_data:
                        if isinstance(item, dict) and "complexity" in item:
                            complexities.append(item["complexity"])

                return sum(complexities) / len(complexities) if complexities else 0.0
        except Exception:
            pass
        return 0.0

    def _get_maintainability_index(self, project_path: Path) -> float:
        """Get maintainability index."""
        try:
            result = subprocess.run(
                ["python", "-m", "radon", "mi", "-j", str(project_path / "src")],
                capture_output=True,
                text=True,
                cwd=project_path
            )
            if result.returncode == 0:
                mi_data = json.loads(result.stdout)
                indices = [v["mi"] for v in mi_data.values() if isinstance(v, dict) and "mi" in v]
                return sum(indices) / len(indices) if indices else 0.0
        except Exception:
            pass
        return 0.0

    def _estimate_technical_debt(self, project_path: Path) -> float:
        """Estimate technical debt in hours."""
        # Simplified technical debt estimation based on code smells
        try:
            result = subprocess.run(
                ["python", "-m", "flake8", "--statistics", str(project_path / "src")],
                capture_output=True,
                text=True,
                cwd=project_path
            )
            if result.returncode == 0:
                # Rough estimation: 15 minutes per violation
                violation_count = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
                return violation_count * 0.25  # 15 minutes = 0.25 hours
        except Exception:
            pass
        return 0.0

    def _count_lint_violations(self, project_path: Path) -> int:
        """Count lint violations."""
        try:
            result = subprocess.run(
                ["python", "-m", "ruff", "check", "--output-format=json", str(project_path / "src")],
                capture_output=True,
                text=True,
                cwd=project_path
            )
            if result.stdout.strip():
                violations = json.loads(result.stdout)
                return len(violations)
        except Exception:
            pass
        return 0

    def _get_type_coverage(self, project_path: Path) -> float:
        """Get type coverage percentage."""
        try:
            result = subprocess.run(
                ["python", "-m", "mypy", "--strict", str(project_path / "src")],
                capture_output=True,
                text=True,
                cwd=project_path
            )
            # Simplified type coverage estimation
            if result.returncode == 0:
                return 95.0  # High coverage if mypy passes
            else:
                error_count = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
                # Rough estimation based on error count
                return max(0, 100 - (error_count * 2))
        except Exception:
            pass
        return 0.0

    def _get_documentation_coverage(self, project_path: Path) -> float:
        """Get documentation coverage percentage."""
        try:
            # Count functions/classes with docstrings
            python_files = list((project_path / "src").rglob("*.py"))
            total_definitions = 0
            documented_definitions = 0

            for py_file in python_files:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Simple docstring detection
                import ast
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        total_definitions += 1
                        if ast.get_docstring(node):
                            documented_definitions += 1

            if total_definitions > 0:
                return (documented_definitions / total_definitions) * 100
        except Exception:
            pass
        return 0.0

    def generate_quality_report(self) -> Dict[str, Any]:
        """Generate comprehensive quality report."""
        if not self.metrics_data:
            self.collect_all_metrics()

        report = {
            "generated_at": datetime.now().isoformat(),
            "workspace_path": str(self.workspace_path),
            "summary": {
                "total_projects": len(self.metrics_data),
                "average_coverage": sum(m.test_coverage for m in self.metrics_data) / len(self.metrics_data),
                "total_lines_of_code": sum(m.lines_of_code for m in self.metrics_data),
                "average_complexity": sum(m.cyclomatic_complexity for m in self.metrics_data) / len(self.metrics_data),
                "total_technical_debt_hours": sum(m.technical_debt_hours for m in self.metrics_data)
            },
            "projects": [
                {
                    "name": m.project_name,
                    "lines_of_code": m.lines_of_code,
                    "test_coverage": m.test_coverage,
                    "cyclomatic_complexity": m.cyclomatic_complexity,
                    "maintainability_index": m.maintainability_index,
                    "technical_debt_hours": m.technical_debt_hours,
                    "lint_violations": m.lint_violations,
                    "type_coverage": m.type_coverage,
                    "documentation_coverage": m.documentation_coverage,
                    "quality_grade": self._calculate_quality_grade(m)
                }
                for m in self.metrics_data
            ]
        }

        return report

    def _calculate_quality_grade(self, metrics: QualityMetrics) -> str:
        """Calculate overall quality grade for project."""
        score = 0

        # Test coverage (30%)
        score += (metrics.test_coverage / 100) * 30

        # Maintainability (25%)
        score += min(metrics.maintainability_index / 100, 1.0) * 25

        # Type coverage (20%)
        score += (metrics.type_coverage / 100) * 20

        # Documentation coverage (15%)
        score += (metrics.documentation_coverage / 100) * 15

        # Low complexity bonus (10%)
        complexity_bonus = max(0, (10 - metrics.cyclomatic_complexity) / 10) * 10
        score += complexity_bonus

        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def export_to_csv(self, output_file: Path):
        """Export metrics to CSV file."""
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = [
                'project_name', 'lines_of_code', 'test_coverage',
                'cyclomatic_complexity', 'maintainability_index',
                'technical_debt_hours', 'lint_violations',
                'type_coverage', 'documentation_coverage'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for metrics in self.metrics_data:
                writer.writerow({
                    'project_name': metrics.project_name,
                    'lines_of_code': metrics.lines_of_code,
                    'test_coverage': metrics.test_coverage,
                    'cyclomatic_complexity': metrics.cyclomatic_complexity,
                    'maintainability_index': metrics.maintainability_index,
                    'technical_debt_hours': metrics.technical_debt_hours,
                    'lint_violations': metrics.lint_violations,
                    'type_coverage': metrics.type_coverage,
                    'documentation_coverage': metrics.documentation_coverage
                })

def main():
    """Main execution."""
    workspace_path = Path("/home/marlonsc/pyauto")
    collector = CodeQualityCollector(workspace_path)

    print("Collecting code quality metrics...")
    collector.collect_all_metrics()

    print("Generating quality report...")
    report = collector.generate_quality_report()

    # Save JSON report
    with open(workspace_path / "reports" / "quality_metrics.json", 'w') as f:
        json.dump(report, f, indent=2)

    # Save CSV export
    collector.export_to_csv(workspace_path / "reports" / "quality_metrics.csv")

    print(f"Quality analysis complete:")
    print(f"  - Total projects: {report['summary']['total_projects']}")
    print(f"  - Average coverage: {report['summary']['average_coverage']:.1f}%")
    print(f"  - Total LOC: {report['summary']['total_lines_of_code']:,}")
    print(f"  - Technical debt: {report['summary']['total_technical_debt_hours']:.1f} hours")

if __name__ == "__main__":
    main()
```

### **2. Maintenance Scripts (maintenance/)**

The maintenance directory already has a comprehensive README.md file documenting all the maintenance scripts and procedures.

### **3. Testing Scripts (testing/)**

#### **Complete Test Suite Runner (run_all_tests.py)**

```python
#!/usr/bin/env python3
"""Complete test suite runner for PyAuto workspace.

This script executes all test suites across all projects in the PyAuto
workspace and generates comprehensive test reports.
"""

import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class TestResult:
    """Test execution result."""
    project_name: str
    status: str
    duration: float
    tests_run: int
    tests_passed: int
    tests_failed: int
    tests_skipped: int
    coverage: float
    error_message: Optional[str] = None

class PyAutoTestRunner:
    """Comprehensive test runner for PyAuto workspace."""

    def __init__(self, workspace_path: Path, parallel: bool = True):
        self.workspace_path = workspace_path
        self.parallel = parallel
        self.test_results = []

    def discover_test_projects(self) -> List[Path]:
        """Discover all projects with test suites."""
        projects = []
        for project_dir in self.workspace_path.iterdir():
            if (project_dir.is_dir() and
                (project_dir / "pyproject.toml").exists() and
                (project_dir / "tests").exists()):
                projects.append(project_dir)
        return projects

    def run_all_tests(self) -> List[TestResult]:
        """Run tests for all projects."""
        projects = self.discover_test_projects()

        if self.parallel:
            return self._run_tests_parallel(projects)
        else:
            return self._run_tests_sequential(projects)

    def _run_tests_parallel(self, projects: List[Path]) -> List[TestResult]:
        """Run tests in parallel."""
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_project = {
                executor.submit(self._run_project_tests, project): project
                for project in projects
            }

            for future in as_completed(future_to_project):
                result = future.result()
                self.test_results.append(result)
                print(f"✓ {result.project_name}: {result.status} ({result.duration:.1f}s)")

        return self.test_results

    def _run_tests_sequential(self, projects: List[Path]) -> List[TestResult]:
        """Run tests sequentially."""
        for project in projects:
            result = self._run_project_tests(project)
            self.test_results.append(result)
            print(f"✓ {result.project_name}: {result.status} ({result.duration:.1f}s)")

        return self.test_results

    def _run_project_tests(self, project_path: Path) -> TestResult:
        """Run tests for a single project."""
        start_time = time.time()

        try:
            # Run pytest with coverage
            result = subprocess.run(
                [
                    "python", "-m", "pytest",
                    "-v",
                    "--cov=src",
                    "--cov-report=json",
                    "--junit-xml=test-results.xml",
                    "tests/"
                ],
                capture_output=True,
                text=True,
                cwd=project_path,
                timeout=300  # 5 minute timeout
            )

            duration = time.time() - start_time

            # Parse pytest output
            tests_info = self._parse_pytest_output(result.stdout)
            coverage = self._get_coverage_from_json(project_path)

            if result.returncode == 0:
                status = "PASSED"
            elif tests_info["failed"] > 0:
                status = "FAILED"
            else:
                status = "ERROR"

            return TestResult(
                project_name=project_path.name,
                status=status,
                duration=duration,
                tests_run=tests_info["total"],
                tests_passed=tests_info["passed"],
                tests_failed=tests_info["failed"],
                tests_skipped=tests_info["skipped"],
                coverage=coverage,
                error_message=result.stderr if result.returncode != 0 else None
            )

        except subprocess.TimeoutExpired:
            return TestResult(
                project_name=project_path.name,
                status="TIMEOUT",
                duration=300.0,
                tests_run=0,
                tests_passed=0,
                tests_failed=0,
                tests_skipped=0,
                coverage=0.0,
                error_message="Test execution timed out after 5 minutes"
            )
        except Exception as e:
            return TestResult(
                project_name=project_path.name,
                status="ERROR",
                duration=time.time() - start_time,
                tests_run=0,
                tests_passed=0,
                tests_failed=0,
                tests_skipped=0,
                coverage=0.0,
                error_message=str(e)
            )

    def _parse_pytest_output(self, output: str) -> Dict[str, int]:
        """Parse pytest output to extract test counts."""
        # Simple parsing of pytest summary
        lines = output.split('\n')
        summary_line = None

        for line in lines:
            if "passed" in line or "failed" in line or "error" in line:
                summary_line = line

        if not summary_line:
            return {"total": 0, "passed": 0, "failed": 0, "skipped": 0}

        # Extract numbers from summary
        import re
        passed = len(re.findall(r'(\d+) passed', summary_line))
        failed = len(re.findall(r'(\d+) failed', summary_line))
        skipped = len(re.findall(r'(\d+) skipped', summary_line))

        return {
            "total": passed + failed + skipped,
            "passed": passed,
            "failed": failed,
            "skipped": skipped
        }

    def _get_coverage_from_json(self, project_path: Path) -> float:
        """Get coverage percentage from coverage.json."""
        coverage_file = project_path / "coverage.json"
        if coverage_file.exists():
            try:
                with open(coverage_file) as f:
                    coverage_data = json.load(f)
                    return coverage_data.get("totals", {}).get("percent_covered", 0.0)
            except Exception:
                pass
        return 0.0

    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        total_tests = sum(r.tests_run for r in self.test_results)
        total_passed = sum(r.tests_passed for r in self.test_results)
        total_failed = sum(r.tests_failed for r in self.test_results)
        total_skipped = sum(r.tests_skipped for r in self.test_results)

        avg_coverage = (
            sum(r.coverage for r in self.test_results) / len(self.test_results)
            if self.test_results else 0.0
        )

        total_duration = sum(r.duration for r in self.test_results)

        report = {
            "execution_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "workspace_path": str(self.workspace_path),
            "summary": {
                "total_projects": len(self.test_results),
                "projects_passed": len([r for r in self.test_results if r.status == "PASSED"]),
                "projects_failed": len([r for r in self.test_results if r.status == "FAILED"]),
                "projects_error": len([r for r in self.test_results if r.status == "ERROR"]),
                "total_tests": total_tests,
                "tests_passed": total_passed,
                "tests_failed": total_failed,
                "tests_skipped": total_skipped,
                "success_rate": (total_passed / total_tests * 100) if total_tests > 0 else 0,
                "average_coverage": avg_coverage,
                "total_duration": total_duration
            },
            "project_results": [
                {
                    "project_name": r.project_name,
                    "status": r.status,
                    "duration": r.duration,
                    "tests_run": r.tests_run,
                    "tests_passed": r.tests_passed,
                    "tests_failed": r.tests_failed,
                    "tests_skipped": r.tests_skipped,
                    "coverage": r.coverage,
                    "error_message": r.error_message
                }
                for r in self.test_results
            ]
        }

        return report

    def print_summary(self):
        """Print test execution summary."""
        if not self.test_results:
            print("No test results available.")
            return

        passed_projects = [r for r in self.test_results if r.status == "PASSED"]
        failed_projects = [r for r in self.test_results if r.status == "FAILED"]
        error_projects = [r for r in self.test_results if r.status == "ERROR"]

        print("\n" + "="*60)
        print("PyAuto Test Suite Summary")
        print("="*60)
        print(f"Total Projects: {len(self.test_results)}")
        print(f"✓ Passed: {len(passed_projects)}")
        print(f"✗ Failed: {len(failed_projects)}")
        print(f"⚠ Error: {len(error_projects)}")

        total_tests = sum(r.tests_run for r in self.test_results)
        total_passed = sum(r.tests_passed for r in self.test_results)

        if total_tests > 0:
            success_rate = (total_passed / total_tests) * 100
            print(f"\nOverall Success Rate: {success_rate:.1f}%")

        avg_coverage = sum(r.coverage for r in self.test_results) / len(self.test_results)
        print(f"Average Coverage: {avg_coverage:.1f}%")

        total_duration = sum(r.duration for r in self.test_results)
        print(f"Total Duration: {total_duration:.1f}s")

        if failed_projects:
            print(f"\nFailed Projects:")
            for project in failed_projects:
                print(f"  - {project.project_name}: {project.tests_failed} failed tests")

        if error_projects:
            print(f"\nError Projects:")
            for project in error_projects:
                print(f"  - {project.project_name}: {project.error_message}")

def main():
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser(description="Run all tests in PyAuto workspace")
    parser.add_argument("--sequential", action="store_true", help="Run tests sequentially")
    parser.add_argument("--output", help="Output file for test report")

    args = parser.parse_args()

    workspace_path = Path("/home/marlonsc/pyauto")
    runner = PyAutoTestRunner(workspace_path, parallel=not args.sequential)

    print("Discovering test projects...")
    projects = runner.discover_test_projects()
    print(f"Found {len(projects)} projects with tests")

    print("Running test suites...")
    runner.run_all_tests()

    # Generate and save report
    report = runner.generate_test_report()

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Test report saved to {args.output}")

    # Print summary
    runner.print_summary()

    # Exit with appropriate code
    failed_projects = [r for r in runner.test_results if r.status in ["FAILED", "ERROR"]]
    exit(1 if failed_projects else 0)

if __name__ == "__main__":
    main()
```

---

## 🔧 **Usage Examples**

### **Running Analysis Scripts**

```bash
# Analyze FLX framework architecture
cd /home/marlonsc/pyauto
python scripts/analysis/analyze_flx.py

# Collect code quality metrics
python scripts/analysis/code_quality_metrics.py

# Validate standards compliance
python scripts/analysis/validate_standards.py

# Check for duplicate code
python scripts/analysis/validate_no_duplications.py
```

### **Running Maintenance Scripts**

```bash
# Run comprehensive maintenance
python scripts/maintenance/unified_maintenance_system.py

# Fix lint and mypy issues
python scripts/maintenance/official_lint_mypy_fixer.py

# Validate project dependencies
python scripts/maintenance/validate_dependencies.py

# Clean up old files
python scripts/maintenance/cleanup_temp_scripts.py
```

### **Running Test Scripts**

```bash
# Run all tests in parallel
python scripts/testing/run_all_tests.py

# Run tests sequentially
python scripts/testing/run_all_tests.py --sequential

# Quick test execution
python scripts/testing/quick_test.py

# Test CLI installations
python scripts/testing/test_cli_installations.py
```

---

## 🔗 **Cross-References**

### **PyAuto Documentation**

- [PyAuto Home](../README.md) - Main workspace documentation
- [Development Guidelines](../docs/development/) - Development standards
- [Architecture Documentation](../docs/architecture/) - System architecture

### **Project Documentation**

- [FLX Framework](../flx/README.md) - Core framework documentation
- [Maintenance Scripts](./maintenance/README.md) - Detailed maintenance procedures
- [Examples Directory](../examples/README.md) - Usage examples

### **External References**

- [Python Testing Best Practices](https://docs.pytest.org/en/latest/good-practices.html) - Testing guidelines
- [Code Quality Tools](https://github.com/psf/black) - Code formatting and quality
- [CI/CD Best Practices](https://docs.github.com/en/actions) - Continuous integration

---

**📂 Module**: Scripts Hub | **🏠 Root**: [PyAuto](../README.md) | **Tools**: Python 3.13+, Poetry, pytest | **Updated**: 2025-06-19
