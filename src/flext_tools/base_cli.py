"""FLEXT Tools CLI Facade - ANTI-DUPLICATION flext-cli Integration.

CRITICAL: This module is a FACADE to flext-cli. It eliminates ALL CLI duplication
by delegating to the established flext-cli library.

ZERO TOLERANCE ENFORCEMENT: NO local CLI implementations. ALL CLI functionality
MUST use flext-cli exclusively.

DOMAIN SEPARATION: CLI patterns belong to flext-cli domain, NOT flext-tools.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

# ANTI-DUPLICATION: Use flext-cli exclusively - NO Click/Rich direct imports
from flext_cli import (
    FlextCliApi,
    FlextCliConfig,
    FlextCliMain,
)
from flext_core import FlextDomainService, FlextResult

# =============================================================================
# FLEXT-CLI FACADE ALIASES (ELIMINATE DUPLICATION)
# =============================================================================

# Primary CLI API - delegate to flext-cli
BaseCLI = FlextCliMain  # Main CLI interface
CLIConfig = FlextCliConfig  # Configuration management
CLIApi = FlextCliApi  # CLI API interface


# Facade class for backward compatibility
class FlextToolsCliService(FlextDomainService):
    """Facade to flext-cli - eliminates CLI code duplication."""

    def __init__(self) -> None:
        """Initialize with flext-cli dependencies."""
        super().__init__()
        self._cli_api = FlextCliApi()
        self._cli_main = FlextCliMain()

    def execute(self, _request: str = "") -> FlextResult[str]:
        """Execute CLI operation through flext-cli."""
        return FlextResult[str].ok("FlextToolsCliService using flext-cli facade")


# Legacy aliases for compatibility
FlextBaseCLI = BaseCLI
FlextCLIConfig = CLIConfig

__all__ = [
    "BaseCLI",
    "CLIApi",
    "CLIConfig",
    "FlextBaseCLI",
    "FlextCLIConfig",
    "FlextToolsCliService",
]
