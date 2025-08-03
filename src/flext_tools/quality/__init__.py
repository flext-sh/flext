"""FLEXT Tools Quality - Enterprise Code Quality Gates and Enforcement.

Provides comprehensive code quality assurance utilities for the FLEXT ecosystem,
implementing automated quality gates, linting enforcement, type checking, and
quality metrics collection across all 32 FLEXT projects. This module ensures
consistent code quality standards and automated validation throughout the
distributed development environment.

Quality tools integrate with CI/CD pipelines to enforce enterprise-grade
standards, providing detailed reporting, automated fixes, and gradual quality
improvement strategies. All quality operations support both individual project
validation and ecosystem-wide quality coordination.

Key Components:
    - QualityGateway: Centralized quality gate coordination and enforcement
    - GradualLintFixer: Progressive linting improvement with automated fixes
    - MyPyChecker: Type checking validation with comprehensive error reporting
    - Quality Metrics: Code quality measurement and trend analysis
    - Standards Enforcement: Consistent application of quality standards

Architecture:
    Implements quality assurance patterns with proper abstraction layers,
    supporting both development workflows and production quality gates.
    Integrates with external tools while providing consistent interfaces
    and comprehensive error handling throughout the quality process.

Example:
    Quality gate enforcement for development workflows:

    >>> from flext_tools.quality import QualityGateway, MyPyChecker
    >>> from flext_tools.quality import GradualLintFixer
    >>> from pathlib import Path
    >>>
    >>> # Initialize quality gateway for ecosystem validation
    >>> gateway = QualityGateway(
    ...     workspace_root=Path("/home/developer/flext-workspace"),
    ...     enforce_strict=True,
    ...     generate_reports=True,
    ... )
    >>>
    >>> # Run comprehensive quality validation
    >>> result = gateway.validate_all_projects()
    >>> if result.success:
    ...     print(
    ...         f"Quality validation passed for {result.value.projects_validated} projects"
    ...     )
    ...     print(f"Overall quality score: {result.value.quality_score}")
    >>> else:
    ...     print(f"Quality issues found: {result.error}")
    >>>
    >>> # Progressive linting improvement
    >>> linter = GradualLintFixer(target_project="flext-core")
    >>> fix_result = linter.apply_gradual_fixes(max_changes=50)
    >>>
    >>> # Type checking validation
    >>> type_checker = MyPyChecker()
    >>> type_result = type_checker.validate_project("flext-api")
    >>> print(f"Type coverage: {type_result.value.coverage_percentage}%")

Integration:
    - Built on flext-core patterns with FlextResult error handling
    - Integrates with flext-observability for quality metrics and monitoring
    - Coordinates with CI/CD pipelines for automated quality enforcement
    - Supports multiple linting tools (Ruff, Black, MyPy) with unified interface
    - Provides foundation for quality-driven development workflows

Quality Standards:
    - Comprehensive error handling with detailed validation context
    - Full type annotation coverage for enhanced development experience
    - Extensive integration testing with real project scenarios
    - Performance optimization for large-scale quality operations
    - Security-conscious tool execution and result processing

Author: FLEXT Development Team
Version: 2.0.0
License: MIT

"""

from flext_tools.quality.gateway import QualityGateway
from flext_tools.quality.lint_fixer import GradualLintFixer
from flext_tools.quality.mypy_checker import MyPyChecker

__all__ = ["GradualLintFixer", "MyPyChecker", "QualityGateway"]
