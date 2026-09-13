"""Models facade for flext-workspace — m.Root project namespace.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import m

from ._models.base import FlextRootModelsBase
from ._models.config import FlextRootModelsConfig


class FlextRootModels(m):
    """Workspace root models facade — access via m.Root.*."""

    class Root(
        FlextRootModelsBase,
        FlextRootModelsConfig,
    ):
        """Workspace root models MRO composition."""


m = FlextRootModels

__all__: tuple[str, ...] = ("FlextRootModels", "m")

