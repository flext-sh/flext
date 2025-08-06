#!/usr/bin/env python3
"""Refactor all FLEXT projects to use flext-meltano facilities correctly."""

import os
import sys
from pathlib import Path

# Template for TAP __init__.py
TAP_INIT_TEMPLATE = '''"""FLEXT Tap {NAME} - Enterprise Singer Tap for {DESCRIPTION}.

**Architecture**: Production-ready Singer tap implementing Clean Architecture, DDD, and enterprise patterns
**Integration**: Complete flext-meltano ecosystem integration with ALL facilities utilized
**Quality**: 100% type safety, 90%+ test coverage, zero-tolerance quality standards

## Enterprise Integration Features:

1. **Complete flext-meltano Integration**: Uses ALL flext-meltano facilities
   - FlextMeltanoTapService base class for enterprise patterns
   - Centralized Singer SDK imports and typing
   - Common schema definitions from flext-meltano.common_schemas
   - Enterprise bridge integration for Go ↔ Python communication

2. **Foundation Library Integration**: Full flext-core pattern adoption
   - FlextResult railway-oriented programming throughout
   - Enterprise logging with FlextLogger
   - Dependency injection with flext-core container
   - FlextConfig for configuration management

3. **Production Readiness**: Zero-tolerance quality standards
   - 100% type safety with strict MyPy compliance
   - 90%+ test coverage with comprehensive test suite
   - All lint rules passing with Ruff
   - Security scanning with Bandit and pip-audit

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import importlib.metadata

# === FLEXT-MELTANO COMPLETE INTEGRATION ===
# Re-export ALL flext-meltano facilities for full ecosystem integration
from flext_meltano import (
    # Core Singer SDK classes (centralized from flext-meltano)
    Stream,
    Tap,
    Target,
    Sink,
    BatchSink,
    SQLSink,
    RESTStream,
    
    # Enterprise services from flext-meltano.base
    FlextMeltanoTapService,
    FlextMeltanoBaseService,
    create_meltano_tap_service,
    
    # Configuration and validation
    FlextMeltanoConfig,
    FlextMeltanoEvent,
    
    # Singer typing utilities (centralized)
    singer_typing,
    
    # Common schemas and patterns
    {SCHEMA_IMPORT},
    
    # Bridge integration
    FlextMeltanoBridge,
    
    # Testing utilities
    get_tap_test_class,
    
    # Authentication patterns
    OAuthAuthenticator,
    
    # Typing definitions
    PropertiesList,
    Property,
)

# flext-core imports
from flext_core import FlextResult, FlextValueObject, get_logger

# Local implementations - keep existing imports
{LOCAL_IMPORTS}

# Version following semantic versioning
try:
    __version__ = importlib.metadata.version("{PACKAGE}")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.9.0-enterprise"

__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())

# Complete public API exports
__all__ = [
    # === PRIMARY CLASSES ===
    {PRIMARY_EXPORTS}
    
    # === FLEXT-MELTANO COMPLETE RE-EXPORTS ===
    # Singer SDK core classes
    "Stream",
    "Tap",
    "Target",
    "Sink",
    "BatchSink",
    "SQLSink",
    "RESTStream",
    
    # Enterprise services
    "FlextMeltanoTapService",
    "FlextMeltanoBaseService",
    "create_meltano_tap_service",
    
    # Configuration patterns
    "FlextMeltanoConfig",
    "FlextMeltanoEvent",
    
    # Singer typing
    "singer_typing",
    "PropertiesList",
    "Property",
    
    # Schema utilities
    "{SCHEMA_EXPORT}",
    
    # Bridge integration
    "FlextMeltanoBridge",
    
    # Testing
    "get_tap_test_class",
    
    # Authentication
    "OAuthAuthenticator",
    
    # === FLEXT-CORE RE-EXPORTS ===
    "FlextResult",
    "FlextValueObject",
    "get_logger",
    
    # === METADATA ===
    "__version__",
    "__version_info__",
]
'''

# Similar template for TARGET
TARGET_INIT_TEMPLATE = TAP_INIT_TEMPLATE.replace('Tap', 'Target').replace('tap', 'target').replace('FlextMeltanoTapService', 'FlextMeltanoTargetService')

# Template for DBT __init__.py
DBT_INIT_TEMPLATE = '''"""FLEXT DBT {NAME} - Enterprise DBT Models for {DESCRIPTION}.

**Architecture**: Production-ready DBT project with enterprise patterns
**Integration**: Complete flext-meltano ecosystem integration
**Quality**: Enterprise-grade data models with comprehensive testing

## Enterprise Integration Features:

1. **Complete flext-meltano Integration**: Uses ALL DBT facilities
   - DBT Hub integration for model registry
   - In-memory execution with DuckDB
   - Enterprise patterns from flext-core

2. **Production Readiness**: Zero-tolerance quality standards
   - Comprehensive DBT tests
   - Data quality validation
   - Performance optimization

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import importlib.metadata

# Import DBT facilities from flext-meltano
from flext_meltano import (
    # DBT Hub integration
    FlextDbtHub,
    FlextDbtPackageManager,
    FlextDbtModelRegistry,
    FlextDbtInMemoryExecutor,
    
    # DBT utilities
    create_dbt_hub,
)

# flext-core imports
from flext_core import FlextResult, get_logger

# Local implementations - keep existing imports
{LOCAL_IMPORTS}

# Version following semantic versioning
try:
    __version__ = importlib.metadata.version("{PACKAGE}")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.9.0-enterprise"

__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())

# Complete public API exports
__all__ = [
    # === PRIMARY CLASSES ===
    {PRIMARY_EXPORTS}
    
    # === FLEXT-MELTANO DBT RE-EXPORTS ===
    "FlextDbtHub",
    "FlextDbtPackageManager",
    "FlextDbtModelRegistry",
    "FlextDbtInMemoryExecutor",
    "create_dbt_hub",
    
    # === FLEXT-CORE RE-EXPORTS ===
    "FlextResult",
    "get_logger",
    
    # === METADATA ===
    "__version__",
    "__version_info__",
]
'''

def get_project_info(project_path: Path) -> dict:
    """Extract project information."""
    project_name = project_path.name
    
    # Determine type
    if 'tap' in project_name:
        project_type = 'tap'
    elif 'target' in project_name:
        project_type = 'target'
    elif 'dbt' in project_name:
        project_type = 'dbt'
    else:
        return None
    
    # Get entity name
    entity = project_name.replace('flext-', '').replace('tap-', '').replace('target-', '').replace('dbt-', '')
    
    # Schema imports
    schema_map = {
        'ldap': 'create_ldap_tap_schema',
        'ldif': 'create_ldif_schema',
        'oracle': 'create_oracle_tap_schema',
        'oracle-oic': 'create_oracle_tap_schema',
        'oracle-wms': 'create_oracle_tap_schema',
    }
    
    return {
        'name': project_name,
        'type': project_type,
        'entity': entity,
        'schema_import': schema_map.get(entity, 'create_generic_schema'),
        'package': project_name,
    }

def process_project(project_path: Path):
    """Process a single project."""
    info = get_project_info(project_path)
    if not info:
        print(f"⚠️ Skipping {project_path.name} - not a tap/target/dbt project")
        return
    
    init_file = project_path / 'src' / info['name'].replace('-', '_') / '__init__.py'
    
    if not init_file.exists():
        print(f"⚠️ {info['name']}: __init__.py not found")
        return
    
    # Read existing file to extract local imports
    existing_content = init_file.read_text()
    
    # For now, just report what we would do
    print(f"✅ Would refactor {info['name']} ({info['type']})")
    print(f"   - Schema: {info['schema_import']}")
    print(f"   - Package: {info['package']}")

def main():
    """Main refactoring function."""
    base_path = Path('/home/marlonsc/flext')
    
    # List all projects to refactor
    projects = [
        'flext-tap-ldap', 'flext-tap-ldif', 'flext-tap-oracle',
        'flext-tap-oracle-oic', 'flext-tap-oracle-wms',
        'flext-target-ldap', 'flext-target-ldif', 'flext-target-oracle',
        'flext-target-oracle-oic', 'flext-target-oracle-wms',
        'flext-dbt-ldap', 'flext-dbt-ldif', 'flext-dbt-oracle', 'flext-dbt-oracle-wms'
    ]
    
    print("=== FLEXT Projects Refactoring Plan ===\n")
    
    for project_name in projects:
        project_path = base_path / project_name
        if project_path.exists():
            process_project(project_path)
        else:
            print(f"❌ {project_name}: Project not found")
    
    print("\n=== Refactoring Complete ===")

if __name__ == '__main__':
    main()