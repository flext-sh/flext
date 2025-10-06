"""
FLEXT Control Panel - Enterprise Data Integration Platform.

FLEXT is a comprehensive enterprise data integration platform that provides a unified
framework for data processing, transformation, and integration across multiple domains
including LDAP, Oracle, and various enterprise systems.

This module contains the core FLEXT application framework including:

    - CLI interface for data integration operations
    - Workspace management for project coordination
    - Application handlers for pipeline orchestration
    - Development tools for workflow automation
    - Service utilities for enterprise operations

The platform follows clean architecture principles with CQRS patterns, railway-oriented
programming, and comprehensive error handling throughout.

Attributes:
    PROJECT_VERSION (FlextVersion): Current version of the FLEXT project.
    __version__ (str): Version string for the package.
    __version_info__ (tuple): Detailed version information.

Example:
    >>> from flext import FlextCli, create_cli
    >>>
    >>> # Create and run FLEXT CLI
    >>> cli = create_cli()
    >>> cli.run()

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""
from __future__ import annotations

from typing import Final


from flext.version import VERSION, FlextVersion
from flext.application_handlers import (
    FlextApplicationHandlerService,
    create_handler_service,
)
from flext.application_pipeline import (
    FlextApplicationPipelineService,
    create_pipeline_service,
)
from flext.base_cli import (
    FlextCli,
    FlextCliContext,
    FlextCliModels,
    FlextCliOutput,
    FlextCliService,
)
from flext.cli import (
    FlextControlPanelCli,
    analysis,
    create_cli,
    format_code,
    info,
    lint,
    main,
    quality,
    scripts,
    test,
)
from flext.cli_patterns import (
    FlextCli as FlextCliPattern,
    FlextCliContext as FlextCliContextPattern,
    FlextCliOutput as FlextCliFormattersPattern,
)
from flext.dev import (
    DevToolsManager,
    FlextAdvancedDevModels,
    FlextAdvancedDevToolsManager,
    create_dev_tools_manager,
)
from flext.dev_enums import FlextDevEnums, OperationStatus, OperationType
from flext.project_types import FlextProjectTypes, ProjectType
from flext.services import (
    FlextUnifiedServices,
    create_services,
)
from flext.services_utils import (
    FlextLogger,
    FlextResult,
    FlextUtilities,
)
from flext.workspace import (
    FlextAdvancedWorkspaceModels,
    FlextWorkspaceService,
    WorkspaceStatus,
    create_workspace_service,
)
from flext.workspace_cli import (
    FlextWorkspaceCli,
    build,
    check,
    create_workspace_cli,
    docker,
    main as workspace_main,
    run_tests as workspace_test,
    status,
)
from flext_cli import (
    FlextCliCommands,
)

PROJECT_VERSION: Final[FlextVersion] = VERSION

__version__: str = VERSION.version
__version_info__: tuple[int | str, ...] = VERSION.version_info

__all__ = [
    "DevToolsManager",
    "FlextAdvancedDevModels",
    "FlextAdvancedDevToolsManager",
    "FlextAdvancedWorkspaceModels",
    "FlextApplicationHandlerService",
    "FlextApplicationPipelineService",
    "FlextCli",
    "FlextCliPattern",
    "FlextCliCommands",
    "FlextCliContext",
    "FlextCliContextPattern",
    "FlextCliFormattersPattern",
    "FlextCliModels",
    "FlextCliOutput",
    "FlextCliService",
    "FlextControlPanelCli",
    "FlextDevEnums",
    "FlextLogger",
    "FlextProjectTypes",
    "FlextResult",
    "FlextUnifiedServices",
    "FlextUtilities",
    "FlextWorkspaceCli",
    "FlextWorkspaceService",
    "OperationStatus",
    "OperationType",
    "ProjectType",
    "WorkspaceStatus",
    "analysis",
    "build",
    "check",
    "create_cli",
    "create_dev_tools_manager",
    "create_handler_service",
    "create_pipeline_service",
    "create_services",
    "create_workspace_cli",
    "create_workspace_service",
    "docker",
    "format_code",
    "info",
    "lint",
    "main",
    "quality",
    "scripts",
    "status",
    "test",
    "workspace_main",
    "workspace_test",
    "FlextVersion",
    "VERSION",
    "PROJECT_VERSION",
    "__version__",
    "__version_info__",
]
