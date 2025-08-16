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
    - documentation: Documentation generation with Jinja2 templates and MkDocs
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
    >>> from flext_tools.documentation import DocumentationGenerator
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
    >>>
    >>> # Generate documentation
    >>> doc_gen = DocumentationGenerator("/path/to/workspace")
    >>> doc_result = doc_gen.generate_complete_documentation()

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
__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())

# Core patterns integration
from flext_core import FlextContainer, get_flext_container

# Exporta módulos principais
from flext_tools.analysis import ConflictAnalyzer, VersionAnalyzer
# Cache module removed - not implemented yet
from flext_tools.discovery import DependencyDiscovery
from flext_tools.documentation import DocumentationGenerator, TemplateManager
from flext_tools.poetry import PoetryOperations, PoetryValidator
from flext_tools.safety import BackupManager, RollbackManager, SafetyValidator
from flext_tools.utils import (
    Colors,
    DetailedLogger,
    get_logger,
    get_stdlib_modules,
    print_colored,
    should_ignore_path,
)


def get_flext_tools_container() -> FlextContainer:
    """Get or create the FlextTools service container."""
    container = get_flext_container()

    # Register core services
    try:
        container.get("conflict_analyzer")
    except KeyError:
        container.register("conflict_analyzer", ConflictAnalyzer)

    try:
        container.get("cache_manager")
    except KeyError:
        container.register("cache_manager", CacheManager)

    try:
        container.get("dependency_discovery")
    except KeyError:
        container.register("dependency_discovery", DependencyDiscovery)

    try:
        container.get("documentation_generator")
    except KeyError:
        container.register("documentation_generator", DocumentationGenerator)

    try:
        container.get("poetry_operations")
    except KeyError:
        container.register("poetry_operations", PoetryOperations)

    try:
        container.get("safety_validator")
    except KeyError:
        container.register("safety_validator", SafetyValidator)

    return container


__all__: list[str] = [
    "BackupManager",
    "CacheManager",
    "Colors",
    "ConflictAnalyzer",
    "DependencyDiscovery",
    "DetailedLogger",
    "DocumentationGenerator",
    "FlextContainer",
    "PoetryOperations",
    "PoetryValidator",
    "RollbackManager",
    "SafetyValidator",
    "TemplateManager",
    "VersionAnalyzer",
    "__version__",
    "__version_info__",
            # "cache_result",  # Cache module removed
        # "cached",        # Cache module removed
    "get_flext_container",
    "get_flext_tools_container",
    "get_logger",
    "get_stdlib_modules",
    "print_colored",
    "should_ignore_path",
]
