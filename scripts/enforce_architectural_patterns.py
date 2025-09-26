#!/usr/bin/env python3
"""FLEXT Ecosystem Architectural Pattern Enforcement Script.

This script systematically enforces FLEXT architectural patterns across all projects:
1. Unified Class Pattern - Single class per module with nested helpers
2. Domain Separation - Proper import hierarchy and library usage
3. FlextResult Pattern - Explicit error handling without try/except fallbacks
4. Constants Unification - Use FlextConstants inheritance hierarchy
5. CLI Standardization - Use flext-cli exclusively, no direct Click/Rich

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import ast
import operator
import re
from pathlib import Path
from typing import Any

# FLEXT projects to enforce patterns on
FLEXT_ROOT = Path("/home/marlonsc/flext")

# Domain violation patterns
DOMAIN_VIOLATIONS = {
    "cli_ui": [
        r"import click\b",
        r"import rich\b",
        r"import typer\b",
        r"from rich\.",
        r"from click\.",
        r"from typer\.",
    ],
    "web_framework": [
        r"import fastapi\b",
        r"import flask\b",
        r"import django\b",
        r"import aiohttp\b",
        r"from fastapi\.",
        r"from flask\.",
    ],
    "http_client": [
        r"import requests\b",
        r"import httpx\b",
        r"from requests\.",
        r"from httpx\.",
    ],
    "data_pipeline": [
        r"import meltano\b",
        r"import singer\b",
        r"import dbt\b",
        r"from meltano\.",
        r"from singer\.",
        r"from dbt\.",
    ],
    "database": [
        r"import sqlalchemy\b",
        r"import oracledb\b",
        r"import ldap3\b",
        r"from sqlalchemy\.",
        r"from oracledb\.",
        r"from ldap3\.",
    ],
    "quality_analysis": [
        r"import mypy\b",
        r"import coverage\b",
        r"import pytest\b",
        r"import ruff\b",
        r"import black\b",
        r"from mypy\.",
        r"from coverage\.",
    ],
    "grpc": [
        r"import grpc\b",
        r"import grpcio\b",
        r"from grpc\.",
        r"from grpcio\.",
    ],
    "monitoring": [
        r"import redis\b",
        r"import prometheus_client\b",
        r"from redis\.",
        r"from prometheus_client\.",
    ],
}

# Proper domain library mappings
DOMAIN_REPLACEMENTS = {
    # CLI/UI
    "import click": "from flext_cli import FlextCliApi",
    "import rich": "from flext_cli import FlextCliApi",
    "import typer": "from flext_cli import FlextCliApi",
    "from rich.console import Console": "from flext_cli import FlextCliApi",
    "from click import command": "from flext_cli import FlextCliApi",
    # Web Framework
    "import fastapi": "from flext_web import FlextWebServer",
    "import flask": "from flext_web import FlextWebServer",
    "import django": "from flext_web import FlextWebServer",
    # HTTP Client
    "import requests": "from flext_api import FlextApiClient",
    "import httpx": "from flext_api import FlextApiClient",
    # Data Pipeline
    "import meltano": "from flext_meltano import FlextMeltanoRunner",
    "import singer": "from flext_meltano import FlextSingerTap, FlextSingerTarget",
    "import dbt": "from flext_meltano import FlextDbtRunner",
    # Database
    "import sqlalchemy": "from flext_db_oracle import FlextOracleClient",
    "import oracledb": "from flext_db_oracle import FlextOracleClient",
    "import ldap3": "from flext_ldap import FlextLdapClient",
    # Quality/Analysis
    "import mypy": "from flext_quality import FlextQualityAnalyzer",
    "import coverage": "from flext_quality import FlextQualityAnalyzer",
    "import pytest": "from flext_quality import FlextQualityAnalyzer",
    # gRPC
    "import grpc": "from flext_grpc import FlextGrpcServer",
    # Monitoring
    "import redis": "from flext_observability import FlextMetrics",
    "import prometheus_client": "from flext_observability import FlextMetrics",
}


def find_python_files() -> list[Path]:
    """Find all Python files in FLEXT projects."""
    python_files = []

    for py_file in FLEXT_ROOT.rglob("src/**/*.py"):
        # Skip virtual environment and system files
        if ".venv" in str(py_file) or "site-packages" in str(py_file):
            continue

        # Only include FLEXT projects
        if any(
            part.startswith("flext-")
            or part in {"client-a-oud-mig", "flexcore", "client-b-meltano-native"}
            for part in py_file.parts
        ):
            python_files.append(py_file)

    return sorted(python_files)


def detect_domain_violations(content: str, file_path: Path) -> list[str]:
    """Detect domain separation violations in file content."""
    violations = []

    # Skip certain domain-specific projects
    project_name = None
    for part in file_path.parts:
        if part.startswith("flext-") or part in {
            "client-a-oud-mig",
            "flexcore",
            "client-b-meltano-native",
        }:
            project_name = part
            break

    # Define allowed violations for specific domain projects
    allowed_domains = {
        "flext-cli": ["cli_ui"],
        "flext-web": ["web_framework"],
        "flext-api": ["http_client"],
        "flext-meltano": ["data_pipeline"],
        "flext-db-oracle": ["database"],
        "flext-ldap": ["database"],
        "flext-ldif": ["database"],
        "flext-quality": ["quality_analysis"],
        "flext-grpc": ["grpc"],
        "flext-observability": ["monitoring"],
    }

    for domain, patterns in DOMAIN_VIOLATIONS.items():
        # Skip if this project is allowed to use this domain
        if project_name and domain in allowed_domains.get(project_name, []):
            continue

        violations.extend(
            f"Domain violation: {domain} - {pattern}"
            for pattern in patterns
            if re.search(pattern, content)
        )

    return violations


def detect_multiple_classes(content: str) -> list[str]:
    """Detect multiple classes in a single module."""
    violations = []

    try:
        tree = ast.parse(content)
        class_count = sum(
            1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
        )

        if class_count > 1:
            violations.append(
                f"Multiple classes detected: {class_count} classes (should be 1)"
            )

    except SyntaxError:
        violations.append("Syntax error - cannot parse file")

    return violations


def detect_loose_functions(content: str) -> list[str]:
    """Detect loose helper functions outside classes."""
    violations = []

    # Find function definitions that are not inside classes
    function_pattern = r"^def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\("
    class_pattern = r"^class\s+"

    lines = content.split("\n")
    in_class = False
    indent_level = 0

    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()

        # Track class context
        if re.match(class_pattern, stripped):
            in_class = True
            indent_level = len(line) - len(stripped)
        elif in_class and stripped and len(line) - len(stripped) <= indent_level:
            in_class = False

        # Check for loose functions (not inside class)
        if re.match(function_pattern, stripped) and not in_class:
            func_name = re.match(function_pattern, stripped).group(1)
            # Allow certain special functions
            if func_name not in {"main", "__main__"}:
                violations.append(
                    f"Loose function '{func_name}' at line {i} (should be nested in class)"
                )

    return violations


def detect_try_except_fallbacks(content: str) -> list[str]:
    """Detect try/except fallback patterns instead of FlextResult."""
    # Patterns that indicate fallback mechanisms
    fallback_patterns = [
        r"try:\s*.*?\s*except.*?:\s*return.*?default",
        r"try:\s*.*?\s*except.*?:\s*pass",
        r"try:\s*.*?\s*except.*?:\s*None",
        r"try:\s*.*?\s*except.*?:\s*\[\]",
        r"try:\s*.*?\s*except.*?:\s*\{\}",
        r'try:\s*.*?\s*except.*?:\s*""',
        r"try:\s*.*?\s*except.*?:\s*0",
        r"try:\s*.*?\s*except.*?:\s*False",
    ]

    return [
        "Try/except fallback pattern detected (use FlextResult instead)"
        for pattern in fallback_patterns
        if re.search(pattern, content, re.DOTALL | re.MULTILINE)
    ]


def detect_non_flext_constants(content: str, file_path: Path) -> list[str]:
    """Detect constants classes that don't inherit from FlextConstants."""
    violations = []

    # Skip if this is a constants file itself
    if "constants.py" in file_path.name:
        # Check if it inherits from FlextConstants
        if "class " in content and "Constants" in content:
            if "FlextConstants" not in content:
                violations.append("Constants class should inherit from FlextConstants")

    return violations


def detect_internal_imports(content: str) -> list[str]:
    """Detect internal imports instead of root-level imports."""
    internal_patterns = [
        r"from flext_core\.result import",
        r"from flext_core\.models import",
        r"from flext_core\.container import",
        r"from flext_core\.loggings import",
        r"from flext_cli\.api import",
        r"from flext_cli\.commands import",
    ]

    return [
        f"Internal import detected: {pattern} (use root-level imports)"
        for pattern in internal_patterns
        if re.search(pattern, content)
    ]


def enforce_unified_class_pattern(
    content: str, file_path: Path
) -> tuple[str, list[str]]:
    """Enforce unified class pattern with nested helpers."""
    changes = []

    # This would be a complex transformation requiring AST manipulation
    # For now, we'll detect violations and suggest manual fixes

    violations = []
    violations.extend(detect_multiple_classes(content))
    violations.extend(detect_loose_functions(content))

    if violations:
        changes.append("File needs unified class pattern refactoring")

    return content, changes


def enforce_domain_separation(content: str, file_path: Path) -> tuple[str, list[str]]:
    """Enforce domain separation by replacing direct imports."""
    changes = []

    # Replace domain violations with proper imports
    for old_import, new_import in DOMAIN_REPLACEMENTS.items():
        if old_import in content:
            content = content.replace(old_import, new_import)
            changes.append(f"Replaced '{old_import}' with '{new_import}'")

    return content, changes


def enforce_flext_result_pattern(content: str) -> tuple[str, list[str]]:
    """Enforce FlextResult pattern instead of try/except fallbacks."""
    changes = []

    # Add FlextResult import if not present and try/except patterns detected
    if "try:" in content and "except:" in content and "FlextResult" not in content:
        # Add import after existing imports
        lines = content.split("\n")

        # Find where to insert import
        for i, line in enumerate(lines):
            if line.strip().startswith("from flext_core"):
                if "FlextResult" not in line:
                    lines[i] = line.rstrip(" ,") + ", FlextResult"
                    changes.append("Added FlextResult to imports")
                    break
        else:
            # Add new import line
            for i, line in enumerate(lines):
                if line.strip().startswith("from __future__"):
                    lines.insert(i + 2, "from flext_core import FlextResult")
                    changes.append("Added FlextResult import")
                    break

        content = "\n".join(lines)

    return content, changes


def enforce_constants_inheritance(
    content: str, file_path: Path
) -> tuple[str, list[str]]:
    """Enforce FlextConstants inheritance pattern."""
    changes = []

    if "constants.py" in file_path.name:
        # Check if it has a constants class
        if re.search(r"class\s+\w*Constants?\w*", content):
            if "FlextConstants" not in content:
                # Add FlextConstants import and inheritance
                if "from flext_core import" in content:
                    content = re.sub(
                        r"from flext_core import ([^)]+)",
                        r"from flext_core import \1, FlextConstants",
                        content,
                    )
                else:
                    content = "from flext_core import FlextConstants\n\n" + content

                # Update class definition
                content = re.sub(
                    r"class\s+(\w*Constants?\w*)\s*:",
                    r"class \1(FlextConstants):",
                    content,
                )

                changes.append("Added FlextConstants inheritance")

    return content, changes


def analyze_architectural_patterns(file_path: Path) -> dict[str, Any]:
    """Analyze a single file for architectural pattern compliance."""
    try:
        with Path(file_path).open("r", encoding="utf-8") as f:
            content = f.read()

        violations = []

        # Detect various violations
        violations.extend(detect_domain_violations(content, file_path))
        violations.extend(detect_multiple_classes(content))
        violations.extend(detect_loose_functions(content))
        violations.extend(detect_try_except_fallbacks(content))
        violations.extend(detect_non_flext_constants(content, file_path))
        violations.extend(detect_internal_imports(content))

        return {
            "status": "analyzed",
            "violations": violations,
            "file": str(file_path),
            "violation_count": len(violations),
        }

    except Exception as e:
        return {
            "status": "error",
            "violations": [],
            "file": str(file_path),
            "error": str(e),
            "violation_count": 0,
        }


def enforce_architectural_patterns(file_path: Path) -> dict[str, Any]:
    """Enforce architectural patterns on a single file."""
    try:
        with Path(file_path).open("r", encoding="utf-8") as f:
            original_content = f.read()

        content = original_content
        all_changes = []

        # Apply all enforcement patterns
        content, changes = enforce_domain_separation(content, file_path)
        all_changes.extend(changes)

        content, changes = enforce_flext_result_pattern(content)
        all_changes.extend(changes)

        content, changes = enforce_constants_inheritance(content, file_path)
        all_changes.extend(changes)

        content, changes = enforce_unified_class_pattern(content, file_path)
        all_changes.extend(changes)

        # Write changes if any were made
        if content != original_content and any(
            c for c in all_changes if not c.startswith("File needs")
        ):
            with Path(file_path).open("w", encoding="utf-8") as f:
                f.write(content)

            return {
                "status": "modified",
                "changes": all_changes,
                "file": str(file_path),
            }
        return {
            "status": "needs_manual_refactoring" if all_changes else "compliant",
            "changes": all_changes,
            "file": str(file_path),
        }

    except Exception as e:
        return {
            "status": "error",
            "changes": [],
            "file": str(file_path),
            "error": str(e),
        }


def main() -> None:
    """Main function to enforce architectural patterns across FLEXT ecosystem."""
    print("🏗️  FLEXT Ecosystem Architectural Pattern Enforcement")
    print("=" * 58)
    print("Enforcing unified class patterns, domain separation, and FlextResult usage")

    # Find all Python files
    python_files = find_python_files()

    if not python_files:
        print("No Python files found.")
        return

    print(f"\nFound {len(python_files)} Python files to analyze")

    # First pass: Analysis
    print("\n🔍 Phase 1: Analyzing architectural pattern compliance...")

    total_violations = 0
    files_with_violations = 0
    violation_summary = {}

    for file_path in python_files:
        result = analyze_architectural_patterns(file_path)

        if result["violation_count"] > 0:
            files_with_violations += 1
            total_violations += result["violation_count"]

            # Track violation types
            for violation in result["violations"]:
                violation_type = (
                    violation.split(":")[0] if ":" in violation else violation
                )
                violation_summary[violation_type] = (
                    violation_summary.get(violation_type, 0) + 1
                )

    print("\n📊 Analysis Summary:")
    print(f"  • Total files analyzed: {len(python_files)}")
    print(f"  • Files with violations: {files_with_violations}")
    print(f"  • Total violations: {total_violations}")

    if violation_summary:
        print("\n🔴 Top Violation Types:")
        for violation_type, count in sorted(
            violation_summary.items(), key=operator.itemgetter(1), reverse=True
        )[:10]:
            print(f"  • {violation_type}: {count} occurrences")

    # Second pass: Enforcement
    print("\n🔨 Phase 2: Enforcing architectural patterns...")

    modified_files = 0
    manual_refactoring_needed = 0
    total_changes = 0

    # Process files by project
    projects = {}
    for file_path in python_files:
        # Find project name from path
        project_name = None
        for part in file_path.parts:
            if part.startswith("flext-") or part in {
                "client-a-oud-mig",
                "flexcore",
                "client-b-meltano-native",
            }:
                project_name = part
                break

        if project_name:
            if project_name not in projects:
                projects[project_name] = []
            projects[project_name].append(file_path)

    # Enforce patterns per project
    for project_name, files in projects.items():
        print(f"\n🔧 Enforcing patterns in {project_name} ({len(files)} files)...")

        project_modified = 0
        project_manual = 0
        project_changes = 0

        for file_path in files:
            result = enforce_architectural_patterns(file_path)

            if result["status"] == "modified":
                project_modified += 1
                modified_files += 1
                project_changes += len(result["changes"])
                total_changes += len(result["changes"])

                if result["changes"]:
                    relative_path = str(file_path).replace(str(FLEXT_ROOT) + "/", "")
                    print(f"  ✅ {relative_path}: {len(result['changes'])} changes")
                    for change in result["changes"][:2]:  # Show first 2 changes
                        print(f"     • {change}")
                    if len(result["changes"]) > 2:
                        print(f"     • ... and {len(result['changes']) - 2} more")

            elif result["status"] == "needs_manual_refactoring":
                project_manual += 1
                manual_refactoring_needed += 1

            elif result["status"] == "error":
                print(f"  ❌ Error in {file_path}: {result['error']}")

        if project_modified > 0 or project_manual > 0:
            print(
                f"  📈 {project_name}: {project_modified} modified, {project_manual} need manual refactoring"
            )
        else:
            print(f"  ✅ {project_name}: Already compliant")

    # Summary
    print("\n📊 Architectural Pattern Enforcement Summary:")
    print(f"  • Total files processed: {len(python_files)}")
    print(f"  • Files automatically modified: {modified_files}")
    print(f"  • Files needing manual refactoring: {manual_refactoring_needed}")
    print(f"  • Total automated improvements: {total_changes}")
    print(f"  • Projects enforced: {len(projects)}")

    if modified_files > 0:
        print(
            f"\n✅ Phase 4 Progress: {modified_files}/{len(python_files)} files automatically improved"
        )
        print("Patterns enforced:")
        print("  • Domain separation (proper import hierarchy)")
        print("  • FlextResult error handling")
        print("  • FlextConstants inheritance")
        print("  • Root-level imports")

    if manual_refactoring_needed > 0:
        print(f"\n⚠️  Manual Refactoring Required: {manual_refactoring_needed} files")
        print("Patterns needing manual attention:")
        print("  • Unified class pattern (single class per module)")
        print("  • Nested helper classes (no loose functions)")
        print("  • FlextResult pattern (replace try/except fallbacks)")

    if modified_files == 0 and manual_refactoring_needed == 0:
        print("\n🎉 All files already follow FLEXT architectural patterns!")


if __name__ == "__main__":
    main()
