"""FLEXT Tools Configuration - Development tools configuration using flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Self

from pydantic import Field, computed_field, field_validator, model_validator
from pydantic_settings import SettingsConfigDict

from flext_core import FlextConfig, FlextResult
from flext_tools.constants import FlextToolsConstants


class FlextToolsConfig(FlextConfig):
    """Single Pydantic 2 Settings class for flext-tools extending FlextConfig.

    Follows standardized pattern:
    - Extends FlextConfig from flext-core
    - No nested classes within Config
    - All defaults from FlextToolsConstants
    - Uses enhanced singleton pattern with inverse dependency injection
    - Uses Pydantic 2.11+ features (field_validator, model_validator)
    """

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_TOOLS_",
        case_sensitive=False,
        extra="allow",
        # Inherit enhanced Pydantic 2.11+ features from FlextConfig
        validate_assignment=True,
        str_strip_whitespace=True,
        json_schema_extra={
            "title": "FLEXT Tools Configuration",
            "description": "Development tools configuration extending FlextConfig",
        },
    )

    # Build Configuration using FlextToolsConstants for defaults
    build_type: str = Field(
        default=FlextToolsConstants.Build.DEFAULT_BUILD_TYPE,
        description="Build type (debug, release, profile)",
    )

    target_platform: str = Field(
        default=FlextToolsConstants.Build.DEFAULT_TARGET_PLATFORM,
        description="Target platform for builds",
    )

    optimization_level: str = Field(
        default=FlextToolsConstants.Build.DEFAULT_OPTIMIZATION_LEVEL,
        description="Build optimization level",
    )

    parallel_jobs: int = Field(
        default=FlextToolsConstants.Build.DEFAULT_PARALLEL_JOBS,
        ge=1,
        le=FlextToolsConstants.Build.MAX_PARALLEL_JOBS,
        description="Number of parallel build jobs",
    )

    build_directory: str = Field(
        default=FlextToolsConstants.Build.DEFAULT_BUILD_DIRECTORY,
        description="Build output directory",
    )

    enable_tests: bool = Field(
        default=FlextToolsConstants.Build.DEFAULT_ENABLE_TESTS,
        description="Enable test execution during build",
    )

    enable_documentation: bool = Field(
        default=FlextToolsConstants.Build.DEFAULT_ENABLE_DOCUMENTATION,
        description="Enable documentation generation",
    )

    # Testing Configuration using FlextToolsConstants for defaults
    coverage_threshold: float = Field(
        default=FlextToolsConstants.Testing.RECOMMENDED_COVERAGE_THRESHOLD,
        ge=FlextToolsConstants.Testing.MIN_COVERAGE_THRESHOLD,
        le=100.0,
        description="Test coverage threshold percentage",
    )

    test_timeout: int = Field(
        default=FlextToolsConstants.Testing.DEFAULT_TEST_TIMEOUT,
        gt=0,
        le=FlextToolsConstants.Testing.LONG_TEST_TIMEOUT,
        description="Test execution timeout in seconds",
    )

    test_batch_size: int = Field(
        default=FlextToolsConstants.Testing.DEFAULT_TEST_BATCH_SIZE,
        gt=0,
        le=FlextToolsConstants.Testing.MAX_TEST_BATCH_SIZE,
        description="Test batch size for parallel execution",
    )

    # Code Analysis Configuration using FlextToolsConstants for defaults
    max_complexity: int = Field(
        default=FlextToolsConstants.CodeAnalysis.MAX_COMPLEXITY_THRESHOLD,
        ge=1,
        le=50,
        description="Maximum cyclomatic complexity threshold",
    )

    max_line_length: int = Field(
        default=FlextToolsConstants.CodeAnalysis.MAX_LINE_LENGTH,
        ge=50,
        le=200,
        description="Maximum line length for code",
    )

    lint_severity: str = Field(
        default=FlextToolsConstants.CodeAnalysis.DEFAULT_LINT_SEVERITY,
        description="Linting severity level",
    )

    # Documentation Configuration using FlextToolsConstants for defaults
    docs_format: str = Field(
        default=FlextToolsConstants.Documentation.DEFAULT_DOC_FORMAT,
        description="Documentation output format",
    )

    docs_source_dir: str = Field(
        default=FlextToolsConstants.Documentation.DEFAULT_DOCS_SOURCE_DIR,
        description="Documentation source directory",
    )

    docs_output_dir: str = Field(
        default=FlextToolsConstants.Documentation.DEFAULT_DOCS_OUTPUT_DIR,
        description="Documentation output directory",
    )

    # Environment Configuration using FlextToolsConstants for defaults
    python_version: str = Field(
        default=FlextToolsConstants.Environment.RECOMMENDED_PYTHON_VERSION,
        description="Required Python version",
    )

    venv_name: str = Field(
        default=FlextToolsConstants.Environment.DEFAULT_VENV_NAME,
        description="Virtual environment name",
    )

    development_mode: bool = Field(
        default=False,
        description="Enable development mode features",
    )

    debug_enabled: bool = Field(
        default=False,
        description="Enable debug mode",
    )

    # Monitoring Configuration using FlextToolsConstants for defaults
    memory_limit_mb: int = Field(
        default=FlextToolsConstants.Monitoring.DEFAULT_MEMORY_LIMIT_MB,
        gt=0,
        description="Memory limit in megabytes",
    )

    cpu_limit_percent: float = Field(
        default=FlextToolsConstants.Monitoring.DEFAULT_CPU_LIMIT_PERCENT,
        ge=1.0,
        le=100.0,
        description="CPU usage limit percentage",
    )

    metrics_interval: int = Field(
        default=FlextToolsConstants.Monitoring.DEFAULT_METRICS_INTERVAL,
        gt=0,
        description="Metrics collection interval in seconds",
    )

    # Backup Configuration using FlextToolsConstants for defaults
    backup_retention_days: int = Field(
        default=FlextToolsConstants.Backup.DEFAULT_BACKUP_RETENTION_DAYS,
        gt=0,
        description="Backup retention period in days",
    )

    backup_compression: str = Field(
        default=FlextToolsConstants.Backup.DEFAULT_BACKUP_COMPRESSION,
        description="Backup compression format",
    )

    # Pydantic 2.11+ field validators
    @field_validator("build_type")
    @classmethod
    def validate_build_type(cls, v: str) -> str:
        """Validate build type is supported."""
        if v not in FlextToolsConstants.Build.SUPPORTED_BUILD_TYPES:
            supported = ", ".join(FlextToolsConstants.Build.SUPPORTED_BUILD_TYPES)
            msg = f"Invalid build type: {v}. Supported types: {supported}"
            raise ValueError(msg)
        return v

    @field_validator("target_platform")
    @classmethod
    def validate_target_platform(cls, v: str) -> str:
        """Validate target platform is supported."""
        if v not in FlextToolsConstants.Build.SUPPORTED_PLATFORMS:
            supported = ", ".join(FlextToolsConstants.Build.SUPPORTED_PLATFORMS)
            msg = f"Invalid target platform: {v}. Supported platforms: {supported}"
            raise ValueError(msg)
        return v

    @field_validator("optimization_level")
    @classmethod
    def validate_optimization_level(cls, v: str) -> str:
        """Validate optimization level is supported."""
        if v not in FlextToolsConstants.Build.SUPPORTED_OPTIMIZATION_LEVELS:
            supported = ", ".join(
                FlextToolsConstants.Build.SUPPORTED_OPTIMIZATION_LEVELS
            )
            msg = f"Invalid optimization level: {v}. Supported levels: {supported}"
            raise ValueError(msg)
        return v

    @field_validator("lint_severity")
    @classmethod
    def validate_lint_severity(cls, v: str) -> str:
        """Validate lint severity is supported."""
        if v not in FlextToolsConstants.CodeAnalysis.SUPPORTED_LINT_SEVERITIES:
            supported = ", ".join(
                FlextToolsConstants.CodeAnalysis.SUPPORTED_LINT_SEVERITIES
            )
            msg = f"Invalid lint severity: {v}. Supported severities: {supported}"
            raise ValueError(msg)
        return v

    @field_validator("docs_format")
    @classmethod
    def validate_docs_format(cls, v: str) -> str:
        """Validate documentation format is supported."""
        if v not in FlextToolsConstants.Documentation.SUPPORTED_DOC_FORMATS:
            supported = ", ".join(
                FlextToolsConstants.Documentation.SUPPORTED_DOC_FORMATS
            )
            msg = f"Invalid docs format: {v}. Supported formats: {supported}"
            raise ValueError(msg)
        return v

    @field_validator("backup_compression")
    @classmethod
    def validate_backup_compression(cls, v: str) -> str:
        """Validate backup compression format is supported."""
        if v not in FlextToolsConstants.Backup.SUPPORTED_BACKUP_FORMATS:
            supported = ", ".join(FlextToolsConstants.Backup.SUPPORTED_BACKUP_FORMATS)
            msg = f"Invalid backup compression: {v}. Supported formats: {supported}"
            raise ValueError(msg)
        return v

    @model_validator(mode="after")
    def validate_tools_configuration_consistency(self) -> Self:
        """Validate development tools configuration consistency."""
        # Validate coverage threshold for development mode
        if (
            self.development_mode
            and self.coverage_threshold
            < FlextToolsConstants.Testing.MIN_COVERAGE_THRESHOLD
        ):
            msg = f"Development mode requires coverage >= {FlextToolsConstants.Testing.MIN_COVERAGE_THRESHOLD}%"
            raise ValueError(msg)

        # Validate debug mode consistency
        if self.debug_enabled and self.parallel_jobs > 2:
            msg = "Debug mode should use <= 2 parallel jobs for better debugging"
            raise ValueError(msg)

        # Validate monitoring thresholds
        if self.cpu_limit_percent > FlextToolsConstants.Monitoring.HIGH_CPU_THRESHOLD:
            msg = f"CPU limit should not exceed {FlextToolsConstants.Monitoring.HIGH_CPU_THRESHOLD}%"
            raise ValueError(msg)

        # Validate memory limits for build configuration
        if self.parallel_jobs > 4 and self.memory_limit_mb < 1024:
            msg = "High parallel jobs (>4) require memory limit >= 1024MB"
            raise ValueError(msg)

        return self

    @computed_field
    @property
    def is_production_build(self) -> bool:
        """Check if this is a production build configuration."""
        return (
            self.build_type == "release"
            and self.optimization_level in {"O2", "O3"}
            and not self.debug_enabled
        )

    @computed_field
    @property
    def is_development_build(self) -> bool:
        """Check if this is a development build configuration."""
        return self.build_type == "debug" or self.development_mode or self.debug_enabled

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate development tools business rules."""
        try:
            # Validate build configuration
            if self.enable_tests and self.coverage_threshold <= 0:
                return FlextResult[None].fail(
                    "Test coverage threshold must be positive when tests are enabled"
                )

            # Validate monitoring configuration
            if self.memory_limit_mb < 128:
                return FlextResult[None].fail("Memory limit must be at least 128MB")

            # Validate backup configuration
            if self.backup_retention_days > 365:
                return FlextResult[None].fail(
                    "Backup retention should not exceed 365 days"
                )

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Business rules validation failed: {e}")

    def get_build_config(self) -> dict[str, object]:
        """Get build configuration context."""
        return {
            "build_type": self.build_type,
            "target_platform": self.target_platform,
            "optimization_level": self.optimization_level,
            "parallel_jobs": self.parallel_jobs,
            "build_directory": self.build_directory,
            "enable_tests": self.enable_tests,
            "enable_documentation": self.enable_documentation,
            "is_production": self.is_production_build,
            "is_development": self.is_development_build,
        }

    def get_testing_config(self) -> dict[str, object]:
        """Get testing configuration context."""
        return {
            "coverage_threshold": self.coverage_threshold,
            "test_timeout": self.test_timeout,
            "test_batch_size": self.test_batch_size,
            "enable_tests": self.enable_tests,
        }

    def get_analysis_config(self) -> dict[str, object]:
        """Get code analysis configuration context."""
        return {
            "max_complexity": self.max_complexity,
            "max_line_length": self.max_line_length,
            "lint_severity": self.lint_severity,
        }

    def get_docs_config(self) -> dict[str, object]:
        """Get documentation configuration context."""
        return {
            "docs_format": self.docs_format,
            "docs_source_dir": self.docs_source_dir,
            "docs_output_dir": self.docs_output_dir,
            "enable_documentation": self.enable_documentation,
        }

    def get_monitoring_config(self) -> dict[str, object]:
        """Get monitoring configuration context."""
        return {
            "memory_limit_mb": self.memory_limit_mb,
            "cpu_limit_percent": self.cpu_limit_percent,
            "metrics_interval": self.metrics_interval,
        }

    @classmethod
    def create_for_environment(
        cls, environment: str, **overrides: object
    ) -> FlextToolsConfig:
        """Create configuration for specific environment using enhanced singleton pattern."""
        return cls.get_or_create_shared_instance(
            project_name="flext-tools", environment=environment, **overrides
        )

    @classmethod
    def create_default(cls) -> FlextToolsConfig:
        """Create default configuration instance using enhanced singleton pattern."""
        return cls.get_or_create_shared_instance(project_name="flext-tools")

    @classmethod
    def create_for_development(cls) -> FlextToolsConfig:
        """Create configuration optimized for development using enhanced singleton pattern."""
        return cls.get_or_create_shared_instance(
            project_name="flext-tools",
            build_type="debug",
            development_mode=True,
            debug_enabled=True,
            parallel_jobs=2,
            coverage_threshold=FlextToolsConstants.Testing.MIN_COVERAGE_THRESHOLD,
        )

    @classmethod
    def create_for_production(cls) -> FlextToolsConfig:
        """Create configuration optimized for production using enhanced singleton pattern."""
        return cls.get_or_create_shared_instance(
            project_name="flext-tools",
            build_type="release",
            optimization_level="O3",
            development_mode=False,
            debug_enabled=False,
            parallel_jobs=FlextToolsConstants.Build.MAX_PARALLEL_JOBS,
            coverage_threshold=FlextToolsConstants.Testing.EXCELLENT_COVERAGE_THRESHOLD,
        )

    @classmethod
    def get_global_instance(cls) -> FlextToolsConfig:
        """Get the global singleton instance using enhanced FlextConfig pattern."""
        return cls.get_or_create_shared_instance(project_name="flext-tools")

    @classmethod
    def reset_global_instance(cls) -> None:
        """Reset the global FlextToolsConfig instance (mainly for testing)."""
        # Use the enhanced FlextConfig reset mechanism
        cls.reset_shared_instance()


__all__ = [
    "FlextToolsConfig",
]
