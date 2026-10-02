"""Protocols facade for flext-workspace — p.Root project namespace.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flext_infra
from flext._protocols.base import FlextRootProtocolsBase
from flext._protocols.config import FlextRootProtocolsConfig

if TYPE_CHECKING:
    from flext import t


class FlextRootProtocols(flext_infra.p):
    """Workspace root protocols facade — access via p.Root.*."""

    class Root(FlextRootProtocolsBase, FlextRootProtocolsConfig):
        """Workspace root protocols MRO composition."""


p = FlextRootProtocols

__all__: t.VariadicTuple[str] = ("FlextRootProtocols", "p")
