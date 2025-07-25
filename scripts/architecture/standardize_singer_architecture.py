#!/usr/bin/env python3
"""Singer Architecture Standardizer - consolidated in flext-meltano.

This module is now a compatibility layer that imports from flext-meltano.
All new development should use flext_meltano.architecture directly.

Implements the architectural directive:
"Singer, Meltano e DBT tem que estar em flext-meltano, acabae com essa confusão arrumando isso"
"""

from __future__ import annotations

from pathlib import Path

# Import consolidated components from flext-meltano
from flext_meltano.architecture import FlextSingerArchitectureStandardizer


def main() -> None:
    """Main execution function."""
    flext_root = Path('/home/marlonsc/flext')
    
    if not flext_root.exists():
        raise RuntimeError(f"FLEXT root directory not found: {flext_root}")
    
    standardizer = FlextSingerArchitectureStandardizer(flext_root)
    standardizer.standardize_architecture()


if __name__ == '__main__':
    main()