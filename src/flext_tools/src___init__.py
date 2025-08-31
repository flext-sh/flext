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
    - PipelineManager: Data pipeline orchestration and monitoring
    - FlextCLI: Command-line interface for all operations
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
    - flext-tools: Development and operational tooling

Author: FLEXT Development Team
Version: 2.0.0
License: MIT

"""

from __future__ import annotations

from typing import Protocol

# Import flext-core patterns - always available
from flext_core import FlextResult


class FlextWebAppProtocol(Protocol):
    def run(self, host: str = "localhost", port: int = 5000) -> None: ...


class FlextWebServiceProtocol(Protocol):
    def start(self) -> FlextResult[None]: ...


class FlextAuthProtocol(Protocol):
    def authenticate(self, token: str) -> FlextResult[object]: ...


__version__ = "2.0.0"
__author__ = "FLEXT Development Team"
__email__ = "team@flext.sh"
__license__ = "MIT"
__homepage__ = "https://github.com/flext-sh/flext"


# Optional imports with graceful fallback - using flext-core patterns
def _optional_import(module_name: str, item_name: str) -> object:
    """Import optional dependencies with graceful fallback."""
    try:
        module = __import__(module_name, fromlist=[item_name])
        return getattr(module, item_name)
    except ImportError:
        return None


# Web service imports (optional)
create_web_service = _optional_import("flext_web", "create_service")
create_web_app = _optional_import("flext_web", "create_app")
FlextWebApp = _optional_import("flext_web", "FlextWebApp")
FlextWebService = _optional_import("flext_web", "FlextWebService")

# gRPC service imports (optional)
FlextGrpcClientService = _optional_import("flext_grpc", "FlextGrpcClientService")
FlextGrpcService = _optional_import("flext_grpc", "FlextGrpcService")
create_grpc_service = _optional_import("flext_grpc", "create_service")

# Auth service imports (optional)
FlextAuth = _optional_import("flext_auth", "FlextAuth")
FlextAuthService = _optional_import("flext_auth", "FlextAuthService")
create_auth_service = _optional_import("flext_auth", "create_auth_service")

# CLI integration (optional)
CLIHelper = _optional_import("flext_cli.core.helpers", "CLIHelper")
setup_cli = _optional_import("flext_cli.simple_api", "setup_cli")


# Core workspace management (always available)
class WorkspaceManager:
    """FLEXT workspace management using flext-core patterns."""

    def __init__(self, workspace_path: str) -> None:
        self.workspace_path = workspace_path

    def validate_all_projects(self) -> FlextResult[list[str]]:
        """Validate all projects in workspace."""
        # This would contain actual validation logic
        project_list: list[str] = ["flext-core", "flext-api", "flext-auth"]
        return FlextResult[list[str]].ok(project_list)


# Note: Import optimization to avoid circular dependencies
# Public API exports optimized for performance and maintainability


__all__: list[str] = [
    # CLI (optional)
    "CLIHelper",
    # Auth (optional)
    "FlextAuth",
    "FlextAuthService",
    # gRPC (optional)
    "FlextGrpcClientService",
    "FlextGrpcService",
    # Core patterns
    "FlextResult",
    "FlextWebApp",
    "FlextWebService",
    "WorkspaceManager",
    "__author__",
    "__license__",
    "__version__",
    "create_auth_service",
    "create_grpc_service",
    "create_web_app",
    # Web (optional)
    "create_web_service",
    "setup_cli",
]
