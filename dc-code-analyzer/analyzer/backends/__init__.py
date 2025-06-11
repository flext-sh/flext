"""
Analysis backends for the code analyzer.

This module provides a pluggable architecture for different code analysis backends.
Each backend can provide different analysis capabilities.
"""

from __future__ import annotations

from .ast_backend import ASTBackend
from .base import AnalysisBackend, AnalysisResult
from .external_backend import ExternalToolsBackend
from .quality_backend import QualityBackend

# Registry of available backends
AVAILABLE_BACKENDS: dict[str, type[AnalysisBackend]] = {
    "ast": ASTBackend,
    "external": ExternalToolsBackend,
    "quality": QualityBackend,
}

# Default backend configuration
DEFAULT_BACKENDS = ["ast", "external", "quality"]


def get_backend(name: str) -> type[AnalysisBackend]:
    """Get a backend by name."""
    if name not in AVAILABLE_BACKENDS:
        raise ValueError(
            f"Backend '{name}' not found. Available: {list(AVAILABLE_BACKENDS.keys())}",
        )
    return AVAILABLE_BACKENDS[name]


def get_all_backends() -> list[type[AnalysisBackend]]:
    """Get all available backend classes."""
    return list(AVAILABLE_BACKENDS.values())


def get_default_backends() -> list[type[AnalysisBackend]]:
    """Get default backend classes."""
    return [AVAILABLE_BACKENDS[name] for name in DEFAULT_BACKENDS]


__all__ = [
    "AnalysisBackend",
    "AnalysisResult",
    "ASTBackend",
    "ExternalToolsBackend",
    "QualityBackend",
    "get_backend",
    "get_all_backends",
    "get_default_backends",
    "AVAILABLE_BACKENDS",
]
