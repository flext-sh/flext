"""Root-level test package guard for monorepo.

This repository contains many subprojects, each with its own `tests` package.
To avoid ImportPathMismatch across subprojects, we avoid anchoring a global
`tests` package at repository root. When this module is imported inadvertently
by the test runner, we remove the `tests` entry from `sys.modules` so that
each subproject's `tests` package can be imported in isolation.
"""

from __future__ import annotations

try:  # pragma: no cover - defensive
    import sys as _sys

    # Drop the root-level `tests` package from the module cache to prevent
    # cross-package collisions during pytest collection across subprojects.
    if __name__ == "tests":
        _sys.modules.pop("tests", None)
except Exception:
    # Safe fallback: do nothing if sys manipulation is not allowed
    pass
