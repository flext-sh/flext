"""Constants facade for flext-workspace — c.Root project namespace.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core import c

from ._constants.base import FlextRootConstantsBase
from ._constants.config import FlextRootConstantsConfig

if TYPE_CHECKING:
    from . import t


class FlextRootConstants(c):
    """Workspace root constants facade — access via c.Root.*."""

    class Root(FlextRootConstantsBase, FlextRootConstantsConfig):
        """Workspace root constants MRO composition."""


c = FlextRootConstants

__all__: t.VariadicTuple[str] = ("FlextRootConstants", "c")
