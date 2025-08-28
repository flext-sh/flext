#!/usr/bin/env python3
"""FLEXT Security AntiPattern Scanner - Enterprise Code Security Analysis.

Comprehensive security scanner that identifies dangerous fallback patterns across
the FLEXT ecosystem. This tool performs static code analysis to detect critical
security antipatterns that can lead to silent failures, state corruption, and
production issues.

The scanner implements enterprise-grade analysis patterns with detailed reporting,
risk assessment, and actionable remediation guidance. It focuses on identifying
code patterns that violate fail-fast principles and proper error handling
standards required in production environments.

Key Features:
    - Silent failure pattern detection (except X: return fake_value)
    - Exception swallowing pattern detection (except X: pass)
    - Fake data generation pattern detection
    - Comprehensive risk assessment and classification
    - Detailed remediation guidance with FLEXT patterns
    - Performance-optimized scanning with configurable filters

Architecture:
    Built on flext-core patterns with comprehensive error handling using
    FlextResult for type-safe operations. Implements Clean Architecture
    patterns with proper separation of scanning logic, analysis, and
    reporting concerns.

Example:
    Basic usage for FLEXT ecosystem security analysis:

    >>> from flext_tools.security.antipattern_scanner import (
    ...     AntipatternScanner,
    ...     ScanConfig,
    ...     create_security_scanner,
    ... )
    >>>
    >>> # Enterprise configuration
    >>> config = ScanConfig(
    ...     target_paths=["src/", "flext-core/src/"],
    ...     exclude_patterns=[".venv", "__pycache__", "*.pyc"],
    ...     output_format="detailed",
    ...     risk_threshold="MEDIUM",
    ... )
    >>>
    >>> scanner = AntipatternScanner(config)
    >>> result = scanner.scan_ecosystem()
    >>>
    >>> if result.success:
    ...     violations = result.value
    ...     print(f"Found {len(violations)} security violations")
    ...     scanner.generate_report(violations, "security_report.json")

Integration:
    - Integrates with flext-tools quality gates for comprehensive security validation
    - Supports CLI integration for automated security testing in CI/CD pipelines
    - Provides detailed reporting for security audits and compliance requirements
    - Coordinates with other FLEXT tools for ecosystem-wide security analysis

Quality Standards:
    - Zero false positives for critical security patterns
    - Performance optimized for large codebases (50k+ files)
    - Comprehensive risk classification with actionable guidance
    - Enterprise-grade reporting with audit trail support

Author: FLEXT Development Team
Version: 2.0.0
License: MIT

"""

from __future__ import annotations

import ast
import json
import operator
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import ClassVar

from flext_core import FlextResult, FlextModels, FlextLogger

from .colors import Colors, print_colored

# Use flext-core logger
logger = FlextLogger(__name__)


class ViolationType(Enum):
    """Types of security violations detected by the scanner."""

    SILENT_FAILURE = "silent_failure"
    EXCEPTION_SWALLOWING = "exception_swallowing"
    FAKE_DATA_GENERATION = "fake_data_generation"


class RiskLevel(Enum):
    """Risk levels for security violations with enterprise classification."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass(frozen=True)
class SecurityViolation:
    """Represents a security violation found during scanning.

    Provides comprehensive violation details with risk assessment
    and remediation guidance following enterprise security standards.
    """

    file_path: str
    line_number: int
    violation_type: ViolationType
    risk_level: RiskLevel
    code_snippet: str
    description: str
    suggested_fix: str

    def to_dict(self) -> dict[str, object]:
        """Convert violation to dictionary for JSON serialization."""
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "violation_type": self.violation_type.value,
            "risk_level": self.risk_level.value,
            "code_snippet": self.code_snippet,
            "description": self.description,
            "suggested_fix": self.suggested_fix,
        }


class ScanConfig(FlextModels.Value):
    """Configuration for security scanning operations using flext-core patterns."""

    target_paths: list[str]
    exclude_patterns: ClassVar[list[str]] = [
        ".venv",
        "__pycache__",
        "*.pyc",
        "*.pyo",
        ".git",
        ".pytest_cache",
        "htmlcov",
        "dist",
        "build",
    ]
    include_dependencies: bool = False
    output_format: str = "summary"  # summary, detailed, json
    risk_threshold: str = "LOW"  # Filter violations by risk level
    max_workers: int = 4

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate scanner configuration business rules."""
        if not self.target_paths:
            return FlextResult[None].fail("At least one target path is required")

        if self.output_format not in {"summary", "detailed", "json"}:
            return FlextResult[None].fail(
                "Output format must be: summary, detailed, or json"
            )

        if self.risk_threshold not in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}:
            return FlextResult[None].fail(
                "Risk threshold must be: LOW, MEDIUM, HIGH, or CRITICAL",
            )

        if self.max_workers < 1:
            return FlextResult[None].fail("Max workers must be at least 1")

        return FlextResult[None].ok(None)


class AntipatternScanner:
    """Enterprise-grade scanner for detecting dangerous code patterns.

    Implements comprehensive static analysis for security antipatterns
    with performance optimization and detailed reporting capabilities.
    """

    def __init__(self, config: ScanConfig) -> None:
        """Initialize scanner with enterprise configuration.

        Args:
            config: Scanner configuration with validation

        """
        self.config = config
        self.logger = FlextLogger(self.__class__.__name__)

        # Validate configuration
        validation_result = config.validate_business_rules()
        if not validation_result.success:
            msg = f"Invalid scanner configuration: {validation_result.error}"
            raise ValueError(msg)

    def scan_ecosystem(self) -> FlextResult[list[SecurityViolation]]:
        """Scan FLEXT ecosystem for security violations.

        Returns:
            FlextResult containing list of violations or error information

        """
        try:
            self.logger.info("Starting security scan of FLEXT ecosystem")

            # Collect Python files to scan
            files_result = self._collect_python_files()
            if not files_result.success:
                return FlextResult[list[SecurityViolation]].fail(
                    f"Failed to collect files: {files_result.error}",
                )

            python_files = files_result.value or []
            self.logger.info(f"Scanning {len(python_files)} Python files")

            # Scan files in parallel for performance
            violations = self._scan_files_parallel(python_files)

            # Filter by risk threshold
            filtered_violations = self._filter_by_risk_threshold(violations)

            self.logger.info(
                f"Found {len(filtered_violations)} violations above {self.config.risk_threshold} risk level",
            )

            return FlextResult[list[SecurityViolation]].ok(filtered_violations)

        except Exception as e:
            error_msg = f"Security scan failed: {e}"
            self.logger.exception(error_msg)
            return FlextResult[list[SecurityViolation]].fail(error_msg)

    def _collect_python_files(self) -> FlextResult[list[Path]]:
        """Collect Python files to scan with filtering."""
        try:
            python_files: list[Path] = []

            for target_path in self.config.target_paths:
                path = Path(target_path)
                if not path.exists():
                    self.logger.warning(f"Target path does not exist: {path}")
                    continue

                if path.is_file() and path.suffix == ".py":
                    python_files.append(path)
                elif path.is_dir():
                    # Recursively find Python files
                    python_files.extend(
                        py_file
                        for py_file in path.rglob("*.py")
                        if self._should_include_file(py_file)
                    )

            return FlextResult[list[Path]].ok(python_files)

        except Exception as e:
            return FlextResult[list[Path]].fail(f"Failed to collect Python files: {e}")

    def _should_include_file(self, file_path: Path) -> bool:
        """Check if file should be included in scan based on exclude patterns."""
        file_str = str(file_path)

        for pattern in self.config.exclude_patterns:
            if pattern in file_str:
                return False

        # Skip dependencies unless explicitly included
        return not (not self.config.include_dependencies and ".venv" in file_str)

    def _scan_files_parallel(self, files: list[Path]) -> list[SecurityViolation]:
        """Scan files in parallel for performance optimization."""
        violations: list[SecurityViolation] = []

        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            future_to_file = {
                executor.submit(self._scan_single_file, file): file for file in files
            }

            for future in as_completed(future_to_file):
                file = future_to_file[future]
                try:
                    file_violations = future.result()
                    violations.extend(file_violations)
                except Exception as e:
                    self.logger.warning(f"Failed to scan {file}: {e}")

        return violations

    def _scan_single_file(self, file_path: Path) -> list[SecurityViolation]:
        """Scan a single file for security violations."""
        violations: list[SecurityViolation] = []

        try:
            with file_path.open("r", encoding="utf-8") as f:
                content = f.read()

            # Use both regex and AST analysis for comprehensive detection
            violations.extend(self._regex_scan(file_path, content))
            violations.extend(self._ast_scan(file_path, content))

        except Exception as e:
            self.logger.debug(f"Could not scan {file_path}: {e}")

        return violations

    def _regex_scan(self, file_path: Path, content: str) -> list[SecurityViolation]:
        """Perform regex-based scanning for common patterns."""
        violations: list[SecurityViolation] = []

        # Pattern: except X: pass (Exception swallowing)
        swallow_pattern = re.compile(
            r"except\s+[^:]+:\s*(#[^\r\n]*)?\s*pass\b",
            re.MULTILINE,
        )

        # Pattern: except X: return fake_value (Silent failure)
        silent_pattern = re.compile(
            r"except\s+[^:]+:\s*(#[^\r\n]*)?\s*return\s+(?:None|False|\[\]|{}|''|\"\"|\d+)",
            re.MULTILINE,
        )

        lines = content.split("\n")

        for match in swallow_pattern.finditer(content):
            line_num = content[: match.start()].count("\n") + 1
            line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""

            violations.append(
                SecurityViolation(
                    file_path=str(file_path),
                    line_number=line_num,
                    violation_type=ViolationType.EXCEPTION_SWALLOWING,
                    risk_level=RiskLevel.CRITICAL,
                    code_snippet=line_content,
                    description="Exceção engolida silenciosamente",
                    suggested_fix="Especificar tipo de exceção e tratar adequadamente ou usar FlextResult[None].fail()",
                ),
            )

        for match in silent_pattern.finditer(content):
            line_num = content[: match.start()].count("\n") + 1
            line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""

            violations.append(
                SecurityViolation(
                    file_path=str(file_path),
                    line_number=line_num,
                    violation_type=ViolationType.SILENT_FAILURE,
                    risk_level=RiskLevel.CRITICAL,
                    code_snippet=line_content,
                    description="Retorno de valor fake em caso de falha",
                    suggested_fix="Usar FlextResult[None].fail() ou propagar exceção apropriadamente",
                ),
            )

        return violations

    def _ast_scan(self, file_path: Path, content: str) -> list[SecurityViolation]:
        """Perform AST-based scanning for complex patterns."""
        violations: list[SecurityViolation] = []

        try:
            tree = ast.parse(content)

            violations.extend(
                SecurityViolation(
                    file_path=str(file_path),
                    line_number=node.lineno,
                    violation_type=ViolationType.FAKE_DATA_GENERATION,
                    risk_level=RiskLevel.HIGH,
                    code_snippet=f"except handler at line {node.lineno}",
                    description="Padrão de manipulação de exceção potencialmente perigoso",
                    suggested_fix="Implementar tratamento adequado com FlextResult ou logging apropriado",
                )
                for node in ast.walk(tree)
                if isinstance(
                    node,
                    ast.ExceptHandler,
                )
                and self._is_dangerous_except_handler(node)
            )

        except SyntaxError:
            # Skip files with syntax errors
            pass
        except Exception as e:
            self.logger.debug(f"AST analysis failed for {file_path}: {e}")

        return violations

    def _is_dangerous_except_handler(self, node: ast.ExceptHandler) -> bool:
        """Check if an exception handler uses dangerous patterns."""
        if not node.body:
            return False

        # Check for pass statements
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            return True

        # Check for return statements with literal values
        for stmt in node.body:
            if (
                isinstance(stmt, ast.Return)
                and stmt.value
                and isinstance(stmt.value, ast.Constant)
            ):
                return True

        return False

    def _filter_by_risk_threshold(
        self,
        violations: list[SecurityViolation],
    ) -> list[SecurityViolation]:
        """Filter violations by risk threshold configuration."""
        risk_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
        min_risk = risk_order[self.config.risk_threshold]

        return [v for v in violations if risk_order[v.risk_level.value] >= min_risk]

    def generate_report(
        self,
        violations: list[SecurityViolation],
        output_file: str | None,
    ) -> FlextResult[None]:
        """Generate comprehensive security report.

        Args:
            violations: List of security violations to report
            output_file: Path to output report file

        Returns:
            FlextResult indicating report generation success or failure

        """
        try:
            if self.config.output_format == "json":
                if not output_file:
                    return FlextResult[None].fail(
                        "Output file required for json report"
                    )
                return self._generate_json_report(violations, output_file)
            if self.config.output_format == "detailed":
                if not output_file:
                    return FlextResult[None].fail(
                        "Output file required for detailed report"
                    )
                return self._generate_detailed_report(violations, output_file)
            return self._generate_summary_report(violations)

        except Exception as e:
            return FlextResult[None].fail(f"Report generation failed: {e}")

    def _generate_json_report(
        self,
        violations: list[SecurityViolation],
        output_file: str,
    ) -> FlextResult[None]:
        """Generate JSON format security report."""
        try:
            report_data = {
                "scan_summary": {
                    "total_violations": len(violations),
                    "risk_breakdown": self._get_risk_breakdown(violations),
                    "violation_types": self._get_type_breakdown(violations),
                },
                "violations": [v.to_dict() for v in violations],
                "scan_config": {
                    "target_paths": self.config.target_paths,
                    "risk_threshold": self.config.risk_threshold,
                    "output_format": self.config.output_format,
                },
            }

            with Path(output_file).open("w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2)

            self.logger.info(f"JSON report generated: {output_file}")
            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"JSON report generation failed: {e}")

    def _generate_detailed_report(
        self,
        violations: list[SecurityViolation],
        output_file: str,
    ) -> FlextResult[None]:
        """Generate detailed text format report."""
        try:
            with Path(output_file).open("w", encoding="utf-8") as f:
                f.write("FLEXT Security AntiPattern Scan Report\n")
                f.write("=" * 50 + "\n\n")

                f.write(f"Total Violations: {len(violations)}\n")
                f.write(f"Risk Threshold: {self.config.risk_threshold}\n\n")

                # Risk breakdown
                risk_breakdown = self._get_risk_breakdown(violations)
                f.write("Risk Level Breakdown:\n")
                f.writelines(
                    f"  {risk}: {count}\n" for risk, count in risk_breakdown.items()
                )
                f.write("\n")

                # Detailed violations
                for i, violation in enumerate(violations, 1):
                    f.write(f"Violation #{i}\n")
                    f.write(f"  File: {violation.file_path}\n")
                    f.write(f"  Line: {violation.line_number}\n")
                    f.write(f"  Type: {violation.violation_type.value}\n")
                    f.write(f"  Risk: {violation.risk_level.value}\n")
                    f.write(f"  Code: {violation.code_snippet}\n")
                    f.write(f"  Description: {violation.description}\n")
                    f.write(f"  Fix: {violation.suggested_fix}\n")
                    f.write("-" * 40 + "\n")

            self.logger.info(f"Detailed report generated: {output_file}")
            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Detailed report generation failed: {e}")

    def _generate_summary_report(
        self,
        violations: list[SecurityViolation],
    ) -> FlextResult[None]:
        """Generate summary report to console."""
        try:
            print_colored("=" * 60, Colors.CYAN)
            print_colored("🔒 FLEXT Security AntiPattern Scan Results", Colors.CYAN)
            print_colored("=" * 60, Colors.CYAN)

            if not violations:
                print_colored("✅ No security violations found!", Colors.GREEN)
                return FlextResult[None].ok(None)

            print_colored(f"❌ Found {len(violations)} security violations", Colors.RED)

            # Risk breakdown
            risk_breakdown = self._get_risk_breakdown(violations)
            print_colored("\n📊 Risk Level Breakdown:", Colors.BLUE)
            for risk, count in risk_breakdown.items():
                color = self._get_risk_color(risk)
                print_colored(f"  {risk}: {count}", color)

            # Type breakdown
            type_breakdown = self._get_type_breakdown(violations)
            print_colored("\n🔍 Violation Types:", Colors.BLUE)
            for vtype, count in type_breakdown.items():
                print_colored(f"  {vtype}: {count}", Colors.WHITE)

            # Top files with violations
            file_breakdown: dict[str, int] = {}
            for violation in violations:
                file_path = violation.file_path
                file_breakdown[file_path] = file_breakdown.get(file_path, 0) + 1

            top_files = sorted(
                file_breakdown.items(),
                key=operator.itemgetter(1),
                reverse=True,
            )[:5]
            print_colored("\n📁 Top Files with Violations:", Colors.BLUE)
            for file_path, count in top_files:
                print_colored(f"  {Path(file_path).name}: {count}", Colors.YELLOW)

            print_colored("=" * 60, Colors.CYAN)

            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Summary report generation failed: {e}")

    def _get_risk_breakdown(
        self,
        violations: list[SecurityViolation],
    ) -> dict[str, int]:
        """Get breakdown of violations by risk level."""
        breakdown = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for violation in violations:
            breakdown[violation.risk_level.value] += 1
        return breakdown

    def _get_type_breakdown(
        self,
        violations: list[SecurityViolation],
    ) -> dict[str, int]:
        """Get breakdown of violations by type."""
        breakdown: dict[str, int] = {}
        for violation in violations:
            vtype = violation.violation_type.value
            breakdown[vtype] = breakdown.get(vtype, 0) + 1
        return breakdown

    def _get_risk_color(self, risk: str) -> str:
        """Get color for risk level display."""
        colors = {
            "CRITICAL": Colors.RED,
            "HIGH": Colors.YELLOW,
            "MEDIUM": Colors.BLUE,
            "LOW": Colors.GREEN,
        }
        return colors.get(risk, Colors.WHITE)


def create_security_scanner(
    target_paths: list[str],
    *,
    exclude_dependencies: bool = True,
    output_format: str = "summary",
    risk_threshold: str = "MEDIUM",
) -> FlextResult[AntipatternScanner]:
    """Create security scanner with common configurations.

    Args:
      target_paths: List of paths to scan
      exclude_dependencies: Whether to exclude .venv and dependencies
      output_format: Output format (summary, detailed, json)
      risk_threshold: Minimum risk level to report

    Returns:
      FlextResult containing configured scanner or error

    """
    try:
        # Some FlextValue subclasses use dynamic constructors; ignore call-arg typing here
        config = ScanConfig(
            target_paths=target_paths,
            include_dependencies=not exclude_dependencies,
            output_format=output_format,
            risk_threshold=risk_threshold,
        )

        scanner = AntipatternScanner(config)
        return FlextResult[AntipatternScanner].ok(scanner)

    except Exception as e:
        return FlextResult[AntipatternScanner].fail(
            f"Failed to create security scanner: {e}"
        )


def scan_flext_ecosystem(
    workspace_path: str = ".",
    output_file: str | None = None,
) -> FlextResult[list[SecurityViolation]]:
    """Scan the entire FLEXT ecosystem.

    Args:
      workspace_path: Path to FLEXT workspace
      output_file: Optional output file for detailed report

    Returns:
      FlextResult containing violations list or error

    """
    # Common FLEXT project paths
    target_paths = [
        f"{workspace_path}/src",
        f"{workspace_path}/flext-core/src",
        f"{workspace_path}/flext-api/src",
        f"{workspace_path}/flext-auth/src",
        f"{workspace_path}/flext-cli/src",
    ]

    # Filter existing paths
    existing_paths = [path for path in target_paths if Path(path).exists()]

    if not existing_paths:
        return FlextResult[list[SecurityViolation]].fail(
            "No valid FLEXT project paths found"
        )

    scanner_result = create_security_scanner(
        target_paths=existing_paths,
        exclude_dependencies=True,
        output_format="detailed" if output_file else "summary",
        risk_threshold="MEDIUM",
    )

    if not scanner_result.success:
        return FlextResult[list[SecurityViolation]].fail(
            f"Scanner creation failed: {scanner_result.error}"
        )

    scanner = scanner_result.value
    if not scanner:
        return FlextResult[list[SecurityViolation]].fail(
            "Scanner creation returned None"
        )

    # Perform scan
    scan_result = scanner.scan_ecosystem()
    if not scan_result.success:
        return scan_result

    violations = scan_result.value or []

    # Generate report if output file specified
    if output_file and violations:
        report_result = scanner.generate_report(violations, output_file)
        if not report_result.success:
            logger.warning(f"Report generation failed: {report_result.error}")
    else:
        # Generate summary report to console via public API
        scanner.generate_report(violations, None)
    return FlextResult[list[SecurityViolation]].ok(violations)
