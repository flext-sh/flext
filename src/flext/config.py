"""Config facade for flext-workspace — workspace-level configuration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

import flext_core

if TYPE_CHECKING:
    from . import t


class FlextRootConfig(flext_core.FlextConfig):
    """Workspace root configuration — extends flext-core config."""

    CONFIG_DIR: ClassVar[str] = "config"


config: FlextRootConfig = FlextRootConfig.fetch_global()
"""Process-wide root configuration singleton."""

__all__: t.VariadicTuple[str] = ("FlextRootConfig", "config")
