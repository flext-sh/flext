"""Protocols facade for flext-workspace — p.Root project namespace.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import p

from ._protocols.base import FlextRootProtocolsBase
from ._protocols.config import FlextRootProtocolsConfig


class FlextRootProtocols(p):
    """Workspace root protocols facade — access via p.Root.*."""

    class Root(
        FlextRootProtocolsBase,
        FlextRootProtocolsConfig,
    ):
        """Workspace root protocols MRO composition."""


p = FlextRootProtocols

__all__: tuple[str, ...] = ("FlextRootProtocols", "p")

