"""Oracle OIC Dump Modules - Modular Dump Methods
Implements all standardized dump methods with STRICT error propagation.
"""

# Import all dump methods for easy access
from .artifacts import (
    dump_standardized_certificates,
    dump_standardized_libraries,
    dump_standardized_lookups,
)
from .base import _dump_generic_entity
from .core_entities import (
    dump_standardized_connections,
    dump_standardized_integrations,
    dump_standardized_packages,
    dump_standardized_projects,
)
from .runtime import (
    dump_standardized_instances,
    dump_standardized_schedules,
    dump_standardized_tracking,
)
from .system_admin import (
    dump_standardized_adapters,
    dump_standardized_administration,
    dump_standardized_metadata,
    dump_standardized_monitoring,
    dump_standardized_security,
    dump_standardized_system,
)

__all__ = [
    # Base
    "_dump_generic_entity",
    # System & Admin
    "dump_standardized_adapters",
    "dump_standardized_administration",
    "dump_standardized_certificates",
    "dump_standardized_connections",
    # Runtime
    "dump_standardized_instances",
    # Core entities
    "dump_standardized_integrations",
    "dump_standardized_libraries",
    # Artifacts
    "dump_standardized_lookups",
    "dump_standardized_metadata",
    "dump_standardized_monitoring",
    "dump_standardized_packages",
    "dump_standardized_projects",
    "dump_standardized_schedules",
    "dump_standardized_security",
    "dump_standardized_system",
    "dump_standardized_tracking",
]
