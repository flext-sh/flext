"""Base facade for flext-workspace — service base composition.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import s


class FlextRootServiceBase(s[bool]):
    """Workspace root service base — composes through cooperative FLEXT MRO."""


s: FlextRootServiceBase = FlextRootServiceBase.fetch_global()
"""Process-wide root service base singleton."""

__all__: tuple[str, ...] = ("FlextRootServiceBase", "s")
