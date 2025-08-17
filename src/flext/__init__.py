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

    >>> from flext import WorkspaceManager, FlextResult
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

__version__ = "2.0.0"
__author__ = "FLEXT Development Team"
__email__ = "team@flext.sh"
__license__ = "MIT"
__homepage__ = "https://github.com/flext-sh/flext"

# Core FLEXT imports - enterprise integration patterns
from flext_web import (
    create_service as create_web_service,
    create_app as create_web_app,
    FlextWebApp,
    FlextWebService,
)
from flext_grpc import (
    FlextGrpcClientService,
    FlextGrpcService,
    create_service as create_grpc_service,
)
from flext_auth import FlextAuth, FlextAuthService, create_auth_service

# CLI integration
from flext_cli.core.helpers import CLIHelper
from flext_cli.simple_api import setup_cli

# Note: Import optimization to avoid circular dependencies
# Public API exports optimized for performance and maintainability

__all__: list[str] = [
    "__author__",
    "__license__",
    "__version__",
    # Web
    "create_web_service",
    "create_web_app",
    "FlextWebApp",
    "FlextWebService",
    # gRPC
    "FlextGrpcClientService",
    "FlextGrpcService",
    "create_grpc_service",
    # Auth
    "FlextAuth",
    "FlextAuthService",
    "create_auth_service",
    # CLI
    "CLIHelper",
    "setup_cli",
]
