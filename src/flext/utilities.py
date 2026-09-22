"""Utilities facade for flext-workspace — u.Root project namespace.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core import u

from ._utilities.base import FlextRootUtilitiesBase
from ._utilities.config import FlextRootUtilitiesConfig

if TYPE_CHECKING:
    from . import t


class FlextRootUtilities(u):
    """Workspace root utilities facade — access via u.Root.*."""

    class Root(FlextRootUtilitiesBase, FlextRootUtilitiesConfig):
        """Workspace root utilities MRO composition."""


u = FlextRootUtilities

__all__: t.VariadicTuple[str] = ("FlextRootUtilities", "u")
