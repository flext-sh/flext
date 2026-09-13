"""Config facade for flext-workspace — config singleton.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextConfig


class FlextRootConfig(FlextConfig):
    """Workspace root config facade — access via config.*."""


config = FlextRootConfig.fetch_global()

__all__: tuple[str, ...] = ("FlextRootConfig", "config")
