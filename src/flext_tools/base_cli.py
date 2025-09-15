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

# Primary CLI API - delegate to flext-cli
BaseCLI = FlextCliMain  # Main CLI interface
CLIConfig = FlextCliConfig  # Configuration management
CLIApi = FlextCliApi  # CLI API interface


# Direct usage of flext-cli - no facade needed


# Legacy aliases for compatibility
FlextBaseCLI = BaseCLI
FlextCLIConfig = CLIConfig

__all__ = [
    "BaseCLI",
    "CLIApi",
    "CLIConfig",
    "FlextBaseCLI",
    "FlextCLIConfig",
]
