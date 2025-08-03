"""FLEXT Tools Security - Enterprise Security Management and Validation.

Provides comprehensive security tooling for the FLEXT ecosystem with enterprise-grade
secret management, vulnerability scanning, security validation, and compliance
checking across all 32 FLEXT projects. This module implements advanced security
patterns for distributed systems with centralized security coordination and
automated security enforcement.

The security system supports both development and production environments,
providing secure secret management, vulnerability detection, compliance validation,
and security policy enforcement. All security operations use FlextResult patterns
and integrate with the broader FLEXT ecosystem for comprehensive security coverage.

Key Components:
    - SecretGenerator: Cryptographically secure secret generation and management
    - SecretVaultDecryptor: Secure secret storage and retrieval with encryption
    - Vulnerability Scanner: Automated security vulnerability detection
    - Compliance Checker: Security policy and compliance validation
    - Access Control: Authentication and authorization pattern enforcement
    - Security Auditing: Comprehensive security audit and reporting

Architecture:
    Implements security patterns with proper abstraction layers and defense-in-depth
    strategies. Supports both local development security and distributed production
    environments with centralized security management and automated enforcement.
    Integrates with external security systems and compliance frameworks.

Example:
    Comprehensive security management for FLEXT ecosystem:

    >>> from flext_tools.security import SecretGenerator, SecretVaultDecryptor
    >>> from pathlib import Path
    >>>
    >>> # Generate secure secrets for ecosystem
    >>> generator = SecretGenerator(
    ...     entropy_bits=256, algorithm="AES-256-GCM", key_rotation=True
    ... )
    >>>
    >>> # Generate application secrets
    >>> api_key_result = generator.generate_api_key(
    ...     service="flext-api", environment="production"
    ... )
    >>> if api_key_result.success:
    ...     api_key = api_key_result.value
    ...     print(f"Generated secure API key: {api_key.key_id}")
    >>>
    >>> # Manage secret vault
    >>> vault = SecretVaultDecryptor(
    ...     vault_path=Path("/secure/secrets"), encryption_key_env="FLEXT_VAULT_KEY"
    ... )
    >>>
    >>> # Retrieve production secrets securely
    >>> db_secret_result = vault.decrypt_secret("database_credentials")
    >>> if db_secret_result.success:
    ...     credentials = db_secret_result.value
    ...     print("Database credentials retrieved securely")

Integration:
    - Built on flext-core patterns with FlextResult error handling
    - Integrates with flext-observability for security monitoring and alerting
    - Coordinates with quality gates for automated security validation
    - Supports integration with external security systems (Vault, LDAP, OAuth)
    - Provides foundation for DevSecOps and security-focused workflows

Quality Standards:
    - Comprehensive error handling with security context preservation
    - Full type annotation coverage for enhanced development experience
    - Extensive security testing and penetration testing validation
    - Cryptographic best practices with industry-standard algorithms
    - Compliance validation and security audit integration

Security Considerations:
    - Zero-trust security model with proper access controls
    - Encryption at rest and in transit for all sensitive data
    - Secure key management with proper rotation and lifecycle
    - Vulnerability scanning and automated security updates
    - Compliance validation with security standards and regulations

Author: FLEXT Development Team
Version: 2.0.0
License: MIT

"""

from flext_tools.security.secret_generator import SecretGenerator
from flext_tools.security.secret_vault import SecretVaultDecryptor

__all__ = ["SecretGenerator", "SecretVaultDecryptor"]
