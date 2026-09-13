"""Base facade for flext-workspace — re-exports flext_core base.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import s as s_core


class FlextRootServiceBase(s_core):
    """Workspace root base facade — delegates to flext_core base."""


s = FlextRootServiceBase

__all__: tuple[str, ...] = ("FlextRootServiceBase", "s")
