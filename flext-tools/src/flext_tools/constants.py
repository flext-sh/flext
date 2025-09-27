"""FLEXT Tools Constants - Development tools and utilities constants.

This module defines all constants for FLEXT development tools operations,
extending FlextConstants for consistency across the ecosystem.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import ClassVar, Final

from flext_core import FlextConstants, FlextTypes


class FlextToolsConstants(FlextConstants):
    """Development tools constants extending FlextConstants for ecosystem consistency."""

    class Build:
        """Build and deployment constants."""

        # Build types
        DEFAULT_BUILD_TYPE: Final[str] = "release"
        SUPPORTED_BUILD_TYPES: ClassVar[FlextTypes.Core.StringList] = [
            "debug",
            "release",
            "profile",
        ]

        # Target platforms
        DEFAULT_TARGET_PLATFORM: Final[str] = "linux"
        SUPPORTED_PLATFORMS: ClassVar[FlextTypes.Core.StringList] = [
            "linux",
            "darwin",
            "windows",
        ]

        # Optimization levels
        DEFAULT_OPTIMIZATION_LEVEL: Final[str] = "O2"
        SUPPORTED_OPTIMIZATION_LEVELS: ClassVar[FlextTypes.Core.StringList] = [
            "O0",
            "O1",
            "O2",
            "O3",
            "Os",
        ]

        # Build configuration
        DEFAULT_PARALLEL_JOBS: Final[int] = (
            4  # Reasonable default for build parallelism
        )
        MAX_PARALLEL_JOBS: Final[int] = 16  # Maximum parallel jobs for build
        DEFAULT_BUILD_DIRECTORY: Final[str] = "build"
        DEFAULT_ENABLE_TESTS: Final[bool] = True
        DEFAULT_ENABLE_DOCUMENTATION: Final[bool] = True

    class Testing:
        """Testing and validation constants."""

        # Coverage thresholds
        MIN_COVERAGE_THRESHOLD: Final[float] = 75.0
        RECOMMENDED_COVERAGE_THRESHOLD: Final[float] = 85.0
        EXCELLENT_COVERAGE_THRESHOLD: Final[float] = 95.0

        # Test timeouts
        DEFAULT_TEST_TIMEOUT: Final[int] = FlextConstants.Network.DEFAULT_TIMEOUT * 2
        LONG_TEST_TIMEOUT: Final[int] = FlextConstants.Network.DEFAULT_TIMEOUT * 10

        # Test batch sizes
        DEFAULT_TEST_BATCH_SIZE: Final[int] = (
            FlextConstants.Performance.BatchProcessing.DEFAULT_SIZE
        )
        MAX_TEST_BATCH_SIZE: Final[int] = (
            FlextConstants.Performance.BatchProcessing.MAX_ITEMS
        )

    class CodeAnalysis:
        """Code analysis and quality constants."""

        # Quality thresholds
        MAX_COMPLEXITY_THRESHOLD: Final[int] = 10
        MAX_LINE_LENGTH: Final[int] = 79  # PEP8 strict
        MIN_FUNCTION_NAME_LENGTH: Final[int] = 3
        MAX_FUNCTION_NAME_LENGTH: Final[int] = 50

        # Linting configuration
        DEFAULT_LINT_SEVERITY: Final[str] = "error"
        SUPPORTED_LINT_SEVERITIES: ClassVar[FlextTypes.Core.StringList] = [
            "error",
            "warning",
            "info",
        ]

    class Documentation:
        """Documentation generation constants."""

        # Documentation formats
        DEFAULT_DOC_FORMAT: Final[str] = "html"
        SUPPORTED_DOC_FORMATS: ClassVar[FlextTypes.Core.StringList] = [
            "html",
            "pdf",
            "markdown",
            "json",
        ]

        # Documentation directories
        DEFAULT_DOCS_SOURCE_DIR: Final[str] = "docs"
        DEFAULT_DOCS_OUTPUT_DIR: Final[str] = "docs/_build"
        DEFAULT_API_DOCS_DIR: Final[str] = "docs/api"

    class Environment:
        """Development environment constants."""

        # Python version requirements
        MIN_PYTHON_VERSION: Final[str] = "3.13"
        RECOMMENDED_PYTHON_VERSION: Final[str] = "3.13"

        # Virtual environment
        DEFAULT_VENV_NAME: Final[str] = ".venv"
        DEFAULT_REQUIREMENTS_FILE: Final[str] = "requirements.txt"
        DEFAULT_DEV_REQUIREMENTS_FILE: Final[str] = "requirements-dev.txt"

        # Environment variables
        DEVELOPMENT_ENV_VAR: Final[str] = "FLEXT_DEVELOPMENT"
        DEBUG_ENV_VAR: Final[str] = "FLEXT_DEBUG"
        LOG_LEVEL_ENV_VAR: Final[str] = "FLEXT_LOG_LEVEL"

    class Monitoring:
        """Development monitoring and metrics constants."""

        # Performance monitoring
        DEFAULT_MEMORY_LIMIT_MB: Final[int] = 512
        DEFAULT_CPU_LIMIT_PERCENT: Final[float] = 80.0

        # Metrics collection
        DEFAULT_METRICS_INTERVAL: Final[int] = 60  # seconds
        MAX_METRICS_HISTORY: Final[int] = 1000

        # Alerts
        HIGH_CPU_THRESHOLD: Final[float] = 90.0
        HIGH_MEMORY_THRESHOLD: Final[float] = 90.0
        DISK_SPACE_WARNING_THRESHOLD: Final[float] = 85.0

    class Backup:
        """Backup and versioning constants."""

        # Backup configuration
        DEFAULT_BACKUP_RETENTION_DAYS: Final[int] = 30
        MAX_BACKUP_SIZE_MB: Final[int] = 1024
        DEFAULT_BACKUP_COMPRESSION: Final[str] = "gzip"

        # Backup formats
        SUPPORTED_BACKUP_FORMATS: ClassVar[FlextTypes.Core.StringList] = [
            "tar",
            "zip",
            "gzip",
        ]

        # Version control
        DEFAULT_GIT_BRANCH: Final[str] = "main"
        DEFAULT_TAG_PREFIX: Final[str] = "v"


__all__: FlextTypes.Core.StringList = [
    "FlextToolsConstants",
]
