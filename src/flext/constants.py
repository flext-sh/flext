"""Constants facade for flext-workspace — c.Root project namespace.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import c as c_core

from ._constants.base import FlextRootConstantsBase


class FlextRootConstants(c_core):
    """Workspace root constants facade — access via c.Root.*."""

    class Root(
        FlextRootConstantsBase,
    ):
        """Workspace root constants MRO composition."""


c = FlextRootConstants

__all__: tuple[str, ...] = ("FlextRootConstants", "c")

