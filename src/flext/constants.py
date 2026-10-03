"""Constants facade for flext-workspace — c.Root project namespace.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flext_core
from flext._constants.base import FlextRootConstantsBase
from flext._constants.config import FlextRootConstantsConfig

if TYPE_CHECKING:
    from flext import t


class FlextRootConstants(flext_core.c):
    """Workspace root constants facade — access via c.Root.*."""

    class Root(FlextRootConstantsBase, FlextRootConstantsConfig):
        """Workspace root constants MRO composition."""


c = FlextRootConstants

__all__: t.VariadicTuple[str] = ("FlextRootConstants", "c")
