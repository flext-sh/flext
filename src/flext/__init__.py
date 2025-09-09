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

"""FLEXT - Enterprise Data Integration Platform.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

# Import all from each module with proper type handling - FLEXT Pattern
from flext.application_handlers import *  # type: ignore[unused-ignore,reportWildcardImport,assignment,import-untyped] # noqa: F403
from flext.application_pipeline import *  # type: ignore[unused-ignore,reportWildcardImport,assignment,import-untyped] # noqa: F403
from flext.base_cli import FlextBaseCLI, CLIConfig, with_config, with_output_format  # type: ignore[unused-ignore,reportWildcardImport,assignment,import-untyped] # noqa: F403
from flext.cli import main, quality  # type: ignore[unused-ignore,reportWildcardImport,assignment,import-untyped] # noqa: F403
from flext.cli_patterns import *  # type: ignore[unused-ignore,reportWildcardImport,assignment,import-untyped] # noqa: F403
from flext.dev import *  # type: ignore[unused-ignore,reportWildcardImport,assignment,import-untyped] # noqa: F403
from flext.services import *  # type: ignore[unused-ignore,reportWildcardImport,assignment,import-untyped] # noqa: F403
from flext.services_utils import *  # type: ignore[unused-ignore,reportWildcardImport,assignment,import-untyped] # noqa: F403
from flext.workspace import *  # type: ignore[unused-ignore,reportWildcardImport,assignment,import-untyped] # noqa: F403
from flext.workspace_cli import *  # type: ignore[unused-ignore,reportWildcardImport,assignment,import-untyped] # noqa: F403

# Combine all __all__ from all modules - FLEXT Pattern
import flext.application_handlers as _application_handlers
import flext.application_pipeline as _application_pipeline
import flext.base_cli as _base_cli
import flext.cli as _cli
import flext.cli_patterns as _cli_patterns
import flext.dev as _dev
import flext.services as _services
import flext.services_utils as _services_utils
import flext.workspace as _workspace
import flext.workspace_cli as _workspace_cli

# Collect all exports from modules - FLEXT Pattern
_collected_exports: list[str] = []
for module in [_application_handlers, _application_pipeline, _base_cli, _cli, _cli_patterns, _dev, _services, _services_utils, _workspace, _workspace_cli]:
    if hasattr(module, "__all__") and module.__all__:
        module_all = getattr(module, "__all__", [])
        if isinstance(module_all, list):
            _collected_exports.extend(module_all)

# Remove duplicates and sort - FLEXT Pattern
__all__ = sorted(set(_collected_exports))

__version__ = "2.0.0"
__author__ = "FLEXT Development Team"
__email__ = "team@flext.sh"
__license__ = "MIT"
__homepage__ = "https://github.com/flext-sh/flext"
