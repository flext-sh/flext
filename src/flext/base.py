"""Base facade for flext-workspace — service base composition.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import s as s_core


class FlextRootServiceBase(s_core[bool]):
    """Workspace root service base — composes through cooperative FLEXT MRO."""


s = FlextRootServiceBase

__all__: tuple[str, ...] = ("FlextRootServiceBase", "s")
