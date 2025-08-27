"""FLEXT Workspace - Main Package Initialization.

Provides unified access to all FLEXT workspace utilities and tools following
flattened directory structure and proper PEP8 module naming conventions.

This module serves as the main entry point for the FLEXT workspace toolkit,
exposing utilities for code analysis, quality management, project tooling,
and development infrastructure in a clean, organized interface.

Architecture:
    Following FLEXT ecosystem patterns with flext-core integration,
    this module aggregates functionality from specialized modules:
    - Analysis tools (conflicts, duplicates, version management)
    - Configuration management and discovery utilities
    - Code quality and safety tooling
    - Infrastructure and monitoring capabilities
    - Poetry and dependency management
    - Security scanning and testing utilities

Example:
    Basic usage of workspace utilities:

    >>> from src.duplicates import CodeDuplicateAnalyzer
    >>> from src.quality_gateway import QualityGateway
    >>> from src.colors import Colors, print_colored
    >>>
    >>> # Analyze code duplications
    >>> analyzer = CodeDuplicateAnalyzer()
    >>> result = analyzer.analyze_duplicates()
    >>>
    >>> # Run quality gates
    >>> gateway = QualityGateway()
    >>> quality_result = gateway.validate_all()
    >>>
    >>> # Colored output
    >>> print_colored("Quality check complete!", Colors.GREEN)

Integration:
    - Built on flext-core patterns for consistent error handling
    - Integrates with FLEXT ecosystem quality standards
    - Follows railway-oriented programming with FlextResult
    - Supports enterprise-grade configuration and monitoring

"""

from __future__ import annotations

# Main CLI and workspace tools
from .cli import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403
from .dev import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403
from .workspace import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403

# CLI patterns and base classes
from .base_cli import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403

# Services and application layer
from .handlers import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403
from .pipeline import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403

# Workspace CLI
from .workspace_cli import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403

# Analysis tools
from .conflicts import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403
from .duplicates import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403
from .lock_consistency import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403
from .version import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403

# Configuration management
from .config_manager import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403

# Core utilities and script base
from .script_base import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403

# Discovery utilities
from .discovery_base import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403
from .discovery_config import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403
from .discovery_python import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403
from .discovery_transitive import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403

# Documentation generators
from .documentation_generator import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403
from .documentation_templates import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403

# Infrastructure management
from .monitoring_manager import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403
from .ssl_manager import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403

# Monitoring and health checks
from .health_check import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403

# Poetry operations and validation
from .poetry_operations import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403
from .poetry_validator import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403

# Quality management
from .quality_bridge import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403
from .quality_gateway import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403
from .lint_fixer import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403
from .mypy_checker import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403

# Safety and backup tools
from .backup import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403
from .rollback import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403
from .safety_validator import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403
from .venv_consistency import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403

# Security scanning
from .antipattern_scanner import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403

# Testing utilities
from .oracle_e2e import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403

# Utility functions
from .colors import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403
from .observability import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403
from .paths import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403
from .stdlib import *  # type: ignore[misc,unused-ignore,reportWildcardImport,assignment] # noqa: F403

# Build __all__ list from all imported modules
import sys
from types import ModuleType

__all__: list[str] = []

# Collect exports from all imported modules
for name, obj in sys.modules.items():
    if (
        name.startswith("flext_")
        and isinstance(obj, ModuleType)
        and hasattr(obj, "__all__")
        and obj.__all__
    ):
        __all__ += obj.__all__

# Remove duplicates and sort - FLEXT Pattern
__all__ = list(sorted(set(__all__)))  # noqa: C413  # __all__ must be list

# Clean up temporary variables
del sys, ModuleType, name, obj
