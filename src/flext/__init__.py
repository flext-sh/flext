"""Flext workspace package.

This module provides the main entry point and shared components for the flext package.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import (
    FlextCliCommonParams,
    FlextCliSettings,
)

from flext_core import (
    FlextConstants,
    FlextContainer,
    FlextContext,
    FlextDecorators,
    FlextDispatcher,
    FlextExceptions,
    FlextHandlers,
    FlextModels,
    FlextProtocols,
    FlextResult,
    FlextRuntime,
    FlextService,
    FlextSettings,
    FlextTypes,
    FlextUtilities,
)
from flext_core.service import FlextService as FlextServiceBase

__all__ = [
    "FlextCliCommonParams",
    "FlextCliSettings",
    "FlextConstants",
    "FlextContainer",
    "FlextContext",
    "FlextDecorators",
    "FlextDispatcher",
    "FlextExceptions",
    "FlextHandlers",
    "FlextModels",
    "FlextProtocols",
    "FlextResult",
    "FlextRuntime",
    "FlextService",
    "FlextServiceBase",
    "FlextSettings",
    "FlextTypes",
    "FlextUtilities",
]
