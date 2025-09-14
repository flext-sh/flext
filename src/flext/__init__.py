"""FLEXT Control Panel - Enterprise Data Integration Platform.

The FLEXT Control Panel serves as the central orchestration hub for the FLEXT
data integration ecosystem, providing enterprise-grade workspace management,
pipeline orchestration, and development tooling for the complete 32-project
ecosystem.

This package implements Clean Architecture and Domain-Driven Design patterns
to provide a maintainable, scalable, and extensible control plane for data
integration operations across Oracle, LDAP, WMS, and other enterprise systems.

Key Components:
    - WorkspaceManager: Complete workspace lifecycle management
    - PipelineService: Data pipeline orchestration and monitoring
    - BaseCLI: Command-line interface foundation
    - Development Tools: Quality gates, testing, and validation

Architecture:
    Implements Clean Architecture with clear separation between:
    - Domain Layer: Business logic and entities
    - Application Layer: Use cases and services
    - Infrastructure Layer: Technical implementations
    - Interface Layer: CLI, API, and external communication

Integration:
    - Built on flext-core foundation patterns
    - Integrates with all 32 FLEXT ecosystem projects
    - Coordinates with FlexCore (Go) runtime service
    - Manages Singer/Meltano data pipeline execution

Example:
    Basic workspace management:

    >>> from flext_core import FlextResult
    >>> from flext import WorkspaceManager
    >>> manager = WorkspaceManager("/path/to/workspace")
    >>> result = manager.validate_all_projects()
    >>> if result.is_success:
    ...     print(f"Validated {len(result.data)} projects successfully")

Dependencies:
    - flext-core: Foundation patterns and error handling
    - flext-observability: Monitoring and metrics

Author: FLEXT Development Team
Version: 2.0.0
License: MIT

"""

from __future__ import annotations

# Application Handlers - Direct exports (no wildcards)
from flext.application_handlers import (
    AuthorizingHandler,
    BasicHandler,
    Command,
    CommandBus,
    CommandHandler,
    EventHandler,
    FlextAdvancedHandlerModels,
)

# Application Pipeline - Direct exports (no wildcards)
from flext.application_pipeline import (
    CreatePipelineCommand,
    Entry,
    EntryValidator,
    ExecutePipelineCommand,
    FlextAdvancedPipelineModels,
    FlextAdvancedPipelineService,
    FlextApplicationPipelineService,
)

# Base CLI - Direct exports (no wildcards)
from flext.base_cli import (
    FlextCliApi,
    FlextCliConfig,
    FlextCliFormatters,
    FlextCliMain,
    FlextCliServices,
)

# CLI - Direct exports (no wildcards)
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

# CLI Patterns - Direct exports (no wildcards)
from flext.cli_patterns import (
    FlextCLI,
    FlextCliApi as FlextCliApiPattern,
    FlextCLICommand,
    FlextCLIConfig,
    FlextCliConfig as FlextCliConfigPattern,
    FlextCliFormatters as FlextCliFormattersPattern,
    FlextCLIGroup,
    FlextCliMain as FlextCliMainPattern,
    with_config,
)

# Development Tools - Direct exports (no wildcards)
from flext.dev import (
    FlextAdvancedDevModels,
    FlextAdvancedDevToolsManager,
    OperationStatus,
    OperationType,
    ProjectType,
    create_dev_tools_manager,
)

# Services - Direct exports (no wildcards)
from flext.services import (
    CommandHandler as ServicesCommandHandler,
    CreatePipelineCommand as ServicesCreatePipelineCommand,
    EventHandler as ServicesEventHandler,
    ExecutePipelineCommand as ServicesExecutePipelineCommand,
    FlextUnifiedServices,
    QueryHandler,
    create_services,
)

# Service Utils - Direct exports (no wildcards)
from flext.services_utils import (
    FlextLogger,
    FlextResult,
    FlextUtilities,
)

# Workspace - Direct exports (no wildcards)
from flext.workspace import (
    FlextAdvancedWorkspaceModels,
    FlextAdvancedWorkspaceService,
    FlextWorkspaceService,
    ProjectType as WorkspaceProjectType,
    WorkspaceStatus,
    create_workspace_service,
)

# Workspace CLI - Direct exports (no wildcards)
from flext.workspace_cli import (
    FlextWorkspaceCli,
    build,
    check,
    cli,
    create_workspace_cli,
    docker,
    main as workspace_main,
    status,
    test as workspace_test,
)

# Export all imported symbols - Direct exports without wildcards
__all__ = [
    "AuthorizingHandler",
    "BasicHandler",
    "Command",
    "CommandBus",
    "CommandHandler",
    "CreatePipelineCommand",
    "Entry",
    "EntryValidator",
    "EventHandler",
    "ExecutePipelineCommand",
    "FlextAdvancedDevModels",
    "FlextAdvancedDevToolsManager",
    "FlextAdvancedHandlerModels",
    "FlextAdvancedPipelineModels",
    "FlextAdvancedPipelineService",
    "FlextAdvancedWorkspaceModels",
    "FlextAdvancedWorkspaceService",
    "FlextApplicationPipelineService",
    "FlextCLI",
    "FlextCLICommand",
    "FlextCLIConfig",
    "FlextCLIGroup",
    "FlextCliApi",
    "FlextCliApiPattern",
    "FlextCliConfig",
    "FlextCliConfigPattern",
    "FlextCliFormatters",
    "FlextCliFormattersPattern",
    "FlextCliMain",
    "FlextCliMainPattern",
    "FlextCliServices",
    "FlextControlPanelCli",
    "FlextLogger",
    "FlextResult",
    "FlextUnifiedServices",
    "FlextUtilities",
    "FlextWorkspaceCli",
    "FlextWorkspaceService",
    "OperationStatus",
    "OperationType",
    "ProjectType",
    "QueryHandler",
    "ServicesCommandHandler",
    "ServicesCreatePipelineCommand",
    "ServicesEventHandler",
    "ServicesExecutePipelineCommand",
    "WorkspaceProjectType",
    "WorkspaceStatus",
    "analysis",
    "build",
    "check",
    "cli",
    "create_cli",
    "create_dev_tools_manager",
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
    "with_config",
    "workspace_main",
    "workspace_test",
]

__version__ = "2.0.0"
__author__ = "FLEXT Development Team"
__email__ = "team@flext.sh"
__license__ = "MIT"
__homepage__ = "https://github.com/flext-sh/flext"
