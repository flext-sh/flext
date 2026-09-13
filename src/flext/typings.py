"""Typings facade for flext-workspace — t.Root project namespace.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import t

from ._typings.base import FlextRootTypingsBase
from ._typings.config import FlextRootTypingsConfig


class FlextRootTypes(t):
    """Workspace root typings facade — access via t.Root.*."""

    class Root(
        FlextRootTypingsBase,
        FlextRootTypingsConfig,
    ):
        """Workspace root typings MRO composition."""


t = FlextRootTypes

__all__: tuple[str, ...] = ("FlextRootTypes", "t")

