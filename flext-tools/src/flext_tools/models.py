"""Models for development tools operations.

This module provides data models for development tools operations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from flext_core import FlextModels
from flext_tools.constants import FlextToolsConstants
from flext_tools.typings import FlextToolsTypes


class FlextToolsModels(FlextModels):
    """Comprehensive models for development tools operations extending FlextModels.

    Provides standardized models for all development tools domain entities including:
    - Build and deployment tools
    - Code analysis and quality tools
    - Testing and validation tools
    - Documentation generation tools
    - Development environment management

    All nested classes inherit FlextModels validation and patterns.
    """

    # Build and Deployment Models
    class BuildConfig(FlextModels.Configuration):
        """Build configuration model."""

        build_type: str = Field(
            default=FlextToolsConstants.Build.DEFAULT_BUILD_TYPE,
            description="Build type (debug, release)",
        )
        target_platform: str = Field(
            default=FlextToolsConstants.Build.DEFAULT_TARGET_PLATFORM,
            description="Target platform",
        )
        optimization_level: str = Field(
            default=FlextToolsConstants.Build.DEFAULT_OPTIMIZATION_LEVEL,
            description="Optimization level",
        )
        enable_tests: bool = Field(
            default=FlextToolsConstants.Build.DEFAULT_ENABLE_TESTS,
            description="Enable test execution",
        )
        enable_documentation: bool = Field(
            default=FlextToolsConstants.Build.DEFAULT_ENABLE_DOCUMENTATION,
            description="Enable documentation generation",
        )
        parallel_jobs: int = Field(
            default=FlextToolsConstants.Build.DEFAULT_PARALLEL_JOBS,
            description="Number of parallel build jobs",
        )
        build_directory: str = Field(
            default=FlextToolsConstants.Build.DEFAULT_BUILD_DIRECTORY,
            description="Build output directory",
        )

    class BuildResult(FlextModels.Entity):
        """Build result model."""

        build_id: str = Field(description="Unique build identifier")
        success: bool = Field(description="Build success status")
        duration_seconds: float = Field(description="Build duration in seconds")
        artifacts: list[str] = Field(
            default_factory=list, description="Generated artifacts"
        )
        warnings_count: int = Field(default=0, description="Number of warnings")
        errors_count: int = Field(default=0, description="Number of errors")
        build_log: str = Field(default="", description="Build log output")
        timestamp: datetime = Field(
            default_factory=datetime.now, description="Build timestamp"
        )

    # Code Analysis Models
    class AnalysisConfig(FlextModels.Configuration):
        """Code analysis configuration model."""

        enable_linting: bool = Field(default=True, description="Enable code linting")
        enable_type_checking: bool = Field(
            default=True, description="Enable type checking"
        )
        enable_security_scan: bool = Field(
            default=True, description="Enable security scanning"
        )
        enable_complexity_analysis: bool = Field(
            default=True, description="Enable complexity analysis"
        )
        max_complexity: int = Field(
            default=FlextToolsConstants.CodeAnalysis.MAX_COMPLEXITY_THRESHOLD,
            description="Maximum cyclomatic complexity",
        )
        min_coverage: float = Field(
            default=FlextToolsConstants.Testing.RECOMMENDED_COVERAGE_THRESHOLD,
            description="Minimum test coverage percentage",
        )

    class AnalysisResult(FlextModels.Entity):
        """Code analysis result model."""

        analysis_id: str = Field(description="Unique analysis identifier")
        tool_name: str = Field(description="Analysis tool name")
        success: bool = Field(description="Analysis success status")
        issues_found: int = Field(default=0, description="Number of issues found")
        critical_issues: int = Field(default=0, description="Number of critical issues")
        warning_issues: int = Field(default=0, description="Number of warning issues")
        info_issues: int = Field(default=0, description="Number of info issues")
        coverage_percentage: float = Field(
            default=0.0, description="Test coverage percentage"
        )
        report_path: str = Field(default="", description="Path to detailed report")
        timestamp: datetime = Field(
            default_factory=datetime.now, description="Analysis timestamp"
        )

    # Testing Models
    class TestConfig(FlextModels.Configuration):
        """Test configuration model."""

        test_type: str = Field(
            default="unit", description="Test type (unit, integration, e2e)"
        )
        test_patterns: list[str] = Field(
            default_factory=list, description="Test file patterns"
        )
        enable_coverage: bool = Field(
            default=True, description="Enable coverage collection"
        )
        coverage_threshold: float = Field(
            default=80.0, description="Coverage threshold"
        )
        parallel_execution: bool = Field(
            default=True, description="Enable parallel test execution"
        )
        max_workers: int = Field(default=4, description="Maximum test workers")
        timeout_seconds: int = Field(default=300, description="Test timeout in seconds")

    class TestResult(FlextModels.Entity):
        """Test execution result model."""

        test_id: str = Field(description="Unique test identifier")
        test_suite: str = Field(description="Test suite name")
        total_tests: int = Field(description="Total number of tests")
        passed_tests: int = Field(description="Number of passed tests")
        failed_tests: int = Field(description="Number of failed tests")
        skipped_tests: int = Field(description="Number of skipped tests")
        duration_seconds: float = Field(description="Test duration in seconds")
        coverage_percentage: float = Field(
            default=0.0, description="Test coverage percentage"
        )
        test_report: str = Field(default="", description="Test report output")
        timestamp: datetime = Field(
            default_factory=datetime.now, description="Test timestamp"
        )

    # Documentation Models
    class DocConfig(FlextModels.Configuration):
        """Documentation generation configuration model."""

        source_directories: list[str] = Field(
            default_factory=list, description="Source directories"
        )
        output_directory: str = Field(
            default="docs", description="Documentation output directory"
        )
        format: str = Field(default="html", description="Documentation format")
        include_private: bool = Field(
            default=False, description="Include private members"
        )
        include_examples: bool = Field(
            default=True, description="Include code examples"
        )
        theme: str = Field(default="default", description="Documentation theme")
        auto_generate: bool = Field(
            default=True, description="Auto-generate documentation"
        )

    class DocResult(FlextModels.Entity):
        """Documentation generation result model."""

        doc_id: str = Field(description="Unique documentation identifier")
        success: bool = Field(description="Documentation generation success")
        pages_generated: int = Field(description="Number of pages generated")
        output_size_mb: float = Field(description="Output size in megabytes")
        duration_seconds: float = Field(description="Generation duration in seconds")
        warnings_count: int = Field(default=0, description="Number of warnings")
        output_path: str = Field(description="Documentation output path")
        timestamp: datetime = Field(
            default_factory=datetime.now, description="Generation timestamp"
        )

    # Environment Management Models
    class EnvironmentConfig(FlextModels.Configuration):
        """Development environment configuration model."""

        python_version: str = Field(default="3.11", description="Python version")
        virtual_env_path: str = Field(
            default=".venv", description="Virtual environment path"
        )
        requirements_file: str = Field(
            default="requirements.txt", description="Requirements file"
        )
        dev_requirements_file: str = Field(
            default="requirements-dev.txt", description="Dev requirements file"
        )
        enable_pre_commit: bool = Field(
            default=True, description="Enable pre-commit hooks"
        )
        enable_git_hooks: bool = Field(default=True, description="Enable git hooks")
        editor_config: dict[str, str] = Field(
            default_factory=dict, description="Editor configuration"
        )

    class EnvironmentStatus(FlextModels.Entity):
        """Development environment status model."""

        env_id: str = Field(description="Unique environment identifier")
        is_active: bool = Field(description="Environment active status")
        python_version: str = Field(description="Active Python version")
        packages_count: int = Field(description="Number of installed packages")
        virtual_env_size_mb: float = Field(description="Virtual environment size in MB")
        last_updated: datetime = Field(description="Last update timestamp")
        health_status: str = Field(
            default="healthy", description="Environment health status"
        )
        issues: list[str] = Field(
            default_factory=list, description="Environment issues"
        )

    # Tool Management Models
    class ToolConfig(FlextModels.Configuration):
        """Development tool configuration model."""

        tool_name: str = Field(description="Tool name")
        tool_version: str = Field(description="Tool version")
        enabled: bool = Field(default=True, description="Tool enabled status")
        configuration: FlextToolsTypes.Core.ToolConfigDict = Field(
            default_factory=dict, description="Tool configuration"
        )
        dependencies: list[str] = Field(
            default_factory=list, description="Tool dependencies"
        )
        execution_timeout: int = Field(
            default=300, description="Tool execution timeout"
        )
        auto_update: bool = Field(default=False, description="Auto-update tool")

    class ToolResult(FlextModels.Entity):
        """Development tool execution result model."""

        tool_name: str = Field(description="Tool name")
        execution_id: str = Field(description="Unique execution identifier")
        success: bool = Field(description="Tool execution success")
        exit_code: int = Field(description="Tool exit code")
        stdout: str = Field(default="", description="Standard output")
        stderr: str = Field(default="", description="Standard error")
        duration_seconds: float = Field(description="Execution duration in seconds")
        timestamp: datetime = Field(
            default_factory=datetime.now, description="Execution timestamp"
        )

    # Legacy type aliases for backward compatibility (now using FlextToolsTypes)
    BuildConfiguration = FlextToolsTypes.Core.BuildConfigDict
    TestConfiguration = FlextToolsTypes.Core.TestConfigDict
