"""FLEXT Tools - Consolidated workspace tools library.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Unified entry point consolidating 85+ scripts into 6 tool modules + utilities.
"""

#  Unified API (PRIMARY IMPORT)
from flext_tools.api import FlextTools, FlextToolsAPI

# Tool modules (6 unified modules consolidating 85+ scripts)
from flext_tools.architecture_tools import FlextArchitectureTools

# Namespace classes
from flext_tools.constants import FlextToolsConstants
from flext_tools.dependency_tools import FlextDependencyTools
from flext_tools.exceptions import FlextToolsExceptions
from flext_tools.git_tools import FlextGitTools
from flext_tools.models import FlextToolsModels
from flext_tools.optimizer_tools import FlextOptimizerTools
from flext_tools.protocols import FlextToolsProtocols
from flext_tools.quality_tools import FlextQualityTools
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

__all__ = [
    "Colors",
    "FlextArchitectureTools",
    "FlextDependencyTools",
    # Tool modules
    "FlextGitTools",
    "FlextOptimizerTools",
    "FlextQualityTools",
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
    "colorize",
    "get_project_root",
    "get_stdlib_modules",
    "is_stdlib_module",
    "normalize_path",
    "print_colored",
    "should_ignore_path",
]
