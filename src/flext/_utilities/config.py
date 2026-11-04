"""Configuration helper utilities and serialization routines for the FLEXT workspace.

Provides utility functions for reading, converting, sanitizing, and validating
configuration parameters and environment values.

See Also:
    - ADR-005: Config, Settings, Constants, Templates, Schemas SSOT.
    - ADR-016: Settings & Config Singleton Contract.
    - :class:`flext._utilities.base.FlextRootUtilitiesBase`: Foundational utilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations


class FlextRootUtilitiesConfig:
    """Configuration-specific utility methods and parameter parsers.

    Contains specialized functions to parse, transform, and normalize configuration
    structures into typed models and immutable dictionaries.
    """


__all__ = ("FlextRootUtilitiesConfig",)
