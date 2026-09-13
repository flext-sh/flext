"""Models facade for flext-workspace — m.Root project namespace.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import m as m_core

from ._models.base import FlextRootModelsBase


class FlextRootModels(m_core):
    """Workspace root models facade — access via m.Root.*."""

    class Root(
        FlextRootModelsBase,
    ):
        """Workspace root models MRO composition."""


m = FlextRootModels

__all__: tuple[str, ...] = ("FlextRootModels", "m")

