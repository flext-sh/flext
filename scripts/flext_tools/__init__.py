"""
FLEXT Tools - Biblioteca modular para gerenciamento de dependências

Esta biblioteca separa a complexidade do sync_dependencies.py em módulos
menores, testáveis e reutilizáveis.

Módulos:
- discovery: Descoberta de dependências (imports, configs, etc)
- analysis: Análise de versões e conflitos
- poetry: Operações com Poetry (lock, install, update)
- cache: Sistema de cache para performance
- utils: Utilitários comuns (logging, colors, etc)
"""

__version__ = "0.1.0"

# Exporta módulos principais
from flext_tools.analysis import ConflictAnalyzer, VersionAnalyzer
from flext_tools.cache import CacheManager, cache_result, cached
from flext_tools.discovery import DependencyDiscovery
from flext_tools.poetry import PoetryOperations, PoetryValidator
from flext_tools.safety import BackupManager, RollbackManager, SafetyValidator
from flext_tools.utils import (
    Colors,
    DetailedLogger,
    LogLevel,
    get_logger,
    get_stdlib_modules,
    print_colored,
    should_ignore_path,
)

__all__ = [
    "BackupManager",
    "CacheManager",
    "Colors",
    "ConflictAnalyzer",
    "DependencyDiscovery",
    "DetailedLogger",
    "LogLevel",
    "PoetryOperations",
    "PoetryValidator",
    "RollbackManager",
    "SafetyValidator",
    "VersionAnalyzer",
    "cache_result",
    "cached",
    "get_logger",
    "get_stdlib_modules",
    "print_colored",
    "should_ignore_path",
]
