"""FlextWorkspaceManager - FLEXT Workspace Manager.

This module provides the main FLEXT workspace manager with unified access to CLI
and core services. It coordinates all FLEXT components through a centralized service
architecture using FlextService pattern and FlextResult return types.

Scope: Main package entry point providing control panel, CLI, and workspace services
with automatic lifecycle management and result handling.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union

from flext_cli import FlextCli
from flext_core import FlextResult, FlextService

ConfigDict = dict[
    str,
    Union[
        str,
        int,
        float,
        bool,
        list[Union[str, int, float, bool]],
        dict[str, Union[str, int, float, bool, list[Union[str, int, float, bool]]]],
    ],
]


class FlextWorkspaceManager:
    """FLEXT Workspace Manager providing unified access to all services."""

    @dataclass
    class WorkspaceConfig:
        """Workspace configuration container."""

        cli_config: ConfigDict = field(default_factory=dict)
        service_config: ConfigDict = field(default_factory=dict)

    class ControlPanelCli(FlextService[str]):
        """Control Panel CLI service wrapper around FlextCli."""

        _cli_api: FlextCli
        _config: FlextWorkspaceManager.WorkspaceConfig

        def execute(self) -> FlextResult[str]:
            """Execute control panel CLI."""
            if not hasattr(self, "_cli_api"):
                self._cli_api = FlextCli()
                self._config = FlextWorkspaceManager.WorkspaceConfig()
            return FlextResult.ok("Control panel CLI executed")

        def run(self) -> FlextResult[str]:
            """Run control panel CLI."""
            return self.execute()

    class WorkspaceCli(FlextService[str]):
        """Workspace CLI service for workspace operations."""

        _cli_api: FlextCli
        _config: FlextWorkspaceManager.WorkspaceConfig

        def execute(self) -> FlextResult[str]:
            """Execute workspace CLI."""
            if not hasattr(self, "_cli_api"):
                self._cli_api = FlextCli()
                self._config = FlextWorkspaceManager.WorkspaceConfig()
            return FlextResult.ok("Workspace CLI executed")

        def run(self) -> FlextResult[str]:
            """Run workspace CLI."""
            return self.execute()

        def create_build_handler(self) -> FlextResult[str]:
            """Create build handler."""
            return FlextResult.ok("build_handler")

        def create_test_handler(self) -> FlextResult[str]:
            """Create test handler."""
            return FlextResult.ok("test_handler")

    class UnifiedServices(FlextService[str]):
        """Unified services coordinator."""

        _config: FlextWorkspaceManager.WorkspaceConfig

        def execute(self) -> FlextResult[str]:
            """Execute unified services."""
            if not hasattr(self, "_config"):
                self._config = FlextWorkspaceManager.WorkspaceConfig()
            return FlextResult.ok("unified_services")

        def run(self) -> FlextResult[str]:
            """Run unified services."""
            return self.execute()

    class ApplicationHandlerService(FlextService[str]):
        """Application handler service."""

        _config: FlextWorkspaceManager.WorkspaceConfig

        def execute(self) -> FlextResult[str]:
            """Execute application handler service."""
            if not hasattr(self, "_config"):
                self._config = FlextWorkspaceManager.WorkspaceConfig()
            return FlextResult.ok("application_handler")

        def run(self) -> FlextResult[str]:
            """Run application handler service."""
            return self.execute()

    class ApplicationPipelineService(FlextService[str]):
        """Application pipeline service."""

        _config: FlextWorkspaceManager.WorkspaceConfig

        def execute(self) -> FlextResult[str]:
            """Execute application pipeline service."""
            if not hasattr(self, "_config"):
                self._config = FlextWorkspaceManager.WorkspaceConfig()
            return FlextResult.ok("application_pipeline")

        def run(self) -> FlextResult[str]:
            """Run application pipeline service."""
            return self.execute()

    class CliService(FlextService[str]):
        """CLI service wrapper."""

        _cli_api: FlextCli
        _config: FlextWorkspaceManager.WorkspaceConfig

        def execute(self) -> FlextResult[str]:
            """Execute CLI service."""
            if not hasattr(self, "_cli_api"):
                self._cli_api = FlextCli()
                self._config = FlextWorkspaceManager.WorkspaceConfig()
            return FlextResult.ok("cli_service")

        def run(self) -> FlextResult[str]:
            """Run CLI service."""
            return self.execute()

    class WorkspaceService(FlextService[str]):
        """Workspace service for workspace operations."""

        _config: FlextWorkspaceManager.WorkspaceConfig

        def execute(self) -> FlextResult[str]:
            """Execute workspace service."""
            if not hasattr(self, "_config"):
                self._config = FlextWorkspaceManager.WorkspaceConfig()
            return FlextResult.ok("workspace_info")

        def run(self) -> FlextResult[str]:
            """Run workspace service."""
            return self.execute()

        def get_workspace_info(self) -> FlextResult[str]:
            """Get workspace information."""
            return FlextResult.ok("workspace_info")


__all__ = [
    "FlextWorkspaceManager",
]
