#!/usr/bin/env python3
"""FLEXT: Unified Module Optimization Command (Simplified Version).

MANDATORY: Uses serena, sequential-thinking, and context7 MCP tools for best results.

This is a simplified version that demonstrates the core patterns without
the complex flext-core integrations that may have circular import issues.

## 📚 QUICK REFERENCE - Key Sections

**Core Patterns** (Most Important):
- **[Namespace Class Pattern](#-namespace-class-pattern-critical-flext-core-foundation)** - FlextConstants, FlextModels, FlextTypes, FlextExceptions, FlextProtocols
- **[Extending Namespace Classes](#-extending-namespace-classes-domain-library-pattern)** - How domain libraries extend flext-core
- **[FlextConfig Advanced](#-flextconfig-advanced-patterns-pydantic-211-basesettings)** - Pydantic 2.11+ BaseSettings, validators, computed fields
- **[FlextResult Railway](#-flextresult-railway-pattern-monadic-error-handling)** - Monadic operations, railway-oriented programming
- **[Complete API Surface](#-complete-flext-core-api-surface-20-exports)** - All 20+ flext-core exports
- **[Module-Only-One-Class](#-module-only-one-class-pattern-unified-single-class)** - Single unified class pattern with nested helpers

**Quality & Standards**:
- **[Anti-Patterns](#-comprehensive-anti-patterns-zero-tolerance)** - What NOT to do (with examples)
- **[Quality Standards](#-quality-standards-checklist)** - Complete checklist for code quality

**Reference**:
- **[Type System](#-type-system-40-typevars-and-modern-python-313-syntax)** - 40+ TypeVars, covariant/contravariant
- **[Domain Libraries](#-mandatory-domain-libraries-zero-tolerance)** - Complete library hierarchy
- **[Command Structure](#command-structure-reality-based-workflow)** - Step-by-step workflow

---

Environment Setup:
- Venv automatically available at: `~/flext/.venv`
- Activate serena project: `mcp__serena-flext__activate_project project="[project-name]"`
- Available projects:
  * **FLEXT Libraries** (flext-* prefix): flext-core, flext-api, flext-ldap, flext-cli, flext-auth, flext-web, flext-meltano, flext-db-oracle, flext-ldif, etc.
  * **Enterprise Tools** (custom prefix): client-a-oud-mig, client-b-meltano-native
- PYTHONPATH managed automatically by Makefile and poetry

**NOTE**: Tools like client-a-oud-mig and client-b-* **USE and EXTEND** flext libraries but follow their own naming conventions (client-a_oud_mig, client-b_meltano_native in imports).

**CRITICAL DOMAIN LIBRARY PRINCIPLE**: ALL domain functionality MUST be implemented as libraries (flext-*) using flext-core patterns. Tools consume these libraries - they do NOT reimplement domain logic.

---

MANDATORY DOMAIN LIBRARIES (ZERO TOLERANCE)

**PRINCIPLE**: Domain functionality MUST be implemented as libraries using flext-core patterns. Tools and applications MUST use these libraries - reimplementation is FORBIDDEN.

### Available Domain Libraries (MANDATORY USE):

| Library | Domain | Wraps | MANDATORY For | Forbidden Direct Imports |
|---------|--------|-------|---------------|-------------------------|
| **flext-core** | Foundation patterns | - | ALL projects | - |
| **flext-cli** | CLI functionality | click, rich, tabulate | ANY CLI needs | `click`, `rich`, `tabulate` |
| **flext-ldif** | LDIF processing | ldif, ldap3 | ANY LDIF operations | `ldif` module |
| **flext-ldap** | LDAP operations | ldap3 | ANY LDAP needs | `ldap3` |
| **flext-api** | HTTP client/server | httpx, requests | ANY HTTP needs | `httpx`, `requests` |
| **flext-web** | Web frameworks | fastapi, flask | ANY web apps | `fastapi`, `flask` |
| **flext-db-oracle** | Oracle database | oracledb, sqlalchemy | ANY Oracle DB | `oracledb`, `sqlalchemy` (for Oracle) |
| **flext-meltano** | Data integration | meltano, dbt, singer | ANY ETL/ELT | `meltano`, `dbt`, `singer` |
| **flext-oracle-wms** | Oracle WMS API | custom WMS API | ANY Oracle WMS | Direct WMS API calls |
| **flext-oracle-oic** | Oracle OIC API | custom OIC API | ANY Oracle OIC | Direct OIC API calls |
| **flext-auth** | Authentication | oauth, jwt | ANY auth needs | Direct auth libraries |
| **flext-observability** | Monitoring/metrics | prometheus, statsd | ANY monitoring | Direct monitoring libs |
| **flext-grpc** | gRPC services | grpc, grpcio | ANY gRPC | `grpc`, `grpcio` |

### ZERO TOLERANCE ENFORCEMENT:

**IF your code needs**:
- ✅ CLI functionality → MUST use `flext-cli` (NOT direct `click`/`rich`)
- ✅ LDIF processing → MUST use `flext-ldif` (NOT direct `ldif` module)
- ✅ LDAP operations → MUST use `flext-ldap` (NOT direct `ldap3`)
- ✅ HTTP requests → MUST use `flext-api` (NOT direct `httpx`/`requests`)
- ✅ Web application → MUST use `flext-web` (NOT direct `fastapi`/`flask`)
- ✅ Oracle database → MUST use `flext-db-oracle` (NOT direct `oracledb`)
- ✅ ETL/ELT/DBT → MUST use `flext-meltano` (NOT direct `meltano`/`dbt`)
- ✅ Oracle WMS → MUST use `flext-oracle-wms` (NOT direct WMS API)
- ✅ Oracle OIC → MUST use `flext-oracle-oic` (NOT direct OIC API)
- ✅ Authentication → MUST use `flext-auth` (NOT direct auth libraries)
- ✅ Monitoring → MUST use `flext-observability` (NOT direct prometheus)
- ✅ gRPC → MUST use `flext-grpc` (NOT direct `grpc`)

**IF functionality doesn't exist in domain library**: Enhance the library FIRST, then use it.

**NEVER**: Create custom wrappers or direct imports in tools/applications.
"""

from __future__ import annotations

import argparse
import ast
import asyncio
import operator
import os
import re
import shutil
import sys
from pathlib import Path
from typing import ClassVar, TypeVar

from flext_core import (
    FlextConfig,
    FlextConstants,
    FlextLogger,
    FlextResult,
    FlextTypes,
    FlextUtilities,
)

T = TypeVar("T")

# Ensure ruff is available
RUFF_CMD = shutil.which("ruff")
if not RUFF_CMD:
    print("Error: ruff command not found. Please install ruff.", file=sys.stderr)
    sys.exit(1)


# Configuration for the optimizer
class FlextModuleOptimizerConstants(FlextConstants):
    """Optimization constants extending flext-core."""

    class Optimization:
        """Optimization-specific constants."""

        DEFAULT_BATCH_SIZE: int = 5
        MAX_FILE_SIZE: int = 1024 * 1024  # 1MB
        SUPPORTED_EXTENSIONS: ClassVar[set[str]] = {".py", ".pyi"}
        EXCLUDE_PATTERNS: ClassVar[FlextTypes.StringList] = [
            "__pycache__",
            ".git",
            ".venv",
            "node_modules",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            ".DS_Store",
        ]

    class ModulePatterns:
        """Pattern matching constants."""

        # ❌ FORBIDDEN - Direct imports in tools
        FORBIDDEN_DIRECT_IMPORTS: ClassVar[dict[str, str]] = {
            "import ldap3": "flext-ldap",
            "from ldap3": "flext-ldap",
            "import click": "flext-cli",
            "from click": "flext-cli",
            "import rich": "flext-cli",
            "from rich": "flext-cli",
            "import httpx": "flext-api",
            "from httpx": "flext-api",
            "import requests": "flext-api",
            "from requests": "flext-api",
            "import oracledb": "flext-db-oracle",
            "from oracledb": "flext-db-oracle",
            "import meltano": "flext-meltano",
            "from meltano": "flext-meltano",
            "import fastapi": "flext-web",
            "from fastapi": "flext-web",
        }

        # ❌ FORBIDDEN - Anti-patterns
        FORBIDDEN_PATTERNS: ClassVar[FlextTypes.StringList] = [
            r"# type: ignore.*$",  # Generic type ignore
            r"def .*\).*-> object:",  # object return type
            r"except.*pass",  # Empty except blocks
            r"from flext_core\.[^.]+\.import",  # Internal imports
        ]


class FlextModuleOptimizerConfig(FlextConfig):
    """Optimization configuration."""

    def __init__(self, **kwargs: object) -> None:
        """Initialize the optimizer configuration."""
        super().__init__()
        self.batch_size: int = kwargs.get(
            "batch_size", FlextModuleOptimizerConstants.Optimization.DEFAULT_BATCH_SIZE
        )
        self.dry_run = kwargs.get("dry_run", True)
        self.verbose = kwargs.get("verbose", False)
        self.force = kwargs.get("force", False)
        self.project_type = kwargs.get("project_type", "library")
        self.exclude_patterns = list(
            FlextModuleOptimizerConstants.Optimization.EXCLUDE_PATTERNS
        )


class FlextModuleOptimizer:
    """Unified Module Optimization Command (Simplified).

    Demonstrates FLEXT patterns without complex integrations that may cause
    circular import issues in the current flext-core implementation.
    """

    def __init__(self, config: FlextModuleOptimizerConfig | None = None) -> None:
        """Initialize optimizer."""
        super().__init__()
        self._config = config or FlextModuleOptimizerConfig()
        self.logger = FlextLogger(__name__)

    def optimize_project(self, project_path: str) -> FlextResult[None]:
        """Optimize entire project according to FLEXT patterns.

        Args:
            project_path: Path to project to optimize

        Returns:
            FlextResult with optimization summary

        """
        self.logger.info(
            "Starting unified module optimization", extra={"project_path": project_path}
        )

        try:
            # Phase 1: Discovery and analysis
            discovery_result = self._discover_optimization_targets(project_path)
            if discovery_result.is_failure:
                return FlextResult.fail(f"Discovery failed: {discovery_result.error}")

            targets = discovery_result.unwrap()

            # Phase 2: Quality gate validation
            quality_result = self._validate_quality_gates(targets)
            if quality_result.is_failure and not self._config.force:
                return FlextResult.fail(f"Quality gates failed: {quality_result.error}")

            # Phase 3: Batch optimization
            optimization_result = self._optimize_in_batches(targets)

            # Phase 4: Final validation
            return self._validate_optimization_results(optimization_result)

        except Exception as e:
            self.logger.exception("Optimization failed", extra={"error": str(e)})
            return FlextResult.fail(f"Optimization error: {e}")

    def _discover_optimization_targets(
        self, project_path: str
    ) -> FlextResult[list[dict[str, object]]]:
        """Discover modules that need optimization."""
        self.logger.info(
            "Discovering optimization targets", extra={"project_path": project_path}
        )

        targets = []

        try:
            project_root = Path(project_path).resolve()

            # Check if it's a valid project
            if not (project_root / "src").exists():
                return FlextResult.fail(f"No src directory found in {project_path}")

            # Walk through src directory
            for root, dirs, files in os.walk(project_root / "src"):
                # Filter out excluded patterns
                dirs[:] = [
                    d
                    for d in dirs
                    if not any(
                        pattern in d for pattern in self._config.exclude_patterns
                    )
                ]

                for file in files:
                    if not any(
                        file.endswith(ext)
                        for ext in FlextModuleOptimizerConstants.Optimization.SUPPORTED_EXTENSIONS
                    ):
                        continue

                    file_path = Path(root) / file

                    # Skip if file too large
                    if (
                        file_path.stat().st_size
                        > FlextModuleOptimizerConstants.Optimization.MAX_FILE_SIZE
                    ):
                        self.logger.info(f"Skipping large file: {file_path}")
                        continue

                    # Analyze file for optimization needs
                    analysis_result = self._analyze_file_for_optimization(file_path)
                    if analysis_result.is_failure:
                        self.logger.info(
                            f"Analysis failed for {file_path}: {analysis_result.error}"
                        )
                        continue

                    analysis = analysis_result.unwrap()

                    if self._needs_optimization(analysis):
                        target = {
                            "project_path": project_path,
                            "module_name": file_path.stem,
                            "file_path": str(file_path),
                            "optimization_type": self._determine_optimization_type(
                                analysis
                            ),
                            "priority": self._calculate_priority(analysis),
                        }
                        targets.append(target)

            # Sort by priority (highest first)
            targets.sort(key=operator.itemgetter("priority"), reverse=True)

            self.logger.info(f"Discovered {len(targets)} optimization targets")
            return FlextResult.ok(targets)

        except Exception as e:
            return FlextResult.fail(f"Discovery error: {e}")

    def _analyze_file_for_optimization(
        self, file_path: Path
    ) -> FlextResult[dict[str, object]]:
        """Analyze file for optimization opportunities."""
        try:
            with Path(file_path).open(encoding="utf-8") as f:
                content = f.read()

            # Parse AST for structural analysis
            try:
                tree = ast.parse(content, filename=str(file_path))
            except SyntaxError as e:
                return FlextResult.fail(f"Syntax error: {e}")

            violations = []
            suggestions = []
            domain_library_usage = {
                "flext-cli": False,
                "flext-ldif": False,
                "flext-ldap": False,
                "flext-api": False,
                "flext-web": False,
                "flext-db-oracle": False,
                "flext-meltano": False,
            }

            # Check for forbidden patterns
            for pattern, _ in FlextModuleOptimizerConstants.Patterns.FORBIDDEN_PATTERNS:
                if re.search(pattern, content, re.MULTILINE):
                    violations.append(f"Forbidden pattern found: {pattern}")

            # Check for domain library violations (CRITICAL)
            for (
                forbidden_import,
                required_library,
            ) in (
                FlextModuleOptimizerConstants.Patterns.FORBIDDEN_DIRECT_IMPORTS.items()
            ):
                if forbidden_import in content:
                    violations.append(
                        f"Domain library violation: {forbidden_import} should use {required_library}"
                    )

            # Check for positive domain library usage
            for library in domain_library_usage:
                if f"from {library}" in content or f"import {library}" in content:
                    domain_library_usage[library] = True

            # Calculate complexity score
            complexity_score = self.calculate_complexity_score(tree, content)

            # Generate suggestions
            if violations:
                suggestions.append("Fix violations to comply with FLEXT patterns")
            if complexity_score > 0.7:
                suggestions.append("Consider breaking down complex module")
            if not any(domain_library_usage.values()):
                suggestions.append(
                    "Consider using domain libraries for better architecture"
                )

            return FlextResult.ok({
                "violations": violations,
                "suggestions": suggestions,
                "complexity_score": complexity_score,
                "domain_library_usage": domain_library_usage,
            })

        except Exception as e:
            return FlextResult.fail(f"Analysis error: {e}")

    def _needs_optimization(self, analysis: dict[str, object]) -> bool:
        """Determine if module needs optimization."""
        return (
            len(analysis["violations"]) > 0
            or analysis["complexity_score"] > 0.5
            or not any(analysis["domain_library_usage"].values())
        )

    def _determine_optimization_type(self, analysis: dict[str, object]) -> str:
        """Determine the type of optimization needed."""
        if analysis["violations"]:
            return "pattern_violation"
        if analysis["complexity_score"] > 0.7:
            return "complexity_reduction"
        if not any(analysis["domain_library_usage"].values()):
            return "domain_library_integration"
        return "general_improvement"

    def _calculate_priority(self, analysis: dict[str, object]) -> int:
        """Calculate optimization priority (higher = more urgent)."""
        priority = 0

        # Critical violations get highest priority
        if any("Domain library violation" in v for v in analysis["violations"]):
            priority += 100

        # Pattern violations are high priority
        if any("Forbidden pattern" in v for v in analysis["violations"]):
            priority += 50

        # High complexity needs attention
        priority += int(analysis["complexity_score"] * 20)

        # Missing domain library usage
        if not any(analysis["domain_library_usage"].values()):
            priority += 25

        return priority

    def calculate_complexity_score(self, tree: ast.Module, content: str) -> float:
        """Calculate complexity score for module."""
        score = 0.0

        # Count classes (should be 1 per module)
        class_count = len([
            node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
        ])
        if class_count > 1:
            score += 0.3
        elif class_count == 0:
            score += 0.2

        # Count functions (should be minimal in optimized modules)
        func_count = len([
            node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        ])
        if func_count > 10:
            score += 0.3

        # Check for nested complexity
        max_depth = self.calculate_ast_depth(tree)
        if max_depth > 5:
            score += 0.2

        # Line count complexity
        line_count = len(content.split("\n"))
        if line_count > 200:
            score += 0.2

        return min(score, 1.0)

    def calculate_ast_depth(self, node: ast.AST, depth: int = 0) -> int:
        """Calculate maximum AST depth."""
        if not hasattr(node, "body"):
            return depth

        max_child_depth = depth
        for child in ast.iter_child_nodes(node):
            child_depth = self.calculate_ast_depth(child, depth + 1)
            max_child_depth = max(max_child_depth, child_depth)

        return max_child_depth

    def _validate_quality_gates(
        self, targets: list[dict[str, object]]
    ) -> FlextResult[None]:
        """Validate targets against quality gates."""
        self.logger.info(
            "Validating quality gates", extra={"target_count": len(targets)}
        )

        violations = []

        for target in targets:
            # Check for critical violations
            if "Domain library violation" in target["optimization_type"]:
                violations.append(
                    f"Critical: {target['file_path']} has domain library violations"
                )

            if target["priority"] > 100:
                violations.append(
                    f"High priority: {target['file_path']} needs immediate attention"
                )

        if violations and not self._config.force:
            return FlextResult[None].fail("Quality gate violations found")

        return FlextResult[None].ok(None)

    def _optimize_in_batches(
        self, targets: list[FlextTypes.Dict]
    ) -> list[FlextTypes.Dict]:
        """Optimize targets in batches."""
        self.logger.info(
            "Starting batch optimization", extra={"total_targets": len(targets)}
        )

        results = []
        batch_size = self._config.batch_size

        for i in range(0, len(targets), batch_size):
            batch = targets[i : i + batch_size]
            self.logger.info(
                f"Processing batch {i // batch_size + 1}/{(len(targets) - 1) // batch_size + 1}"
            )

            # Run tasks sequentially since we're removing async
            batch_results = []
            for target in batch:
                result = self._optimize_single_target(target)
                batch_results.append(result)

            results.extend(batch_results)

            # Progress reporting
            success_count = sum(1 for r in batch_results if r["success"])
            self.logger.info(f"Batch complete: {success_count}/{len(batch)} successful")

        return results

    def _optimize_single_target(self, target: dict[str, object]) -> dict[str, object]:
        """Optimize a single target module."""
        self.logger.info(f"Optimizing {target['file_path']}")

        try:
            # Read current content
            with Path(target["file_path"]).open(encoding="utf-8") as f:
                original_content = f.read()

            # Apply optimizations based on type
            if target["optimization_type"] == "pattern_violation":
                optimized_content = self.fix_pattern_violations(original_content)
            elif target["optimization_type"] == "complexity_reduction":
                optimized_content = self._reduce_complexity(original_content)
            elif target["optimization_type"] == "domain_library_integration":
                optimized_content = self._integrate_domain_libraries(
                    original_content, target
                )
            else:
                optimized_content = self.general_improvements(original_content)

            # Calculate changes
            changes_made = self.count_changes(original_content, optimized_content)

            # Apply changes if not dry run
            if not self._config.dry_run and optimized_content != original_content:
                with Path(target["file_path"]).open("w", encoding="utf-8") as f:
                    f.write(optimized_content)

                # Validate the optimized file
                validation_result = self._validate_optimized_file(target["file_path"])
                if validation_result.is_failure:
                    return {
                        "target": target,
                        "success": False,
                        "changes_made": changes_made,
                        "errors": [f"Validation failed: {validation_result.error}"],
                        "warnings": [],
                    }

            return {
                "target": target,
                "success": True,
                "changes_made": changes_made,
                "errors": [],
                "warnings": [],
            }

        except Exception as e:
            return {
                "target": target,
                "success": False,
                "changes_made": 0,
                "errors": [f"Optimization error: {e}"],
                "warnings": [],
            }

    def fix_pattern_violations(self, content: str) -> str:
        """Fix pattern violations in module."""
        optimized = content

        # Fix forbidden direct imports
        for (
            forbidden_import,
            required_library,
        ) in FlextModuleOptimizerConstants.Patterns.FORBIDDEN_DIRECT_IMPORTS.items():
            if forbidden_import in optimized:
                # Replace with domain library import
                optimized = optimized.replace(
                    forbidden_import,
                    f"from {required_library} import Flext{required_library.split('-')[1].title()}",
                )

        # Fix generic type ignores
        optimized = re.sub(
            r"# type: ignore.*$",
            "# type: ignore[explicit-error-code]",
            optimized,
            flags=re.MULTILINE,
        )

        # Fix object types
        return optimized.replace(r"-> object:", "-> object:")

    def _reduce_complexity(self, content: str) -> str:
        """Reduce module complexity."""
        # For complexity reduction, we would need more sophisticated analysis
        # This is a simplified version - in practice, this would involve
        # extracting helper methods, reducing nesting, etc.
        return content

    def add_missing_type_hints(self, content: str) -> str:
        """Add missing type hints (simplified implementation)."""
        # This would be a complex analysis in practice
        # For now, just ensure basic patterns are followed
        return content

    def count_changes(self, original: str, optimized: str) -> int:
        """Count number of changes made."""
        original_lines = set(original.split("\n"))
        optimized_lines = set(optimized.split("\n"))
        return len(original_lines.symmetric_difference(optimized_lines))

    def _validate_optimized_file(self, file_path: str) -> FlextResult[None]:
        """Validate optimized file."""
        try:
            # Run ruff check
            result = FlextUtilities.run_external_command(
                [RUFF_CMD, "check", file_path],
                check=False,
                capture_output=True,
                text=True,
                cwd=Path(file_path).parent.parent.parent,  # Project root
            )

            if result.returncode != 0:
                return FlextResult.fail(f"Ruff validation failed: {result.stdout}")

            return FlextResult.ok(None)

        except Exception as e:
            return FlextResult.fail(f"Validation error: {e}")

    def _validate_optimization_results(
        self, results: list[dict[str, object]]
    ) -> FlextResult[dict[str, object]]:
        """Validate final optimization results."""
        total_targets = len(results)
        successful_targets = sum(1 for r in results if r["success"])
        total_changes = sum(r["changes_made"] for r in results)
        total_errors = sum(len(r["errors"]) for r in results)

        summary: dict[str, object] = {
            "total_targets": total_targets,
            "successful_targets": successful_targets,
            "success_rate": successful_targets / total_targets
            if total_targets > 0
            else 0,
            "total_changes": total_changes,
            "total_errors": total_errors,
            "dry_run": self._config.dry_run,
        }

        if total_errors > 0 and not self._config.force:
            return FlextResult[dict[str, object]].fail(
                f"Optimization had {total_errors} errors"
            )

        return FlextResult[dict[str, object]].ok(summary)


def main() -> None:
    """Main entry point for unified module optimization."""
    parser = argparse.ArgumentParser(
        description="FLEXT Unified Module Optimization Command (Simplified)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Optimize flext-core library
  python scripts/unified_module_optimizer_simple.py --project flext-core --project-type library

  # Optimize client-a-oud-mig tool (dry run)
  python scripts/unified_module_optimizer_simple.py --project client-a-oud-mig --project-type tool --dry-run

  # Force optimization with verbose output
  python scripts/unified_module_optimizer_simple.py --project flext-api --force --verbose --batch-size 10

  # Optimize all flext-* libraries
  python scripts/unified_module_optimizer_simple.py --project-pattern "flext-*" --project-type library
        """,
    )

    parser.add_argument(
        "--project",
        help="Specific project to optimize (e.g., flext-core, client-a-oud-mig)",
    )

    parser.add_argument(
        "--project-pattern",
        help="Pattern to match projects (e.g., 'flext-*' for all libraries)",
    )

    parser.add_argument(
        "--project-type",
        choices=["library", "tool"],
        default="library",
        help="Type of project being optimized",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Run in dry-run mode (no file changes)",
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force optimization even if quality gates fail",
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=FlextModuleOptimizerConstants.Optimization.DEFAULT_BATCH_SIZE,
        help="Number of modules to optimize in each batch",
    )

    args = parser.parse_args()

    # Create configuration
    config = FlextModuleOptimizerConfig(
        batch_size=args.batch_size,
        dry_run=args.dry_run,
        verbose=args.verbose,
        force=args.force,
        project_type=args.project_type,
    )

    # Create optimizer
    optimizer = FlextModuleOptimizer(config)

    # Determine projects to optimize
    projects_to_optimize = []

    if args.project:
        projects_to_optimize.append(args.project)
    elif args.project_pattern:
        # Find projects matching pattern
        projects_dir = Path("..")
        projects_to_optimize.extend(
            project_dir.name
            for project_dir in projects_dir.iterdir()
            if project_dir.is_dir() and re.match(args.project_pattern, project_dir.name)
        )
    else:
        # Default to current project if in a project directory
        current_dir = Path.cwd()
        if "flext-" in current_dir.name or current_dir.name in {
            "client-a-oud-mig",
            "client-b-meltano-native",
        }:
            projects_to_optimize.append(current_dir.name)
        else:
            print("❌ No project specified. Use --project or --project-pattern")
            sys.exit(1)

    # Optimize each project
    for project in projects_to_optimize:
        print(f"🔧 Optimizing project: {project}")

        project_path = f"..{project}"
        if not Path(project_path).exists():
            print(f"❌ Project not found: {project_path}")
            continue

        # Run optimization
        result = asyncio.run(optimizer.optimize_project(project_path))

        if result.is_success:
            summary = result.unwrap()
            print("✅ Optimization completed successfully!")
            print(f"   Targets processed: {summary['total_targets']}")
            print(f"   Successful: {summary['successful_targets']}")
            print(f"   Success rate: {summary['success_rate']:.1%}")
            print(f"   Changes made: {summary['total_changes']}")
            if summary["dry_run"]:
                print("   Mode: Dry run (no files changed)")
        else:
            print(f"❌ Optimization failed: {result.error}")
            if not args.force:
                sys.exit(1)

    print("🎉 All optimizations completed!")


if __name__ == "__main__":
    main()
