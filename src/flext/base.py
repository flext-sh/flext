"""Base facade for flext-workspace — root service foundation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import s


class FlextRootServiceBase(s[bool]):
    """Workspace root service base — service surface foundation."""


s = FlextRootServiceBase

__all__: list[str] = ["FlextRootServiceBase", "s"]
