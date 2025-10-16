#!/usr/bin/env python3
"""Generate FLEXT constants environment file from FlextConstants.

This script extracts relevant constants from FlextConstants and creates
environment variables for shell scripts and CI/CD pipelines.

Usage:
    python scripts/generate_constants_env.py > scripts/constants.env
"""

import sys
from pathlib import Path

# Add flext-core to path for import
flext_core_path = Path(__file__).parent.parent / "flext-core" / "src"
sys.path.insert(0, str(flext_core_path))

try:
    from flext_core.constants import FlextConstants
except ImportError as e:
    print(f"Error importing FlextConstants: {e}", file=sys.stderr)
    print(
        "Make sure flext-core is properly installed or PYTHONPATH is set",
        file=sys.stderr,
    )
    sys.exit(1)


def main() -> None:
    """Generate environment variables from FlextConstants."""
    lines = [
        "#!/bin/bash",
        "# FLEXT Constants Environment Variables",
        "# Source this file to get standard FLEXT constants as environment variables",
        "# IMPORTANT: This file is auto-generated from FlextConstants to ensure single source of truth",
        "# Usage: source scripts/constants.env",
        "# To regenerate: python scripts/generate_constants_env.py",
        "",
        "# FLEXT Platform Constants (from FlextConstants.Platform)",
        f"export FLEXT_API_PORT={FlextConstants.Platform.FLEXT_API_PORT}  # FlextConstants.Platform.FLEXT_API_PORT",
        f'export FLEXT_DEFAULT_HOST="{FlextConstants.Platform.DEFAULT_HOST}"  # FlextConstants.Platform.DEFAULT_HOST',
        f"export FLEXT_DEFAULT_HTTP_PORT={FlextConstants.Platform.DEFAULT_HTTP_PORT}  # FlextConstants.Platform.DEFAULT_HTTP_PORT",
        "",
        "# Network Constants (from FlextConstants.Network)",
        f"export FLEXT_DEFAULT_TIMEOUT={FlextConstants.Network.DEFAULT_TIMEOUT}  # FlextConstants.Network.DEFAULT_TIMEOUT",
        f"export FLEXT_MIN_PORT={FlextConstants.Network.MIN_PORT}  # FlextConstants.Network.MIN_PORT",
        f"export FLEXT_MAX_PORT={FlextConstants.Network.MAX_PORT}  # FlextConstants.Network.MAX_PORT",
        "",
        "# Monitoring & Observability (standard ports)",
        "export FLEXT_PROMETHEUS_PORT=9090  # Standard Prometheus port",
        "export FLEXT_GRAFANA_PORT=3000  # Standard Grafana port",
        "",
        "# Docker Testing Ports (test-specific configurations)",
        "export FLEXT_TEST_API_PORT=8081  # Test API port (offset from main API port)",
        "",
        "# Performance Testing Constants (from FlextConstants)",
        f"export FLEXT_PERFORMANCE_CRITICAL_MS={FlextConstants.Performance.CRITICAL_DURATION_MS}  # FlextConstants.Performance.CRITICAL_DURATION_MS",
        f"export FLEXT_CRITICAL_USAGE_PERCENT={FlextConstants.Performance.CRITICAL_USAGE_PERCENT}  # FlextConstants.Performance.CRITICAL_USAGE_PERCENT",
        "",
        "# Business Requirements",
        "export FLEXT_MIN_SUCCESS_RATE=95  # Business requirement - 95% minimum success rate",
        "export FLEXT_MAX_MEMORY_MB=500  # Test environment limit - 500MB max memory",
        "",
        "# URLs for testing scripts (composed from FlextConstants values)",
        'export FLEXT_TEST_SERVER_URL="http://${FLEXT_DEFAULT_HOST}:${FLEXT_TEST_API_PORT}"',
        "",
        "# Common database ports (industry standards, not from FlextConstants)",
        "export FLEXT_REDIS_PORT=6379  # Standard Redis port",
        "export FLEXT_POSTGRES_PORT=5432  # Standard PostgreSQL port",
        "export FLEXT_MYSQL_PORT=3306  # Standard MySQL port",
        "export FLEXT_MONGODB_PORT=27017  # Standard MongoDB port",
        "",
        "# LDAP ports (industry standards, not from FlextConstants)",
        "export FLEXT_LDAP_PORT=389  # Standard LDAP port",
        "export FLEXT_LDAPS_PORT=636  # Standard LDAPS port",
        "export FLEXT_LDAP_TEST_PORT=3390  # Custom test port",
        "",
        'echo "FLEXT Constants Environment Variables Loaded - Synchronized with FlextConstants"',
    ]

    for line in lines:
        print(line)


if __name__ == "__main__":
    main()
