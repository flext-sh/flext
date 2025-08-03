"""FLEXT Tools - Enterprise Development and Operations Toolkit.

Comprehensive modular toolkit for FLEXT ecosystem development operations,
providing enterprise-grade dependency management, code analysis, quality
validation, and operational tooling across all 32 FLEXT projects with
consistent patterns and architectural excellence.

This toolkit implements Clean Architecture and Domain-Driven Design patterns
to provide maintainable, testable, and extensible development operations
infrastructure. Each module focuses on specific operational concerns while
maintaining clear boundaries and consistent integration patterns.

Core Modules:
    - analysis: Dependency conflict detection and version management
    - cache: High-performance caching infrastructure with decorators
    - config: Configuration management and validation
    - core: Base framework patterns and script infrastructure
    - discovery: Project and dependency discovery with transitive analysis
    - infrastructure: Monitoring, SSL management, and system operations
    - monitoring: Health checks and system monitoring
    - poetry: Poetry operations and dependency validation
    - quality: Code quality gates and automated enforcement
    - safety: Backup, rollback, and safety validation systems
    - security: Secret management and security tooling
    - testing: Testing infrastructure and E2E validation
    - utils: Shared utilities for logging, colors, paths, and stdlib

Architecture:
    Implements Clean Architecture with clear separation between:
    - Domain Layer: Core business logic and entities
    - Application Layer: Use cases and orchestration services
    - Infrastructure Layer: External integrations and technical concerns
    - Interface Layer: CLI interfaces and external APIs

Integration:
    - Built on flext-core foundation patterns (FlextResult, FlextContainer)
    - Integrates with flext-observability for monitoring and metrics
    - Coordinates with WorkspaceManager for project operations
    - Provides CLI integration through development commands
    - Supports quality gate enforcement across ecosystem

Example:
    Basic toolkit usage:

    >>> from flext_tools import ConflictAnalyzer, CacheManager, get_logger
    >>> from flext_tools.quality import QualityGateway
    >>>
    >>> # Analyze dependency conflicts
    >>> analyzer = ConflictAnalyzer("/path/to/workspace")
    >>> conflicts = analyzer.analyze_all_projects()
    >>>
    >>> # Use caching for performance
    >>> cache = CacheManager()
    >>> @cache.cached(ttl=3600)
    >>> def expensive_operation():
    ...     return "cached result"
    >>>
    >>> # Enforce quality gates
    >>> gateway = QualityGateway()
    >>> result = gateway.validate_all_projects()

Quality Standards:
    - 100% type annotation coverage across all modules
    - Comprehensive docstring coverage with examples
    - Enterprise-grade error handling with FlextResult patterns
    - Security-focused implementation with proper validation
    - Performance optimization with intelligent caching
    - Comprehensive testing with unit, integration, and E2E coverage

Author: FLEXT Development Team
Version: 2.0.0
License: MIT

"""

__version__ = "2.0.0"

# Exporta módulos principais
from flext_tools.analysis import ConflictAnalyzer, VersionAnalyzer
from flext_tools.cache import CacheManager, cache_result, cached
from flext_tools.discovery import DependencyDiscovery
from flext_tools.poetry import PoetryOperations, PoetryValidator
from flext_tools.safety import BackupManager, RollbackManager, SafetyValidator
from flext_tools.utils import (
    Colors,
    DetailedLogger,
    LogLevel,
    get_logger,
    get_stdlib_modules,
    print_colored,
    should_ignore_path,
)

__all__ = [
    "BackupManager",
    "CacheManager",
    "Colors",
    "ConflictAnalyzer",
    "DependencyDiscovery",
    "DetailedLogger",
    "LogLevel",
    "PoetryOperations",
    "PoetryValidator",
    "RollbackManager",
    "SafetyValidator",
    "VersionAnalyzer",
    "cache_result",
    "cached",
    "get_logger",
    "get_stdlib_modules",
    "print_colored",
    "should_ignore_path",
]
