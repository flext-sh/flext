#!/usr/bin/env python3
"""Example usage of FLEXT Security Tools - Programmatic API Examples.

This script demonstrates how to use the FLEXT security scanner programmatically
for integration with custom workflows, automated security testing, and
enterprise security monitoring systems.

The examples show both simple and advanced usage patterns for different
security analysis scenarios including CI/CD integration, custom reporting,
and workflow automation.

"""

from __future__ import annotations

import sys

from flext_core import FlextTypes

from .security_audit import (
    AntipatternScanner,
    ScanConfig,
    SecurityViolation,
    scan_flext_ecosystem,
)


# Simple color implementation to avoid dependency issues
class Colors:
    """Simple color constants."""

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    RESET = "\033[0m"


def print_colored(message: str, color: str = "") -> None:
    """Print colored message."""
    print(f"{color}{message}{Colors.RESET}" if color else message)


# Define RiskLevel as a simple class with constants
class RiskLevel:
    """Risk level constants."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


# Define create_security_scanner function
def create_security_scanner(
    target_paths: FlextTypes.Core.StringList,
    *,  # Force keyword-only arguments
    exclude_dependencies: bool = False,
    output_format: str = "summary",
    risk_threshold: str = "MEDIUM",
) -> AntipatternScanner:
    """Create a security scanner with the given configuration.

    Args:
        target_paths: List of paths to scan
        exclude_dependencies: Whether to exclude dependency scanning
        output_format: Format for output (summary, detailed, json)
        risk_threshold: Minimum risk level to report (LOW, MEDIUM, HIGH)

    """
    config = ScanConfig(target_paths, include_dependencies=not exclude_dependencies)
    scanner = AntipatternScanner(config)

    # Configure scanner based on parameters
    if output_format == "json":
        scanner.set_output_format("json")
    elif output_format == "detailed":
        scanner.set_output_format("detailed")
    else:
        scanner.set_output_format("summary")

    # Set risk threshold
    scanner.set_risk_threshold(risk_threshold)

    return scanner


def example_basic_scan() -> None:
    """Example 1: Basic security scan with factory function."""
    print_colored("🔍 Example 1: Basic Security Scan", Colors.CYAN)

    # Create scanner with factory function
    scanner = create_security_scanner(
        target_paths=["src/flext_tools/security/"],
        exclude_dependencies=True,
        output_format="summary",
        risk_threshold="MEDIUM",
    )

    # Perform scan
    violations = scanner.scan_ecosystem()
    print_colored(
        f"✅ Scan completed: {len(violations)} violations found",
        Colors.GREEN,
    )

    # Generate summary report
    # scanner._generate_summary_report(violations)  # Method doesn't exist

    print_colored("-" * 60, Colors.WHITE)


def example_advanced_configuration() -> None:
    """Example 2: Advanced scanner configuration."""
    print_colored("🔧 Example 2: Advanced Configuration", Colors.CYAN)

    # Create custom configuration
    config = ScanConfig(
        target_paths=["src/", "scripts/"],
        include_dependencies=False,
    )

    # Create scanner
    scanner = AntipatternScanner(config)

    # Perform scan
    violations = scanner.scan_ecosystem()
    print_colored(
        f"✅ Advanced scan completed: {len(violations)} violations found",
        Colors.GREEN,
    )

    # Custom analysis
    critical_violations = [v for v in violations if v.risk_level == RiskLevel.CRITICAL]
    high_violations = [v for v in violations if v.risk_level == RiskLevel.HIGH]

    print_colored(f"🚨 Critical violations: {len(critical_violations)}", Colors.RED)
    print_colored(f"⚠️  High-risk violations: {len(high_violations)}", Colors.YELLOW)

    print_colored("-" * 60, Colors.WHITE)


def example_ecosystem_scan() -> None:
    """Example 3: Ecosystem-wide scan with convenience function."""
    print_colored("🌐 Example 3: Ecosystem Scan", Colors.CYAN)

    # Use convenience function for full ecosystem scan
    violations = scan_flext_ecosystem(
        workspace_path=".",
        _output_file=None,  # Console output only
    )
    print_colored(
        f"✅ Ecosystem scan completed: {len(violations)} violations found",
        Colors.GREEN,
    )

    # Analyze by risk level
    type_counts: dict[str, int] = {}
    for violation in violations:
        vtype = violation.risk_level
        type_counts[vtype] = type_counts.get(vtype, 0) + 1

    print_colored("📊 Violation types breakdown:", Colors.BLUE)
    for vtype, count in type_counts.items():
        print_colored(f"  {vtype}: {count}", Colors.WHITE)

    print_colored("-" * 60, Colors.WHITE)


def example_custom_reporting() -> None:
    """Example 4: Custom reporting and analysis."""
    print_colored("📊 Example 4: Custom Reporting", Colors.CYAN)

    scanner = create_security_scanner(
        target_paths=["src/flext_tools/"],
        risk_threshold="LOW",
    )

    violations = scanner.scan_ecosystem()

    # Custom analysis and reporting
    print_colored("📈 Custom Analysis Results:", Colors.GREEN)

    # Group by risk level
    risk_violations: dict[str, list[SecurityViolation]] = {}
    for violation in violations:
        risk_level = violation.risk_level
        if risk_level not in risk_violations:
            risk_violations[risk_level] = []
        risk_violations[risk_level].append(violation)

    # Top risk levels
    top_risks = sorted(risk_violations.items(), key=lambda x: len(x[1]), reverse=True)

    print_colored("🎯 Risk level distribution:", Colors.YELLOW)
    for risk_level, risk_viols in top_risks:
        print_colored(f"  {risk_level}: {len(risk_viols)} violations", Colors.WHITE)

    # Risk distribution
    risk_counts: dict[str, int] = {}
    for violation in violations:
        risk = violation.risk_level
        risk_counts[risk] = risk_counts.get(risk, 0) + 1

    print_colored("⚖️  Risk distribution:", Colors.BLUE)
    for risk, count in sorted(risk_counts.items()):
        color = (
            Colors.RED
            if risk == "CRITICAL"
            else Colors.YELLOW
            if risk == "HIGH"
            else Colors.GREEN
        )
        print_colored(f"  {risk}: {count}", color)

    print_colored("-" * 60, Colors.WHITE)


def example_ci_cd_integration() -> None:
    """Example 5: CI/CD integration patterns."""
    print_colored("🚀 Example 5: CI/CD Integration", Colors.CYAN)

    # Scan with focus on critical violations for CI/CD
    scanner = create_security_scanner(
        target_paths=["src/"],
        risk_threshold="CRITICAL",
        output_format="json",
    )

    violations = scanner.scan_ecosystem()
    critical_violations = [v for v in violations if v.risk_level == RiskLevel.CRITICAL]

    # CI/CD decision logic
    if critical_violations:
        print_colored(
            f"🚨 BUILD SHOULD FAIL: {len(critical_violations)} critical violations",
            Colors.RED,
        )

        print_colored("Critical violations that must be fixed:", Colors.RED)
        for violation in critical_violations[:3]:  # Show first 3
            print_colored(
                f"  {violation.risk_level}: {violation.message}",
                Colors.WHITE,
            )

        # In real CI/CD, you would exit with non-zero code
        # sys.exit(1)

    else:
        print_colored(
            "✅ BUILD CAN PROCEED: No critical security violations",
            Colors.GREEN,
        )

    # Generate simple report for CI/CD artifacts
    print_colored("📄 Security scan completed for CI/CD", Colors.BLUE)

    print_colored("-" * 60, Colors.WHITE)


def main() -> None:
    """Run all security scanner examples."""
    print_colored("=" * 60, Colors.CYAN)
    print_colored("🔒 FLEXT Security Tools - API Examples", Colors.CYAN)
    print_colored("=" * 60, Colors.CYAN)

    try:
        # Run all examples
        example_basic_scan()
        example_advanced_configuration()
        example_ecosystem_scan()
        example_custom_reporting()
        example_ci_cd_integration()

        print_colored(
            "✅ All security scanner examples completed successfully!",
            Colors.GREEN,
        )

    except KeyboardInterrupt:
        print_colored("\n❌ Examples interrupted by user", Colors.YELLOW)
    except Exception as e:
        print_colored(f"❌ Example execution failed: {e}", Colors.RED)
        sys.exit(1)


if __name__ == "__main__":
    main()
