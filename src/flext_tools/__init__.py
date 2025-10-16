"""Compatibility façade bridging historical ``flext_tools`` imports to the new
``flext_quality`` implementation.

All execution logic now lives inside :mod:`flext_quality`.  This module keeps a
thin shim so existing scripts continue to work while teams transition their
imports.  Each symbol exposed here is an alias to the corresponding component
in :mod:`flext_quality.tools`.
"""

from __future__ import annotations

import importlib
import sys

from flext_quality.config import FlextQualityConfig as FlextToolsConfig
from flext_quality.constants import FlextQualityConstants as FlextToolsConstants
from flext_quality.models import FlextQualityModels as FlextToolsModels
from flext_quality.protocols import FlextQualityProtocols as FlextToolsProtocols
from flext_quality.typings import FlextQualityTypes as FlextToolsTypes
from flext_quality.tools import (
    BackupManager,
    Colors,
    ConfigurationManager,
    ConflictAnalyzer,
    DependencyDiscovery,
    FlextPathService,
    FlextQualityArchitectureTools,
    FlextQualityDependencyTools,
    FlextQualityGitTools,
    FlextQualityOperations,
    FlextQualityOptimizerOperations,
    FlextQualityToolsUtilities,
    FlextQualityValidationTools,
    FlextScriptService,
    FlextSecurityService,
    SecretVaultDecryptor,
    MyPyChecker,
    PoetryOperations,
    PoetryValidator,
    ScriptMetadata,
    colorize,
    get_project_root,
    get_stdlib_modules,
    is_stdlib_module,
    normalize_path,
    print_colored,
    should_ignore_path,
)

# Backwards compatible aliases expected by downstream projects
FlextArchitectureTools = FlextQualityArchitectureTools
FlextDependencyTools = FlextQualityDependencyTools
FlextGitTools = FlextQualityGitTools
FlextOptimizerTools = FlextQualityOptimizerOperations
FlextQualityTools = FlextQualityOperations
FlextValidationTools = FlextQualityValidationTools
FlextToolsUtilities = FlextQualityToolsUtilities
FlextScript = FlextScriptService
FlextObservabilityService = FlextSecurityService
PoetryOperations = PoetryOperations
PoetryValidator = PoetryValidator
ScriptMetadata = ScriptMetadata
DependencyDiscovery = DependencyDiscovery
ConflictAnalyzer = ConflictAnalyzer
ConfigurationManager = ConfigurationManager
MyPyChecker = MyPyChecker
BackupManager = BackupManager
SecretVaultDecryptor = SecretVaultDecryptor


def _alias_module(alias: str, target: str, extra_attrs: dict[str, object] | None = None) -> None:
    """Register ``flext_tools.<alias>`` as a view over *target* module."""
    module = importlib.import_module(target)
    if extra_attrs:
        for name, value in extra_attrs.items():
            setattr(module, name, value)
    sys.modules[f"{__name__}.{alias}"] = module


_alias_module("utilities", "flext_quality.tools.utilities")
_alias_module("colors", "flext_quality.tools.utilities")
_alias_module("paths", "flext_quality.tools.paths")
_alias_module("backup", "flext_quality.tools.backup")
_alias_module("config_manager", "flext_quality.tools.config_manager")
_alias_module("conflicts", "flext_quality.tools.conflicts")
_alias_module("discovery_base", "flext_quality.tools.discovery")
_alias_module("mypy_checker", "flext_quality.tools.mypy_checker")
_alias_module("poetry_operations", "flext_quality.tools.poetry")
_alias_module("poetry_validator", "flext_quality.tools.poetry")
_alias_module("script_base", "flext_quality.tools.script_base")
_alias_module("security", "flext_quality.tools.security")
_alias_module("observability", "flext_quality.tools.security")
_alias_module("architecture_tools", "flext_quality.tools.architecture")
_alias_module("dependency_tools", "flext_quality.tools.dependencies")
_alias_module("git_tools", "flext_quality.tools.git")
_alias_module("optimizer_tools", "flext_quality.tools.optimizer_operations")
_alias_module("quality_tools", "flext_quality.tools.quality_operations")
_alias_module("validation_tools", "flext_quality.tools.validation")
_alias_module(
    "constants",
    "flext_quality.constants",
    {"FlextToolsConstants": FlextToolsConstants},
)
_alias_module(
    "models",
    "flext_quality.models",
    {"FlextToolsModels": FlextToolsModels},
)
_alias_module(
    "protocols",
    "flext_quality.protocols",
    {"FlextToolsProtocols": FlextToolsProtocols},
)
_alias_module(
    "typings",
    "flext_quality.typings",
    {"FlextToolsTypes": FlextToolsTypes},
)
_alias_module(
    "config",
    "flext_quality.config",
    {"FlextToolsConfig": FlextToolsConfig},
)

__all__ = [
    "BackupManager",
    "Colors",
    "ConfigurationManager",
    "ConflictAnalyzer",
    "DependencyDiscovery",
    "FlextArchitectureTools",
    "FlextDependencyTools",
    "FlextGitTools",
    "FlextObservabilityService",
    "FlextOptimizerTools",
    "FlextPathService",
    "FlextQualityTools",
    "FlextScript",
    "FlextSecurityService",
    "FlextToolsConfig",
    "FlextToolsConstants",
    "FlextToolsModels",
    "FlextToolsProtocols",
    "FlextToolsTypes",
    "FlextToolsUtilities",
    "FlextValidationTools",
    "MyPyChecker",
    "PoetryOperations",
    "PoetryValidator",
    "SecretVaultDecryptor",
    "ScriptMetadata",
    "colorize",
    "get_project_root",
    "get_stdlib_modules",
    "is_stdlib_module",
    "normalize_path",
    "print_colored",
    "should_ignore_path",
]
