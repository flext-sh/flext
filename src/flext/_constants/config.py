"""Configuration and workspace parameter constants.

Declares configuration keys, environment variable names, and default threshold
constants composed into the root constants namespace ``c.Root``.

See Also:
    - ADR-005: Config, Settings, Constants, Templates, Schemas SSOT.
    - ADR-027: Facade Single-Owner Law.
    - :class:`flext._constants.base.FlextRootConstantsBase`: Base constants definitions.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations


class FlextRootConstantsConfig:
    """Configuration-specific constant values and parameter keys.

    Defines immutable names and operational parameters used to resolve and
    validate configuration inputs across the workspace.
    """


__all__ = ("FlextRootConstantsConfig",)
