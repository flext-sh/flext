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
from pathlib import Path

from flext_tools.security import (
    AntipatternScanner,
    RiskLevel,
    ScanConfig,
    SecurityViolation,
    create_security_scanner,
    scan_flext_ecosystem,
)
from flext_tools.utils.colors import Colors, print_colored


def example_basic_scan() -> None:
    """Example 1: Basic security scan with factory function."""
    print_colored("🔍 Example 1: Basic Security Scan", Colors.CYAN)

    # Create scanner with factory function
    scanner_result = create_security_scanner(
        target_paths=["src/flext_tools/security/"],
        exclude_dependencies=True,
        output_format="summary",
        risk_threshold="MEDIUM",
    )

    if not scanner_result.success:
        print_colored(f"❌ Scanner creation failed: {scanner_result.error}", Colors.RED)
        return

    scanner = scanner_result.data
    if not scanner:
        print_colored("❌ Scanner is None", Colors.RED)
        return

    # Perform scan
    result = scanner.scan_ecosystem()

    if result.success:
        violations = result.data or []
        print_colored(
            f"✅ Scan completed: {len(violations)} violations found",
            Colors.GREEN,
        )

        # Generate summary report
        scanner._generate_summary_report(violations)
    else:
        print_colored(f"❌ Scan failed: {result.error}", Colors.RED)

    print_colored("-" * 60, Colors.WHITE)


def example_advanced_configuration() -> None:
    """Example 2: Advanced scanner configuration."""
    print_colored("🔧 Example 2: Advanced Configuration", Colors.CYAN)

    # Create custom configuration
    config = ScanConfig(
        target_paths=["src/", "scripts/"],
        exclude_patterns=[".venv", "__pycache__", "*.pyc", "test_*"],
        include_dependencies=False,
        output_format="detailed",
        risk_threshold="HIGH",
        max_workers=8,
    )

    # Validate configuration
    validation_result = config.validate_business_rules()
    if not validation_result.success:
        print_colored(
            f"❌ Invalid configuration: {validation_result.error}",
            Colors.RED,
        )
        return

    # Create scanner
    scanner = AntipatternScanner(config)

    # Perform scan
    result = scanner.scan_ecosystem()

    if result.success:
        violations = result.data or []
        print_colored(
            f"✅ Advanced scan completed: {len(violations)} violations found",
            Colors.GREEN,
        )

        # Custom analysis
        critical_violations = [
            v for v in violations if v.risk_level == RiskLevel.CRITICAL
        ]
        high_violations = [v for v in violations if v.risk_level == RiskLevel.HIGH]

        print_colored(f"🚨 Critical violations: {len(critical_violations)}", Colors.RED)
        print_colored(f"⚠️  High-risk violations: {len(high_violations)}", Colors.YELLOW)

    else:
        print_colored(f"❌ Advanced scan failed: {result.error}", Colors.RED)

    print_colored("-" * 60, Colors.WHITE)


def example_ecosystem_scan() -> None:
    """Example 3: Ecosystem-wide scan with convenience function."""
    print_colored("🌐 Example 3: Ecosystem Scan", Colors.CYAN)

    # Use convenience function for full ecosystem scan
    result = scan_flext_ecosystem(
        workspace_path=".",
        output_file=None,  # Console output only
    )

    if result.success:
        violations = result.data or []
        print_colored(
            f"✅ Ecosystem scan completed: {len(violations)} violations found",
            Colors.GREEN,
        )

        # Analyze by violation type
        type_counts: dict[str, int] = {}
        for violation in violations:
            vtype = violation.violation_type.value
            type_counts[vtype] = type_counts.get(vtype, 0) + 1

        print_colored("📊 Violation types breakdown:", Colors.BLUE)
        for vtype, count in type_counts.items():
            print_colored(f"  {vtype}: {count}", Colors.WHITE)

    else:
        print_colored(f"❌ Ecosystem scan failed: {result.error}", Colors.RED)

    print_colored("-" * 60, Colors.WHITE)


def example_custom_reporting() -> None:
    """Example 4: Custom reporting and analysis."""
    print_colored("📊 Example 4: Custom Reporting", Colors.CYAN)

    # Simple scan for demonstration
    scanner_result = create_security_scanner(
        target_paths=["src/flext_tools/"],
        risk_threshold="LOW",
    )

    if not scanner_result.success:
        print_colored(f"❌ Scanner creation failed: {scanner_result.error}", Colors.RED)
        return

    scanner = scanner_result.data
    if not scanner:
        return

    result = scanner.scan_ecosystem()

    if not result.success:
        print_colored(f"❌ Scan failed: {result.error}", Colors.RED)
        return

    violations = result.data or []

    # Custom analysis and reporting
    print_colored("📈 Custom Analysis Results:", Colors.GREEN)

    # Group by file
    file_violations: dict[str, list[SecurityViolation]] = {}
    for violation in violations:
        file_path = Path(violation.file_path).name
        if file_path not in file_violations:
            file_violations[file_path] = []
        file_violations[file_path].append(violation)

    # Top problematic files
    top_files = sorted(file_violations.items(), key=lambda x: len(x[1]), reverse=True)[
        :3
    ]

    print_colored("🎯 Top 3 files with most violations:", Colors.YELLOW)
    for file_name, file_viols in top_files:
        print_colored(f"  {file_name}: {len(file_viols)} violations", Colors.WHITE)

        # Show violation types for this file
        types_in_file = {v.violation_type.value for v in file_viols}
        print_colored(f"    Types: {', '.join(types_in_file)}", Colors.BLUE)

    # Risk distribution
    risk_counts = {}
    for violation in violations:
        risk = violation.risk_level.value
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
    scanner_result = create_security_scanner(
        target_paths=["src/"],
        risk_threshold="CRITICAL",
        output_format="json",
    )

    if not scanner_result.success:
        print_colored(
            f"❌ CI/CD scanner creation failed: {scanner_result.error}",
            Colors.RED,
        )
        return

    scanner = scanner_result.data
    if not scanner:
        return

    result = scanner.scan_ecosystem()

    if not result.success:
        print_colored(f"❌ CI/CD scan failed: {result.error}", Colors.RED)
        return

    violations = result.data or []
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
                f"  {Path(violation.file_path).name}:{violation.line_number}",
                Colors.WHITE,
            )
            print_colored(f"    {violation.description}", Colors.YELLOW)
            print_colored(f"    Fix: {violation.suggested_fix}", Colors.GREEN)

        # In real CI/CD, you would exit with non-zero code
        # sys.exit(1)

    else:
        print_colored(
            "✅ BUILD CAN PROCEED: No critical security violations",
            Colors.GREEN,
        )

    # Generate JSON report for CI/CD artifacts
    report_result = scanner.generate_report(violations, "ci_security_report.json")
    if report_result.success:
        print_colored("📄 JSON report generated for CI/CD artifacts", Colors.BLUE)

    print_colored("-" * 60, Colors.WHITE)


def main() -> None:
    """Run all security scanner examples."""
    print_colored("=" * 60, Colors.CYAN)
    print_colored("🔒 FLEXT Security Tools - API Examples", Colors.CYAN)
    print_colored("=" * 60, Colors.CYAN)
    print()

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
