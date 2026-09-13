"""Protocols facade for flext-workspace — p.Root project namespace.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import p as p_core

from ._protocols.base import FlextRootProtocolsBase


class FlextRootProtocols(p_core):
    """Workspace root protocols facade — access via p.Root.*."""

    class Root(
        FlextRootProtocolsBase,
    ):
        """Workspace root protocols MRO composition."""


p = FlextRootProtocols

__all__: tuple[str, ...] = ("FlextRootProtocols", "p")

