"""FLEXT Tools - Consolidated workspace tools library.

This module provides a comprehensive suite of development and operational tools for the FLEXT
ecosystem. It consolidates 85+ individual scripts into 6 unified tool modules plus utilities,
providing a single entry point for all workspace operations.

The module includes tools for:
    - Quality assurance and code analysis
    - Architecture validation and optimization
    - Dependency management and analysis
    - Git operations and repository management
    - Performance optimization and monitoring
    - Validation and testing utilities

All tools follow the unified FLEXT patterns with proper error handling, logging, and
type safety throughout.

Attributes:
    FlextTools (FlextToolsAPI): Primary API for accessing all tool functionality.
    FlextToolsAPI (class): Main API class providing unified tool interface.

Example:
    >>> from flext_tools import FlextTools, FlextQualityTools
    >>>
    >>> # Use primary API
    >>> tools = FlextTools()
    >>> result = tools.run_quality_checks()
    >>>
    >>> # Use specific tool modules
    >>> quality_tools = FlextQualityTools()
    >>> quality_tools.run_linting()

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

#  Unified API (PRIMARY IMPORT)
from flext_tools.api import FlextTools, FlextToolsAPI

# Tool modules (6 unified modules consolidating 85+ scripts)
from flext_tools.architecture_tools import FlextArchitectureTools

# Legacy aliases for backward compatibility
from flext_tools.config import ConfigurationManager
from flext_tools.conflicts import ConflictAnalyzer

# Namespace classes
from flext_tools.constants import FlextToolsConstants
from flext_tools.dependency_tools import DependencyDiscovery, FlextDependencyTools
from flext_tools.exceptions import FlextToolsExceptions
from flext_tools.git_tools import FlextGitTools
from flext_tools.models import FlextToolsModels
from flext_tools.observability import FlextObservabilityService
from flext_tools.optimizer_tools import FlextOptimizerTools
from flext_tools.poetry_operations import PoetryOperations
from flext_tools.poetry_validator import PoetryValidator
from flext_tools.protocols import FlextToolsProtocols
from flext_tools.quality_tools import FlextQualityTools
from flext_tools.script_base import (
    FlextScriptService,
    FlextScriptService as FlextScript,
)
from flext_tools.typings import FlextToolsTypes

# Utilities (consolidated from colors, paths, stdlib)
from flext_tools.utilities import (
    Colors,
    FlextToolsUtilities,
    colorize,
    get_project_root,
    get_stdlib_modules,
    is_stdlib_module,
    normalize_path,
    print_colored,
    should_ignore_path,
)
from flext_tools.validation_tools import FlextValidationTools

ScriptMetadata = FlextScriptService.ScriptMetadata

__all__ = [
    "Colors",
    "ConfigurationManager",  # Legacy
    "ConflictAnalyzer",  # Legacy
    "DependencyDiscovery",  # Legacy
    "FlextArchitectureTools",
    "FlextDependencyTools",
    # Tool modules
    "FlextGitTools",
    "FlextObservabilityService",  # Legacy
    "FlextOptimizerTools",
    "FlextQualityTools",
    # Legacy aliases
    "FlextScript",  # Legacy
    # PRIMARY API
    "FlextTools",
    "FlextToolsAPI",
    # Namespace classes
    "FlextToolsConstants",
    "FlextToolsExceptions",
    "FlextToolsModels",
    "FlextToolsProtocols",
    "FlextToolsTypes",
    # Utilities
    "FlextToolsUtilities",
    "FlextValidationTools",
    "PoetryOperations",  # Legacy
    "PoetryValidator",  # Legacy
    "ScriptMetadata",  # Legacy
    "colorize",
    "get_project_root",
    "get_stdlib_modules",
    "is_stdlib_module",
    "normalize_path",
    "print_colored",
    "should_ignore_path",
]
