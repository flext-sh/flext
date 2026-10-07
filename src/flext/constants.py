"""Constants facade for flext-workspace — c.Root project namespace.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import flext_infra
from flext._constants import FlextRootConstantsBase
from flext._constants import FlextRootConstantsConfig


class FlextRootConstants(flext_infra.c):
    """Workspace root constants facade — access via c.Root.*."""

    class Root(FlextRootConstantsBase, FlextRootConstantsConfig):
        """Workspace root constants MRO composition."""


c = FlextRootConstants

__all__ = ("FlextRootConstants", "c")
