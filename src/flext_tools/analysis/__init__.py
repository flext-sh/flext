"""Módulo de análise de versões e conflitos."""

from flext_tools.analysis.conflicts import ConflictAnalyzer
from flext_tools.analysis.duplicates import CodeDuplicateAnalyzer
from flext_tools.analysis.lock_consistency import LockConsistencyAnalyzer
from flext_tools.analysis.version import (
    VersionAnalyzer,
    analyze_version_conflicts,
    check_version_compatibility,
    normalize_constraint,
    parse_version_spec,
    suggest_version_resolution,
)

__all__: list[str] = [
    "CodeDuplicateAnalyzer",
    "ConflictAnalyzer",
    "LockConsistencyAnalyzer",
    "VersionAnalyzer",
    # Version helper functions
    "analyze_version_conflicts",
    "check_version_compatibility",
    "normalize_constraint",
    "parse_version_spec",
    "suggest_version_resolution",
]
