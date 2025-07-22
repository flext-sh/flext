"""CLI patterns for FLEXT framework.
This module provides base classes and patterns for building
consistent command-line interfaces across FLEXT projects.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from flext.cli_patterns.base_cli import BaseCLI
else:
    try:
        from flext.cli_patterns.base_cli import BaseCLI
    except ImportError:
        # Fallback for missing module
        BaseCLI = None
__all__ = ["BaseCLI"]
