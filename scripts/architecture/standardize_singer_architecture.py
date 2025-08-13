#!/usr/bin/env python3
"""Singer Architecture Standardizer - consolidated in flext-meltano.

This module is now a compatibility layer that imports from flext-meltano.
All new development should use flext_meltano.architecture directly.

Implements the architectural directive:
"Singer, Meltano e DBT tem que estar em flext-meltano, "
"acabae com essa confusão arrumando isso"
"""

from __future__ import annotations

from pathlib import Path

# Conditional import since the architecture module may not exist yet
try:
    from flext_meltano.architecture import (
        FlextSingerArchitectureStandardizer,
    )

    ARCHITECTURE_MODULE_AVAILABLE = True
except ImportError:
    # Create stub implementation when module is not available
    class FlextSingerArchitectureStandardizer:
        def __init__(self, flext_root: Path) -> None:
            self.flext_root = flext_root

        def standardize_architecture(self) -> None:
            print("⚠️  Architecture standardization skipped - module not available")
            print("   flext-meltano architecture module not found")

    ARCHITECTURE_MODULE_AVAILABLE = False


def main() -> None:
    """Main execution function."""
    flext_root = Path("/home/marlonsc/flext")

    if not flext_root.exists():
        msg: str = f"FLEXT root directory not found: {flext_root}"
        raise RuntimeError(msg)

    standardizer = FlextSingerArchitectureStandardizer(flext_root)
    standardizer.standardize_architecture()

    if not ARCHITECTURE_MODULE_AVAILABLE:
        print("⚠️  Note: This script requires the flext-meltano architecture module")


if __name__ == "__main__":
    main()
