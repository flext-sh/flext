"""FLEXT Tools Types - Domain-specific development tools type definitions.

This module provides development tools-specific type definitions extending FlextTypes.
Follows FLEXT standards:
- Domain-specific complex types only
- No simple aliases to primitive types
- Python 3.13+ syntax
- Extends FlextTypes properly

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Literal

from flext_core import FlextTypes

# =============================================================================
# TOOLS-SPECIFIC TYPE VARIABLES - Domain-specific TypeVars for development tools operations
# =============================================================================


class FlextToolsTypes(FlextTypes):
    """Development tools-specific type definitions extending FlextTypes.

    Domain-specific type system for development tools operations.
    Contains ONLY complex development tools-specific types, no simple aliases.
    Uses Python 3.13+ type syntax and patterns.
    """

    # =========================================================================
    # DEVELOPMENT TOOLS DOMAIN TYPES - Complex development tools types
    # =========================================================================

    class Core:
        """Core development tools types extending FlextTypes.Core."""

        # Build and deployment configuration types
        type BuildConfigDict = dict[
            str, FlextTypes.Core.ConfigValue | list[str] | dict[str, object]
        ]
        type BuildResultDict = dict[str, str | int | float | bool | list[str]]
        type ArtifactDict = dict[str, str | int | FlextTypes.Core.JsonValue]

        # Code analysis and quality types
        type AnalysisConfigDict = dict[
            str, FlextTypes.Core.ConfigValue | dict[str, object]
        ]
        type AnalysisResultDict = dict[str, str | int | float | bool | list[object]]
        type QualityMetricsDict = dict[str, int | float | bool | dict[str, object]]

        # Testing and validation types
        type TestConfigDict = dict[
            str, FlextTypes.Core.ConfigValue | list[str] | dict[str, object]
        ]
        type TestResultDict = dict[str, str | int | float | bool | list[str]]
        type CoverageReportDict = dict[str, float | int | dict[str, float]]

        # Documentation generation types
        type DocConfigDict = dict[
            str, FlextTypes.Core.ConfigValue | list[str] | dict[str, object]
        ]
        type DocResultDict = dict[str, str | int | float | bool | list[str]]
        type DocumentationDict = dict[str, str | int | list[str] | dict[str, object]]

        # Environment management types
        type EnvironmentConfigDict = dict[
            str, FlextTypes.Core.ConfigValue | dict[str, str] | list[str]
        ]
        type EnvironmentStatusDict = dict[str, str | int | float | bool | list[str]]
        type PackageInfoDict = dict[str, str | dict[str, str] | list[str]]

        # Tool management types
        type ToolConfigDict = dict[
            str, FlextTypes.Core.ConfigValue | list[str] | dict[str, object]
        ]
        type ToolResultDict = dict[str, str | int | float | bool]
        type ToolExecutionDict = dict[str, str | int | float | bool | list[str]]

        # Development workflow types
        type WorkflowConfigDict = dict[
            str, FlextTypes.Core.ConfigValue | list[dict[str, object]]
        ]
        type WorkflowStepDict = dict[str, str | bool | dict[str, object]]
        type PipelineConfigDict = dict[
            str, FlextTypes.Core.ConfigValue | list[dict[str, object]]
        ]

    # =========================================================================
    # BUILD DOMAIN TYPES - Build system specific types
    # =========================================================================

    class Build:
        """Build system domain types."""

        type BuildTarget = Literal["debug", "release", "test", "production"]
        type BuildPlatform = Literal["linux", "windows", "macos", "cross"]
        type OptimizationLevel = Literal["O0", "O1", "O2", "O3", "Os", "Oz"]
        type CompilerType = Literal["gcc", "clang", "msvc", "mingw"]

        type BuildManifest = dict[
            str,
            FlextTypes.Core.ConfigValue | list[str] | dict[str, str | bool | list[str]],
        ]

        type BuildArtifacts = dict[str, str | int | list[str] | dict[str, str | int]]

    # =========================================================================
    # ANALYSIS DOMAIN TYPES - Code analysis specific types
    # =========================================================================

    class Analysis:
        """Code analysis domain types."""

        type AnalysisTool = Literal[
            "ruff",
            "mypy",
            "pyright",
            "bandit",
            "safety",
            "pylint",
            "flake8",
            "black",
            "isort",
            "coverage",
        ]
        type SeverityLevel = Literal["error", "warning", "info", "note"]
        type IssueCategory = Literal[
            "syntax",
            "type",
            "security",
            "style",
            "complexity",
            "duplication",
            "performance",
            "maintainability",
        ]

        type IssueReport = dict[
            str, str | int | float | dict[str, str | int] | list[dict[str, str | int]]
        ]

        type QualityGate = dict[
            str, FlextTypes.Core.ConfigValue | dict[str, float | int | bool]
        ]

    # =========================================================================
    # TESTING DOMAIN TYPES - Testing framework specific types
    # =========================================================================

    class Testing:
        """Testing domain types."""

        type TestFramework = Literal["pytest", "unittest", "nose2", "tox", "nox"]
        type TestType = Literal[
            "unit", "integration", "functional", "e2e", "performance", "security"
        ]
        type CoverageType = Literal["line", "branch", "function", "statement"]

        type TestSuite = dict[
            str, str | int | bool | list[str] | dict[str, str | int | bool]
        ]

        type CoverageReport = dict[
            str, float | int | dict[str, float | int] | list[dict[str, float | int]]
        ]

    # =========================================================================
    # DOCUMENTATION DOMAIN TYPES - Documentation generation specific types
    # =========================================================================

    class Documentation:
        """Documentation domain types."""

        type DocFormat = Literal["html", "pdf", "markdown", "rst", "latex", "epub"]
        type DocTheme = Literal[
            "default", "readthedocs", "sphinx", "material", "alabaster"
        ]
        type DocBuilder = Literal[
            "sphinx", "mkdocs", "jupyter-book", "gitbook", "docusaurus"
        ]

        type DocTree = dict[str, str | list[str] | dict[str, str | list[str]]]

        type ApiReference = dict[
            str,
            str
            | bool
            | list[dict[str, str | bool]]
            | dict[str, str | bool | list[str]],
        ]

    # =========================================================================
    # ENVIRONMENT DOMAIN TYPES - Development environment specific types
    # =========================================================================

    class Environment:
        """Development environment domain types."""

        type PythonVersion = Literal["3.9", "3.10", "3.11", "3.12", "3.13", "3.14"]
        type PackageManager = Literal["pip", "poetry", "pipenv", "conda", "uv"]
        type VirtualEnvTool = Literal["venv", "virtualenv", "conda", "pipenv", "poetry"]

        type EnvironmentSpec = dict[
            str, FlextTypes.Core.ConfigValue | list[str] | dict[str, str | bool]
        ]

        type PackageManifest = dict[
            str, str | bool | dict[str, str | bool] | list[dict[str, str]]
        ]

    # =========================================================================
    # TOOL DOMAIN TYPES - Development tool specific types
    # =========================================================================

    class Tool:
        """Development tool domain types."""

        type ToolCategory = Literal[
            "linter",
            "formatter",
            "type-checker",
            "security",
            "test",
            "build",
            "deploy",
            "documentation",
            "monitoring",
        ]
        type ExecutionMode = Literal["sync", "async", "parallel", "sequential"]
        type OutputFormat = Literal["json", "xml", "text", "html", "junit", "tap"]

        type ToolChain = dict[
            str,
            FlextTypes.Core.ConfigValue
            | list[dict[str, str | bool]]
            | dict[str, str | bool | list[str]],
        ]

        type ExecutionContext = dict[
            str, str | int | bool | dict[str, str | int | bool] | list[str]
        ]

    # =========================================================================
    # WORKFLOW DOMAIN TYPES - Development workflow specific types
    # =========================================================================

    class Workflow:
        """Development workflow domain types."""

        type WorkflowStage = Literal[
            "pre-commit",
            "build",
            "test",
            "analysis",
            "package",
            "deploy",
            "post-deploy",
            "cleanup",
        ]
        type TriggerEvent = Literal["push", "pull_request", "tag", "schedule", "manual"]
        type ActionType = Literal["script", "command", "api_call", "notification"]

        type WorkflowDefinition = dict[
            str,
            FlextTypes.Core.ConfigValue
            | list[dict[str, str | bool | dict[str, object]]]
            | dict[str, str | bool | list[str]],
        ]

        type PipelineExecution = dict[
            str,
            str
            | int
            | bool
            | float
            | dict[str, str | int | bool]
            | list[dict[str, str | int | bool]],
        ]


# =============================================================================
# TYPE ALIASES FOR BACKWARD COMPATIBILITY
# =============================================================================

# Legacy aliases (these will be deprecated in favor of the above)
BuildConfiguration = FlextToolsTypes.Core.BuildConfigDict
TestConfiguration = FlextToolsTypes.Core.TestConfigDict
ToolConfiguration = FlextToolsTypes.Core.ToolConfigDict


__all__ = [
    "BuildConfiguration",
    "FlextToolsTypes",
    "TestConfiguration",
    "ToolConfiguration",
]
