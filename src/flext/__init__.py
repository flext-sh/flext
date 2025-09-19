"""FLEXT Control Panel - Enterprise Data Integration Platform.

Author: FLEXT Development Team
Version: 0.9.0
License: MIT

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
)
from flext.cli_patterns import (
    FlextCliApi as FlextCliApiPattern,
    FlextCliConfigs as FlextCliConfigsPattern,
    FlextCliFormatters as FlextCliFormattersPattern,
    FlextCliMain as FlextCliMainPattern,
)
from flext.dev import (
    FlextAdvancedDevModels,
    FlextAdvancedDevToolsManager,
    FlextProjectTypes as DevFlextProjectTypes,
    create_dev_tools_manager,
)
from flext.dev_enums import FlextDevEnums
from flext.project_types import FlextProjectTypes
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
)
from flext.workspace_cli import (
    FlextWorkspaceCli,
    build,
    check,
    create_workspace_cli,
    docker,
    main as workspace_main,
    status,
    test as workspace_test,
)
from flext_cli import (
    FlextCliApi,
    FlextCliConfigs,
    FlextCliFormatters,
    FlextCliMain,
    FlextCliService,
)

# ProjectType and WorkspaceStatus are already imported from flext.workspace


__all__ = [
    # Application handlers
    "FlextApplicationHandlerService",
    "create_handler_service",

    # Application pipeline
    "FlextApplicationPipelineService",
    "create_pipeline_service",

    # CLI functionality
    "FlextControlPanelCli",
    "analysis",
    "build",
    "check",
    "create_cli",
    "create_workspace_cli",
    "docker",
    "format_code",
    "info",
    "lint",
    "main",
    "quality",
    "scripts",
    "status",
    "workspace_main",
    "workspace_test",

    # CLI patterns
    "FlextCliApiPattern",
    "FlextCliConfigsPattern",
    "FlextCliFormattersPattern",
    "FlextCliMainPattern",

    # Development tools
    "FlextAdvancedDevModels",
    "FlextAdvancedDevToolsManager",
    "create_dev_tools_manager",

    # Development enums
    "FlextDevEnums",

    # Project types
    "FlextProjectTypes",

    # Services
    "FlextUnifiedServices",
    "create_services",

    # Services utilities
    "FlextLogger",
    "FlextResult",
    "FlextUtilities",

    # Workspace
    "FlextAdvancedWorkspaceModels",
    "FlextWorkspaceCli",
    "FlextWorkspaceService",

    # CLI from flext-cli
    "FlextCliApi",
    "FlextCliConfigs",
    "FlextCliFormatters",
    "FlextCliMain",
    "FlextCliService",
]

__version__ = "0.9.0"
__author__ = "FLEXT Development Team"
__email__ = "team@flext.sh"
__license__ = "MIT"
__homepage__ = "https://github.com/flext-sh/flext"
