"""FLEXT Control Panel - Enterprise Data Integration Platform.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext.application_handlers import (
    FlextApplicationHandlerService,
    create_handler_service,
)
from flext.application_pipeline import (
    FlextApplicationPipelineService,
    create_pipeline_service,
)
from flext.base_cli import (
    FlextCliApi,
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
    FlextCliApi as FlextCliApiPattern,
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

__all__ = [
    "DevToolsManager",
    "FlextAdvancedDevModels",
    "FlextAdvancedDevToolsManager",
    "FlextAdvancedWorkspaceModels",
    "FlextApplicationHandlerService",
    "FlextApplicationPipelineService",
    "FlextCliApi",
    "FlextCliApiPattern",
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
]

__version__ = "0.9.0"
__author__ = "FLEXT Development Team"
__email__ = "team@flext.sh"
__license__ = "MIT"
__homepage__ = "https://github.com/flext-sh/flext"
