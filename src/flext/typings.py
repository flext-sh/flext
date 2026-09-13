"""Typings facade for flext-workspace — t.Root project namespace.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import t as t_core

from ._typings.base import FlextRootTypingsBase


class FlextRootTypes(t_core):
    """Workspace root typings facade — access via t.Root.*."""

    class Root(
        FlextRootTypingsBase,
    ):
        """Workspace root typings MRO composition."""


t = FlextRootTypes

__all__: tuple[str, ...] = ("FlextRootTypes", "t")

