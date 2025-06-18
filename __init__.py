"""
OUD Migration Module - Simplified flat structure
Essential migration functionality without over-engineering
"""

# Core components
from .async_ldap import AsyncLDAPPool
from .base import BaseConnectionManager, BaseProcessor

# Configuration
from .config import ModernHydraConfig
from .exceptions import ConnectionError, LdifError, MigrationError, SchemaError

# LDAP operations
from .ldap_operations import LDAPConnection

# Processing components
from .ldif import StandardLdifProcessor

# Safety and utilities
from .safety import (
    SafeLdifProcessor,
    TransactionContext,
    atomic_ldif_write,
    get_transaction_manager,
)
from .schema import StandardSchemaService

# Backward compatibility aliases
RealLDAPConnection = LDAPConnection
UnifiedLdapManager = LDAPConnection
UnifiedLdifProcessor = StandardLdifProcessor
UnifiedConfig = ModernHydraConfig

__all__ = [
    "AsyncLDAPPool",
    # Core
    "BaseConnectionManager",
    "BaseProcessor",
    "ConnectionError",
    # LDAP
    "LDAPConnection",
    "LdifError",
    "MigrationError",
    # Config
    "ModernHydraConfig",
    # Backward compatibility
    "RealLDAPConnection",
    # Safety
    "SafeLdifProcessor",
    "SchemaError",
    # Processing
    "StandardLdifProcessor",
    "StandardSchemaService",
    "TransactionContext",
    "UnifiedConfig",
    "UnifiedLdapManager",
    "UnifiedLdifProcessor",
    "atomic_ldif_write",
    "get_transaction_manager",
]
