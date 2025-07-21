"""Módulo de análise de versões e conflitos."""

from flext_tools.analysis.conflicts import ConflictAnalyzer
from flext_tools.analysis.duplicates import CodeDuplicateAnalyzer
from flext_tools.analysis.lock_consistency import LockConsistencyAnalyzer
from flext_tools.analysis.version import VersionAnalyzer

__all__ = [
    "CodeDuplicateAnalyzer",
    "ConflictAnalyzer",
    "LockConsistencyAnalyzer",
    "VersionAnalyzer",
]
