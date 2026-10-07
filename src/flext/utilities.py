"""Utilities facade for flext-workspace — u.Root project namespace.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import flext_infra

from flext._utilities.base import FlextRootUtilitiesBase
from flext._utilities.config import FlextRootUtilitiesConfig


class FlextRootUtilities(flext_infra.u):
    """Workspace root utilities facade — access via u.Root.*."""

    class Root(FlextRootUtilitiesBase, FlextRootUtilitiesConfig):
        """Workspace root utilities MRO composition."""


u = FlextRootUtilities

__all__ = ("FlextRootUtilities", "u")
