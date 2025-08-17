#!/usr/bin/env python3
"""Singer Architecture Standardizer - consolidated in flext-meltano.

This module is now a compatibility layer that imports from flext-meltano.
All new development should use flext_meltano.architecture directly.

Implements the architectural directive:
"Singer, Meltano e DBT tem que estar em flext-meltano, "
"acabae com essa confusão arrumando isso"
"""

from __future__ import annotations

from importlib import import_module
from pathlib import Path

# We'll import the heavy `flext_meltano.architecture` module at runtime inside main()
ARCHITECTURE_MODULE_AVAILABLE = False


def main() -> None:
    """Main execution function.

    Import the required flext_meltano.architecture at runtime so importing this
    shim doesn't fail in environments where the package is not installed.
    """
    # Use the current working directory as the flext root when run inside repo
    flext_root = Path.cwd()

    if not flext_root.exists():
        msg = f"FLEXT root directory not found: {flext_root}"
        raise RuntimeError(msg)

    # Import flext_meltano.architecture dynamically to avoid import-time errors
    try:
        mod = import_module("flext_meltano.architecture")
        standardizer_cls = mod.FlextSingerArchitectureStandardizer
    except Exception as exc:  # pragma: no cover - environment dependent
        msg_ = (
            "Missing dependency: flext_meltano.architecture. "
            "Install the package or run from the monorepo workspace."
        )
        raise RuntimeError(msg_) from exc

    standardizer = standardizer_cls(flext_root)
    standardizer.standardize_architecture()


if __name__ == "__main__":
    main()
