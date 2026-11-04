"""Workspace configuration definitions and property specifications.

Provides concrete configuration attributes and workspace defaults composed
into the root configuration facade.

See Also:
    - ADR-005: Config, Settings, Constants, Templates, Schemas SSOT.
    - ADR-016: Settings & Config Singleton Contract.
    - :class:`flext._config.base.FlextRootConfigBase`: Base configuration contract.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations


class FlextRootConfigConfig:
    """Concrete configuration schema for workspace-level parameters.

    Binds specific configuration fields, property accessors, and defaults
    utilized across root workspace tasks and operations.
    """


__all__: list[str] = ["FlextRootConfigConfig"]
