"""FLEXT Tools - Enterprise workspace and development utilities.

This module provides comprehensive tooling for FLEXT workspace management,
including quality analysis, dependency management, monitoring, and automation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextTypes

# Base CLI infrastructure - explicit imports
from .base_cli import (
    BaseCLI,
    CLIApi,
    CLIConfig,
    FlextBaseCLI,
    FlextCLIConfig,
    FlextToolsCliService,
)

# CLI tools - explicit imports
from .cli import (
    FlextToolsCLI,
    create_cli_service,
)

# Colors and output utilities - explicit imports
from .colors import (
    Colors,
    colorize,
    print_colored,
)

# Development tools - explicit imports
from .dev import (
    DevToolsManager,
    FlextToolsDevService,
    create_dev_tools_manager,
)

# Documentation generator (without wildcards)
from .documentation_generator import (
    DocumentationGenerator,
)

# Duplicate analysis - explicit imports
from .duplicates import (
    CodeDuplicateAnalyzer,
)

# Handlers - explicit imports
from .handlers import (
    FlextProcessing,
    FlextResult,
)

# Workspace management - explicit imports
from .workspace import (
    FlextToolsWorkspaceService,
    WorkspaceManager,
    create_workspace_manager,
)

# Workspace CLI - explicit imports
from .workspace_cli import (
    FlextCliApi,
    FlextToolsWorkspaceCLIService,
    WorkspaceCLI,
    create_workspace_cli,
)

# Note: Many modules in this package do not have proper __all__ declarations
# and contain implementation details that should not be exported.
# Only modules with clear, well-defined APIs are explicitly imported above.

__all__: FlextTypes.Core.StringList = [
    # Base CLI
    "BaseCLI",
    "CLIApi",
    "CLIConfig",
    # Analysis tools
    "CodeDuplicateAnalyzer",
    # Colors and output
    "Colors",
    # Development tools
    "DevToolsManager",
    # Documentation
    "DocumentationGenerator",
    "FlextBaseCLI",
    "FlextCLIConfig",
    # Workspace CLI
    "FlextCliApi",
    # Handlers
    "FlextProcessing",
    "FlextResult",
    # CLI tools
    "FlextToolsCLI",
    "FlextToolsCliService",
    "FlextToolsDevService",
    "FlextToolsWorkspaceCLIService",
    # Workspace management
    "FlextToolsWorkspaceService",
    "WorkspaceCLI",
    "WorkspaceManager",
    "colorize",
    "create_cli_service",
    "create_dev_tools_manager",
    "create_workspace_cli",
    "create_workspace_manager",
    "print_colored",
]

# Note: This module has been refactored to use explicit imports only.
# Many utility modules that were previously imported with wildcards (*)
# contain implementation details and do not have proper public APIs.
# Users should import specific functions from individual modules as needed.
