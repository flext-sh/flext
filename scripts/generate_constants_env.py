#!/usr/bin/env python3
"""Generate constants.env file from FlextConstants.

This script ensures that scripts/constants.env stays synchronized with
FlextConstants by auto-generating it from the source of truth.

Usage:
    python scripts/generate_constants_env.py
"""

import sys
from pathlib import Path

# Add flext-core to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "flext-core" / "src"))

from flext_core import FlextConstants


def generate_constants_env() -> str:
    """Generate the contents of constants.env from FlextConstants.

    Returns:
        str: The complete contents of the constants.env file

    """
    # Header
    content = """#!/bin/bash
# FLEXT Constants Environment Variables
# Source this file to get standard FLEXT constants as environment variables
# IMPORTANT: This file is auto-generated from FlextConstants to ensure single source of truth
# Usage: source scripts/constants.env
# To regenerate: python scripts/generate_constants_env.py

"""

    # FLEXT Platform Constants
    content += "# FLEXT Platform Constants (from FlextConstants.Platform)\n"
    content += f"export FLEXT_API_PORT={FlextConstants.Platform.FLEXT_API_PORT}  # FlextConstants.Platform.FLEXT_API_PORT\n"
    content += f"export FLEXT_WEB_PORT={FlextConstants.Platform.DEFAULT_HTTP_PORT}  # FlextConstants.Platform.DEFAULT_HTTP_PORT\n"
    content += f"export FLEXT_DEFAULT_HTTP_PORT={FlextConstants.Platform.DEFAULT_HTTP_PORT}  # FlextConstants.Platform.DEFAULT_HTTP_PORT\n"
    content += f'export FLEXT_DEFAULT_HOST="{FlextConstants.Platform.DEFAULT_HOST}"  # FlextConstants.Platform.DEFAULT_HOST\n'
    content += "\n"

    # Database Constants
    content += "# Database Constants (from FlextConstants.Platform)\n"
    content += f"export FLEXT_REDIS_PORT={FlextConstants.Platform.REDIS_DEFAULT_PORT}  # FlextConstants.Platform.REDIS_DEFAULT_PORT\n"
    content += f"export FLEXT_POSTGRES_PORT={FlextConstants.Platform.POSTGRES_DEFAULT_PORT}  # FlextConstants.Platform.POSTGRES_DEFAULT_PORT\n"
    content += f"export FLEXT_MYSQL_PORT={FlextConstants.Platform.MYSQL_DEFAULT_PORT}  # FlextConstants.Platform.MYSQL_DEFAULT_PORT\n"
    content += f"export FLEXT_MONGODB_PORT={FlextConstants.Platform.MONGODB_DEFAULT_PORT}  # FlextConstants.Platform.MONGODB_DEFAULT_PORT\n"
    content += "\n"

    # LDAP Constants
    content += "# LDAP Constants (from FlextConstants.Platform)\n"
    content += f"export FLEXT_LDAP_PORT={FlextConstants.Platform.LDAP_DEFAULT_PORT}  # FlextConstants.Platform.LDAP_DEFAULT_PORT\n"
    content += f"export FLEXT_LDAPS_PORT={FlextConstants.Platform.LDAPS_DEFAULT_PORT}  # FlextConstants.Platform.LDAPS_DEFAULT_PORT\n"
    content += "export FLEXT_LDAP_TEST_PORT=3390  # Custom test port (no FlextConstants equivalent)\n"
    content += "\n"

    # Network Constants
    content += "# Network Constants (from FlextConstants.Network)\n"
    content += f"export FLEXT_DEFAULT_TIMEOUT={FlextConstants.Network.DEFAULT_TIMEOUT}  # FlextConstants.Network.DEFAULT_TIMEOUT\n"
    content += f"export FLEXT_MIN_PORT={FlextConstants.Network.MIN_PORT}  # FlextConstants.Network.MIN_PORT\n"
    content += f"export FLEXT_MAX_PORT={FlextConstants.Network.MAX_PORT}  # FlextConstants.Network.MAX_PORT\n"
    content += "\n"

    # Monitoring & Observability (custom values)
    content += "# Monitoring & Observability (custom values for monitoring tools)\n"
    content += "export FLEXT_PROMETHEUS_PORT=9090  # Standard Prometheus port\n"
    content += "export FLEXT_GRAFANA_PORT=3000  # Standard Grafana port\n"
    content += "\n"

    # Docker Testing Ports
    content += "# Docker Testing Ports (test-specific configurations)\n"
    content += (
        "export FLEXT_TEST_API_PORT=8081  # Test API port (offset from main API port)\n"
    )
    content += f"export FLEXT_TEST_WEB_PORT={FlextConstants.Platform.DEFAULT_HTTP_PORT}  # FlextConstants.Platform.DEFAULT_HTTP_PORT\n"
    content += "\n"

    # Performance Testing Constants (from FlextConstants.Performance and Logging)
    content += "# Performance Testing Constants (from FlextConstants)\n"
    content += f"export FLEXT_PERFORMANCE_CRITICAL_MS={int(FlextConstants.Performance.CRITICAL_DURATION_MS)}  # FlextConstants.Performance.CRITICAL_DURATION_MS\n"
    content += f"export FLEXT_CRITICAL_USAGE_PERCENT={FlextConstants.Performance.CRITICAL_USAGE_PERCENT}  # FlextConstants.Performance.CRITICAL_USAGE_PERCENT\n"
    content += "export FLEXT_MIN_SUCCESS_RATE=95  # Business requirement - 95% minimum success rate\n"
    content += (
        "export FLEXT_MAX_MEMORY_MB=500  # Test environment limit - 500MB max memory\n"
    )
    content += "\n"

    # URLs for testing scripts
    content += "# URLs for testing scripts (composed from FlextConstants values)\n"
    content += 'export FLEXT_TEST_SERVER_URL="http://${FLEXT_DEFAULT_HOST}:${FLEXT_TEST_API_PORT}"\n'
    content += (
        'export FLEXT_REDIS_ADDRESS="${FLEXT_DEFAULT_HOST}:${FLEXT_REDIS_PORT}"\n'
    )
    content += "\n"

    # Footer
    content += 'echo "FLEXT constants environment variables loaded (synchronized with FlextConstants)"\n'

    return content


def main() -> None:
    """Generate and write the constants.env file."""
    # Generate content
    content = generate_constants_env()

    # Write to file
    constants_env_path = Path(__file__).parent / "constants.env"

    with Path(constants_env_path).open("w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Generated {constants_env_path} from FlextConstants")
    print(f"📝 File contains {len(content.splitlines())} lines")
    print("🔄 Run 'source scripts/constants.env' to load environment variables")


if __name__ == "__main__":
    main()
