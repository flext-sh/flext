"""API facade for flext-workspace — public service surface.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import override

from flext_core import p, r, s


class FlextRoot(s[bool]):
    """Workspace root API facade — service surface entry point."""

    @override
    def execute(self) -> p.Result[bool]:
        """Execute the root API contract."""
        return r[bool].ok(True)


api: FlextRoot = FlextRoot.fetch_global()
"""Process-wide flext API facade singleton resolved from the global container."""

flext: FlextRoot = FlextRoot.fetch_global()
"""Root package canonical alias resolved from the global container."""

__all__: tuple[str, ...] = ("FlextRoot", "api", "flext")
