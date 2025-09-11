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

# Build __all__ list from all imported modules
import sys
from types import ModuleType

from flext_core.typings import FlextTypes

# Security scanning
from .antipattern_scanner import *

# Safety and backup tools
from .backup import *

# CLI patterns and base classes
from .base_cli import *

# Main CLI and workspace tools
from .cli import *

# Utility functions
from .colors import *

# Configuration management
from .config_manager import *

# Analysis tools
from .conflicts import *
from .dev import *

# Discovery utilities
from .discovery_base import *
from .discovery_config import *
from .discovery_python import *
from .discovery_transitive import *

# Documentation generators - exclude conflicting main function
from .documentation_generator import DocumentationGenerator
from .documentation_templates import *
from .duplicates import *

# Services and application layer
from .handlers import *

# Monitoring and health checks
from .health_check import *
from .lint_fixer import *
from .lock_consistency import *

# Infrastructure management
from .monitoring_manager import *
from .mypy_checker import *
from .observability import *

# Testing utilities
from .oracle_e2e import *
from .paths import *
from .pipeline import *

# Poetry operations and validation
from .poetry_operations import *
from .poetry_validator import *

# Quality management
from .quality_bridge import *
from .quality_gateway import *
from .rollback import *
from .safety_validator import *

# Core utilities and script base
from .script_base import *
from .ssl_manager import *
from .stdlib import *
from .venv_consistency import *
from .version import *
from .workspace import *

# Workspace CLI
from .workspace_cli import *

__all__: FlextTypes.Core.StringList = []

# Collect exports from all imported modules
name = None
obj = None
for name, obj in sys.modules.items():
    if (
        name.startswith("flext_")
        and isinstance(obj, ModuleType)
        and hasattr(obj, "__all__")
        and obj.__all__
    ):
        __all__ += obj.__all__

# Remove duplicates and sort - FLEXT Pattern
_all_exports = sorted(set(__all__))
__all__ = list(_all_exports)

# Clean up temporary variables
del sys, ModuleType
if name is not None:
    del name
if obj is not None:
    del obj
