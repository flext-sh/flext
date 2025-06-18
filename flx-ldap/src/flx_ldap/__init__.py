"""flx-ldap: Unified CLI for LDAP ETL operations.

This module provides a unified command-line interface for orchestrating
LDAP data extraction (tap-ldap), transformation (dbt-ldap), and loading
(target-ldap) operations. It also integrates with client-a-oud-mig for
migration workflows.

Architecture: Hexagonal Architecture - Orchestrator
Pattern: ETL Pipeline - Orchestration Layer
Dependencies: tap-ldap, target-ldap, dbt-ldap, click
"""

from flx_ldap.orchestrator import LDAPOrchestrator

__version__ = "1.0.0"
__all__ = ["LDAPOrchestrator"]
