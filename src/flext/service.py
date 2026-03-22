"""Service base for flext-core package.

This module provides the base service class for the flext-core package.
No inheritance from higher domains - core is the foundation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import ClassVar

from flext_core import c, m, t, u


class FlextRootServiceBase:
    """Base service class for flext-core package."""

    Constants: ClassVar[type] = c
    Models: ClassVar[type] = m
    Types: ClassVar[type] = t
    Utilities: ClassVar[type] = u


s = FlextRootServiceBase
