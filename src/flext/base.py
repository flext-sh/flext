"""Base facade for flext-workspace — service base composition.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core import s

if TYPE_CHECKING:
    from . import t


class FlextRootServiceBase(s[bool]):
    """Workspace root service base — composes through cooperative FLEXT MRO."""


s = FlextRootServiceBase

__all__: t.VariadicTuple[str] = ("FlextRootServiceBase", "s")
