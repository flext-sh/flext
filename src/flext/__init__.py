"""Flext workspace package.

This module provides the main entry point and shared components for the flext package.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# Import core aliases for convenience
from flext_core import (
    FlextContainer,
    FlextContext,
    FlextDecorators,
    FlextDispatcher,
    FlextExceptions,
    FlextHandlers,
    FlextResult,
    FlextRuntime,
    FlextService,
    FlextSettings,
)

from flext.constants import FlextConstants, c
from flext.models import FlextModels, m
from flext.protocols import FlextProtocols, p
from flext.service import FlextServiceBase
from flext.types import FlextTypes, t
from flext.utilities import FlextUtilities, u

# Shared from flext-core
container = FlextContainer
ctx = FlextContext
d = FlextDecorators
dispatcher = FlextDispatcher
e = FlextExceptions
h = FlextHandlers
r = FlextResult
rt = FlextRuntime
s = FlextService
settings = FlextSettings

__all__ = [
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
    "c",
    "container",
    "ctx",
    "d",
    "dispatcher",
    "e",
    "h",
    "m",
    "p",
    "r",
    "rt",
    "s",
    "settings",
    "t",
    "u",
]
