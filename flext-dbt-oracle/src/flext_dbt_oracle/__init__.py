"""FLEXT Enterprise - dbt-oracle adapter component."""

from __future__ import annotations

# Re-export from dbt.adapters.oracle
from dbt.adapters.oracle import *  # noqa: F403

__version__ = "1.0.0"
__version_info__ = (1, 0, 0)

__all__ = ["__version__", "__version_info__"]
