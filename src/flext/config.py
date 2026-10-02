"""Config facade for flext-workspace — workspace-level configuration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flext_core

if TYPE_CHECKING:
    from flext import t


class FlextRootConfig(flext_core.FlextConfig):
    """Workspace root configuration — extends flext-core config."""

    @classmethod
    def published(cls) -> FlextRootConfig:
        """Return the process-wide configuration singleton.

        Returns:
            The resulting ``FlextRootConfig``.

        """
        return cls.fetch_global()


config = FlextRootConfig.published()
"""The singleton alias the rule contract allows beside the facade class."""

__all__: t.VariadicTuple[str] = ("FlextRootConfig", "config")
