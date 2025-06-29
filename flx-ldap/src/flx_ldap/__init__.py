"""flx-ldap: Unified CLI for LDAP ETL operations.

This module provides a unified command-line interface for orchestrating
LDAP data extraction (tap-ldap), transformation (dbt-ldap), and loading
(target-ldap) operations. It also integrates with algar-oud-mig for
migration workflows.

Architecture: Hexagonal Architecture - Orchestrator
Pattern: ETL Pipeline - Orchestration Layer
Dependencies: tap-ldap, target-ldap, dbt-ldap, click
"""

from flx_ldap.__version__ import __version__
from flx_ldap.orchestrator import LDAPOrchestrator

__all__ = ["LDAPOrchestrator", "__version__"]
