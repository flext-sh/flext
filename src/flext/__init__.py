"""Flext workspace package.

This module provides the main entry point and shared components for the flext package.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# Import core aliases for convenience
from flext_core import (
    FlextDecorators,
    FlextExceptions,
    FlextHandlers,
    FlextResult,
)

from flext.constants import FlextConstants, c
from flext.models import FlextModels, m
from flext.protocols import FlextProtocols, p
from flext.service import FlextServiceBase, s
from flext.types import FlextTypes, t
from flext.utilities import FlextUtilities, u

# Shared from flext-core
d = FlextDecorators
e = FlextExceptions
r = FlextResult
h = FlextHandlers

__all__ = [
    "FlextConstants",
    "FlextDecorators",
    "FlextExceptions",
    "FlextHandlers",
    "FlextModels",
    "FlextProtocols",
    "FlextResult",
    "FlextServiceBase",
    "FlextTypes",
    "FlextUtilities",
    "c",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "u",
]
