"""Foundational configuration contracts for the FLEXT workspace root.

Declares base schema definitions and contract markers for the workspace-level
configuration hierarchy before domain-specific settings are composed.

See Also:
    - ADR-005: Config, Settings, Constants, Templates, Schemas SSOT.
    - ADR-016: Settings & Config Singleton Contract.
    - :class:`flext.config.FlextRootConfig`: Composed public configuration facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations


class FlextRootConfigBase:
    """Base configuration provider for root workspace options.

    Acts as the foundational class in the configuration inheritance chain,
    establishing baseline schema attributes and validation behaviors.
    """


__all__: list[str] = ["FlextRootConfigBase"]
