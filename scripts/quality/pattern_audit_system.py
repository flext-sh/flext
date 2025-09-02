#!/usr/bin/env python3
"""FLEXT Pattern Audit System - Enterprise Pattern Compliance Analysis."""

import argparse
import ast
import json
import logging
import re
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

from flext_core import FlextResult


@dataclass
class PatternViolation:
    """Represents a single pattern violation with complete context.

    Immutable value object containing all information needed to understand
    and remediate a specific pattern compliance violation.
    """

    file_path: str
    line_number: int
    violation_type: str
    severity_level: str  # CRITICAL, HIGH, MEDIUM, LOW
    current_code_snippet: str
    pattern_reference: str
    remediation_guidance: str
    architectural_context: str = ""
    business_impact: str = ""


@dataclass
class ProjectAuditResult:
    """Complete audit results for a single project.

    Domain entity representing the comprehensive audit state of a project
    including all violations, metrics, and compliance analysis.
    """

    project_name: str
    total_files_analyzed: int
    violations: list[PatternViolation] = field(default_factory=list)
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    compliance_score: float = 0.0
    audit_timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def calculate_compliance_metrics(self) -> None:
        """Calculate compliance score and update violation counts."""
        self.critical_count = len(
            [v for v in self.violations if v.severity_level == "CRITICAL"],
        )
        self.high_count = len(
            [v for v in self.violations if v.severity_level == "HIGH"],
        )
        self.medium_count = len(
            [v for v in self.violations if v.severity_level == "MEDIUM"],
        )
        self.low_count = len([v for v in self.violations if v.severity_level == "LOW"])

        # Calculate weighted compliance score
        total_violations = len(self.violations)
        if total_violations == 0:
            self.compliance_score = 100.0
        else:
            weighted_violations = (
                (self.critical_count * 4)
                + (self.high_count * 3)
                + (self.medium_count * 2)
                + (self.low_count * 1)
            )
            # Base score calculation with file normalization
            base_score = max(
                0,
                100 - (weighted_violations / max(self.total_files_analyzed, 1)) * 20,
            )
            self.compliance_score = round(base_score, 1)


@dataclass
class EcosystemAuditResult:
    """Complete audit results for the entire FLEXT ecosystem.

    Aggregate entity containing compliance analysis across all projects
    with ecosystem-wide metrics and prioritized remediation guidance.
    """

    total_projects_audited: int
    projects_results: dict[str, ProjectAuditResult] = field(default_factory=dict)
    ecosystem_compliance_score: float = 0.0
    total_violations_count: int = 0
    critical_violations_count: int = 0
    high_violations_count: int = 0
    projects_with_critical_issues: list[str] = field(default_factory=list)
    fully_compliant_projects: list[str] = field(default_factory=list)
    audit_timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def calculate_ecosystem_metrics(self) -> None:
        """Calculate ecosystem-wide compliance metrics."""
        if not self.projects_results:
            return

        # Calculate totals
        self.total_violations_count = sum(
            len(r.violations) for r in self.projects_results.values()
        )
        self.critical_violations_count = sum(
            r.critical_count for r in self.projects_results.values()
        )
        self.high_violations_count = sum(
            r.high_count for r in self.projects_results.values()
        )

        # Calculate ecosystem compliance (weighted average)
        total_files = sum(
            r.total_files_analyzed for r in self.projects_results.values()
        )
        if total_files > 0:
            weighted_score = sum(
                r.compliance_score * r.total_files_analyzed
                for r in self.projects_results.values()
            )
            self.ecosystem_compliance_score = round(weighted_score / total_files, 1)

        # Categorize projects
        self.projects_with_critical_issues = [
            name
            for name, result in self.projects_results.items()
            if result.critical_count > 0
        ]
        self.fully_compliant_projects = [
            name
            for name, result in self.projects_results.items()
            if len(result.violations) == 0
        ]


class PatternViolationAnalyzer:
    """Core engine for analyzing pattern violations across FLEXT projects."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.pattern_docs_path = (
            Path(__file__).parent.parent.parent / "docs" / "patterns"
        )

        # Define pattern detection rules without automatic fixes
        self._initialize_pattern_rules()

    def _initialize_pattern_rules(self) -> None:
        """Initialize pattern detection rules for different violation categories."""
        # Foundation pattern violations
        self.foundation_violations = {
            "BaseModel": {
                "severity": "CRITICAL",
                "pattern": "foundation.md#FlextModels",
                "context": "Use FlextModels/FlextModels/FlextModels instead of direct BaseModel",
                "guidance": "Replace with appropriate FLEXT foundation class",
            },
            "validate_domain_rules": {
                "severity": "CRITICAL",
                "pattern": "foundation.md#business-rules",
                "context": "Use validate_business_rules for consistency",
                "guidance": "Rename method to validate_business_rules",
            },
        }

        # Type system violations
        self.type_system_violations = {
            "Dict[str, object]": {
                "severity": "CRITICAL",
                "pattern": "types.md#FlextTypes",
                "context": "Use FlextTypes namespace for semantic type definitions",
                "guidance": "Replace with FlextTypes.Core.JsonDict",
            },
            "List[dict]": {
                "severity": "HIGH",
                "pattern": "types.md#data-types",
                "context": "Use semantic data type definitions",
                "guidance": "Replace with FlextTypes.Data.RecordBatch",
            },
        }

        # Configuration pattern violations
        self.config_violations = {
            r"os\.getenv": {
                "severity": "MEDIUM",
                "pattern": "config-cli.md#hierarchical-config",
                "context": "Use hierarchical configuration instead of direct environment access",
                "guidance": "Use FlextConfigHierarchical.get_value()",
            },
            "BaseSettings": {
                "severity": "HIGH",
                "pattern": "config-cli.md#FlextConfig",
                "context": "Use FLEXT configuration patterns",
                "guidance": "Replace with FlextConfig base class",
            },
        }

        # Constants violations
        self.constants_violations = {
            r"timeout=\d+": {
                "severity": "HIGH",
                "pattern": "constants.md#semantic-constants",
                "context": "Use semantic constants for maintainability",
                "guidance": "Replace with FlextConstants.Defaults.TIMEOUT",
            },
            r"port=\d+": {
                "severity": "MEDIUM",
                "pattern": "constants.md#service-constants",
                "context": "Use service-specific constants",
                "guidance": "Replace with FlextConstants.Services.DEFAULT_PORT",
            },
        }

    def analyze_project_compliance(
        self,
        project_path: Path,
    ) -> FlextResult[ProjectAuditResult]:
        """Analyze pattern compliance for a single project."""
        try:
            if not project_path.exists():
                return FlextResult[ProjectAuditResult].fail(
                    f"Project path does not exist: {project_path}"
                )

            # Find Python files to analyze
            if project_path.name == "main-workspace":
                # For main workspace, scan src/ directory
                src_path = project_path / "src"
                python_files = (
                    list(src_path.glob("**/*.py")) if src_path.exists() else []
                )
            else:
                python_files = list(project_path.glob("**/*.py"))

            if not python_files:
                # Return empty result for projects without Python files
                result = ProjectAuditResult(
                    project_name=project_path.name,
                    total_files_analyzed=0,
                )
                result.calculate_compliance_metrics()
                return FlextResult[ProjectAuditResult].ok(result)

            violations = []
            for python_file in python_files:
                file_violations_result = self._analyze_file_patterns(
                    python_file,
                    project_path.name,
                )
                if file_violations_result.success and file_violations_result.data:
                    violations.extend(file_violations_result.data)

            result = ProjectAuditResult(
                project_name=project_path.name,
                total_files_analyzed=len(python_files),
                violations=violations,
            )
            result.calculate_compliance_metrics()

            self.logger.info(
                f"Analyzed {project_path.name}: {len(violations)} violations found",
            )
            return FlextResult[ProjectAuditResult].ok(result)

        except Exception as e:
            self.logger.exception(f"Error analyzing project {project_path.name}")
            return FlextResult[ProjectAuditResult].fail(f"Analysis failed: {e}")

    def _analyze_file_patterns(
        self,
        file_path: Path,
        project_name: str,
    ) -> FlextResult[list[PatternViolation]]:
        """Analyze patterns in a single file."""
        try:
            with Path(file_path).open(encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.splitlines()

            violations = []

            # AST-based structural analysis
            try:
                tree = ast.parse(content)
                ast_violations = self._analyze_ast_patterns(
                    tree,
                    file_path,
                    lines,
                    project_name,
                )
                violations.extend(ast_violations)
            except SyntaxError:
                # Skip files with syntax errors but log for awareness
                self.logger.debug(f"Skipping file with syntax errors: {file_path}")

            # Text-based pattern analysis
            text_violations = self._analyze_text_patterns(
                file_path,
                lines,
                project_name,
            )
            violations.extend(text_violations)

            return FlextResult[list[PatternViolation]].ok(violations)

        except Exception as e:
            self.logger.debug(f"Error analyzing file {file_path}: {e}")
            return FlextResult[list[PatternViolation]].ok(
                []
            )  # Return empty list on file errors

    def _analyze_ast_patterns(
        self,
        tree: ast.AST,
        file_path: Path,
        lines: list[str],
        _project_name: str,
    ) -> list[PatternViolation]:
        """Analyze AST for structural pattern violations."""
        violations = []

        class PatternVisitor(ast.NodeVisitor):
            def __init__(self, analyzer: PatternViolationAnalyzer) -> None:
                self.analyzer = analyzer

            def visit_ClassDef(self, node: ast.ClassDef) -> None:
                # Check for BaseModel usage instead of FlextModels
                for base in node.bases:
                    if (
                        isinstance(base, ast.Name)
                        and base.id == "BaseModel"
                        and node.lineno <= len(lines)
                    ):
                        rule = self.analyzer.foundation_violations["BaseModel"]
                        violations.append(
                            PatternViolation(
                                file_path=str(file_path),
                                line_number=node.lineno,
                                violation_type="Foundation Pattern - BaseModel Usage",
                                severity_level=rule["severity"],
                                current_code_snippet=lines[node.lineno - 1].strip(),
                                pattern_reference=f"docs/patterns/{rule['pattern']}",
                                remediation_guidance=rule["guidance"],
                                architectural_context=rule["context"],
                                business_impact="Breaks foundation pattern consistency across ecosystem",
                            ),
                        )

                self.generic_visit(node)

            def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
                # Check for validate_domain_rules instead of validate_business_rules
                if node.name == "validate_domain_rules" and node.lineno <= len(lines):
                    rule = self.analyzer.foundation_violations["validate_domain_rules"]
                    violations.append(
                        PatternViolation(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            violation_type="Foundation Pattern - Method Naming",
                            severity_level=rule["severity"],
                            current_code_snippet=lines[node.lineno - 1].strip(),
                            pattern_reference=f"docs/patterns/{rule['pattern']}",
                            remediation_guidance=rule["guidance"],
                            architectural_context=rule["context"],
                            business_impact="Inconsistent method naming violates Single Source of Truth",
                        ),
                    )

                self.generic_visit(node)

        visitor = PatternVisitor(self)
        visitor.visit(tree)

        return violations

    def _analyze_text_patterns(
        self,
        file_path: Path,
        lines: list[str],
        _project_name: str,
    ) -> list[PatternViolation]:
        """Analyze text patterns for violations."""
        violations = []

        for line_num, line in enumerate(lines, 1):
            # Check type system violations
            for pattern, rule in self.type_system_violations.items():
                if pattern in line and "FlextTypes" not in line:
                    violations.append(
                        PatternViolation(
                            file_path=str(file_path),
                            line_number=line_num,
                            violation_type="Type System - Missing FlextTypes",
                            severity_level=rule["severity"],
                            current_code_snippet=line.strip(),
                            pattern_reference=f"docs/patterns/{rule['pattern']}",
                            remediation_guidance=rule["guidance"],
                            architectural_context=rule["context"],
                            business_impact="Reduces type safety and semantic clarity",
                        ),
                    )

            # Check configuration violations
            for pattern, rule in self.config_violations.items():
                if re.search(pattern, line):
                    violations.append(
                        PatternViolation(
                            file_path=str(file_path),
                            line_number=line_num,
                            violation_type="Configuration Pattern - Non-hierarchical Access",
                            severity_level=rule["severity"],
                            current_code_snippet=line.strip(),
                            pattern_reference=f"docs/patterns/{rule['pattern']}",
                            remediation_guidance=rule["guidance"],
                            architectural_context=rule["context"],
                            business_impact="Reduces configuration flexibility and maintainability",
                        ),
                    )

            # Check constants violations
            for pattern, rule in self.constants_violations.items():
                if re.search(pattern, line):
                    violations.append(
                        PatternViolation(
                            file_path=str(file_path),
                            line_number=line_num,
                            violation_type="Constants Pattern - Hardcoded Values",
                            severity_level=rule["severity"],
                            current_code_snippet=line.strip(),
                            pattern_reference=f"docs/patterns/{rule['pattern']}",
                            remediation_guidance=rule["guidance"],
                            architectural_context=rule["context"],
                            business_impact="Reduces maintainability and configuration flexibility",
                        ),
                    )

        return violations


class PatternAuditSystem:
    """Main script class for FLEXT Pattern Audit System."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.analyzer = PatternViolationAnalyzer()
        self.workspace_path = Path(__file__).parent.parent.parent
        # Add metadata for audit reporting

        self.metadata = SimpleNamespace(version="2.0.0")

    def validate_preconditions(self) -> bool:
        """Validate system is ready for pattern audit."""
        if not self.workspace_path.exists():
            self.logger.error(f"Workspace path not found: {self.workspace_path}")
            return False

        patterns_path = self.workspace_path / "docs" / "patterns"
        if not patterns_path.exists():
            self.logger.error(f"Pattern documentation not found: {patterns_path}")
            return False

        return True

    def run_audit(self) -> bool:
        """Execute comprehensive pattern audit across ecosystem."""
        try:
            # Audit ecosystem compliance
            audit_result = self.audit_ecosystem_compliance(self.workspace_path)
            if not audit_result.success:
                return False

            ecosystem_result = audit_result.data

            # Generate comprehensive report
            report_result = self.generate_compliance_report(ecosystem_result)
            return report_result.success

        except Exception:
            return False

    def audit_ecosystem_compliance(
        self,
        workspace_path: Path,
    ) -> FlextResult[EcosystemAuditResult]:
        """Audit pattern compliance across entire FLEXT ecosystem."""
        try:
            # Define all FLEXT projects
            projects = [
                "main-workspace",
                "flext-core",
                "flext-api",
                "flext-auth",
                "flext-cli",
                "flext-web",
                "flext-db-oracle",
                "flext-ldap",
                "flext-ldif",
                "flext-grpc",
                "flext-meltano",
                "flext-observability",
                "flext-oracle-wms",
                "flext-plugin",
                "flext-quality",
                "flext-oracle-oic-ext",
                "flext-tap-ldap",
                "flext-tap-ldif",
                "flext-tap-oracle",
                "flext-tap-oracle-oic",
                "flext-tap-oracle-wms",
                "flext-target-ldap",
                "flext-target-ldif",
                "flext-target-oracle",
                "flext-target-oracle-oic",
                "flext-target-oracle-wms",
                "flext-dbt-ldap",
                "flext-dbt-ldif",
                "flext-dbt-oracle",
                "flext-dbt-oracle-wms",
                "client-a-oud-mig",
                "client-b-meltano-native",
            ]

            results = {}

            for project_name in projects:
                if project_name == "main-workspace":
                    project_path = workspace_path  # Main workspace is the root
                else:
                    project_path = workspace_path / project_name

                self.logger.info(f"Auditing {project_name}...")
                project_result = self.analyzer.analyze_project_compliance(project_path)

                if project_result.success:
                    results[project_name] = project_result.data
                else:
                    self.logger.warning(
                        f"Failed to audit {project_name}: {project_result.error}",
                    )

            # Create ecosystem result
            ecosystem_result = EcosystemAuditResult(
                total_projects_audited=len(results),
                projects_results=results,
            )
            ecosystem_result.calculate_ecosystem_metrics()

            return FlextResult[EcosystemAuditResult].ok(ecosystem_result)

        except Exception as e:
            return FlextResult[EcosystemAuditResult].fail(
                f"Ecosystem audit failed: {e}"
            )

    def generate_compliance_report(
        self,
        ecosystem_result: EcosystemAuditResult,
    ) -> FlextResult[Path]:
        """Generate comprehensive compliance report."""
        try:
            report_data = {
                "audit_metadata": {
                    "timestamp": ecosystem_result.audit_timestamp,
                    "auditor_version": self.metadata.version,
                    "total_projects": ecosystem_result.total_projects_audited,
                    "workspace_path": str(self.workspace_path),
                },
                "ecosystem_summary": {
                    "compliance_score": ecosystem_result.ecosystem_compliance_score,
                    "total_violations": ecosystem_result.total_violations_count,
                    "critical_violations": ecosystem_result.critical_violations_count,
                    "high_violations": ecosystem_result.high_violations_count,
                    "projects_with_critical": len(
                        ecosystem_result.projects_with_critical_issues,
                    ),
                    "fully_compliant": len(ecosystem_result.fully_compliant_projects),
                },
                "project_details": {
                    project_name: {
                        "compliance_score": result.compliance_score,
                        "total_files": result.total_files_analyzed,
                        "violation_counts": {
                            "critical": result.critical_count,
                            "high": result.high_count,
                            "medium": result.medium_count,
                            "low": result.low_count,
                            "total": len(result.violations),
                        },
                        "violations": [
                            {
                                "file_path": v.file_path,
                                "line_number": v.line_number,
                                "violation_type": v.violation_type,
                                "severity": v.severity_level,
                                "current_code": v.current_code_snippet,
                                "pattern_reference": v.pattern_reference,
                                "guidance": v.remediation_guidance,
                                "context": v.architectural_context,
                                "impact": v.business_impact,
                            }
                            for v in result.violations[
                                :50
                            ]  # Limit to first 50 violations per project
                        ],
                    }
                    for project_name, result in ecosystem_result.projects_results.items()
                },
                "recommendations": self._generate_remediation_recommendations(
                    ecosystem_result,
                ),
            }

            # Write report to file
            reports_dir = self.workspace_path / "reports"
            reports_dir.mkdir(exist_ok=True)

            timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            report_path = reports_dir / f"pattern_compliance_audit_{timestamp}.json"

            with Path(report_path).open("w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)

            return FlextResult[Path].ok(report_path)

        except Exception as e:
            return FlextResult[Path].fail(f"Report generation failed: {e}")

    def _generate_remediation_recommendations(
        self,
        ecosystem_result: EcosystemAuditResult,
    ) -> dict[str, str]:
        """Generate prioritized remediation recommendations."""
        recommendations = {}

        if ecosystem_result.critical_violations_count > 0:
            recommendations["immediate_action"] = (
                f"Address {ecosystem_result.critical_violations_count} critical violations "
                "immediately. Focus on foundation pattern compliance and type safety."
            )

        if len(ecosystem_result.projects_with_critical_issues) > 0:
            recommendations["priority_projects"] = (
                f"Prioritize these projects with critical issues: "
                f"{', '.join(ecosystem_result.projects_with_critical_issues[:5])}"
            )

        if ecosystem_result.ecosystem_compliance_score < 80:
            recommendations["compliance_improvement"] = (
                "Ecosystem compliance below 80%. Implement systematic pattern "
                "adoption program with training and automated validation."
            )

        recommendations["next_steps"] = (
            "1. Address critical violations in priority projects\n"
            "2. Implement pattern validation in CI/CD pipeline\n"
            "3. Conduct developer training on FLEXT patterns\n"
            "4. Set up automated compliance monitoring"
        )

        return recommendations


def main() -> None:
    """Main entry point for pattern audit system."""
    parser = argparse.ArgumentParser(description="FLEXT Pattern Audit System")
    parser.add_argument("--project", help="Audit specific project only")
    parser.add_argument(
        "--severity",
        choices=["critical", "high", "medium", "low"],
        help="Filter by severity",
    )
    parser.add_argument("--output", help="Output report file path")

    args = parser.parse_args()

    audit_system = PatternAuditSystem()

    if args.project:
        # Single project audit
        if args.project == "main-workspace":
            project_path = audit_system.workspace_path
        else:
            project_path = audit_system.workspace_path / args.project
        result = audit_system.analyzer.analyze_project_compliance(project_path)
        if result.success:
            pass
    else:
        # Full ecosystem audit
        success = audit_system.run_audit()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
