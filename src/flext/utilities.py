"""Utilities facade for flext-workspace — u.Root project namespace.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import u

from ._utilities.base import FlextRootUtilitiesBase
from ._utilities.config import FlextRootUtilitiesConfig


class FlextRootUtilities(u):
    """Workspace root utilities facade — access via u.Root.*."""

    class Root(
        FlextRootUtilitiesBase,
        FlextRootUtilitiesConfig,
    ):
        """Workspace root utilities MRO composition."""


u = FlextRootUtilities

__all__: tuple[str, ...] = ("FlextRootUtilities", "u")

