"""Models facade for flext-workspace — m.Root project namespace.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import flext_infra

from flext._models.base import FlextRootModelsBase
from flext._models.config import FlextRootModelsConfig


class FlextRootModels(flext_infra.m):
    """Workspace root models facade — access via m.Root.*."""

    class Root(FlextRootModelsBase, FlextRootModelsConfig):
        """Workspace root models MRO composition."""


m = FlextRootModels

__all__ = ("FlextRootModels", "m")
