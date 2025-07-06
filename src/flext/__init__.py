"""FLEXT - Multi-Project Workspace Coordinator for Enterprise Data Integration.

from flext.__version__ import __version__
Version: 0.6.0
Description: Main FLEXT package for workspace coordination
"""

from flext.__version__ import __version__

__author__ = "FLEXT Team"
__email__ = "team@flext.sh"

# Re-export key components for convenience
from typing import Any


def get_version() -> str:
    """Get FLEXT version."""
    return __version__


def get_workspace_info() -> dict[str, Any]:
    """Get workspace information."""
    return {
        "version": __version__,
        "projects": [
            "flext-core",
            "flext-auth",
            "flext-api",
            "flext-grpc",
            "flext-web",
            "flext-cli",
            "flext-plugin",
            "flext-observability",
            "flext-meltano",
            "flext-ldap",
        ],
        "singer_projects": [
            "flext-tap-ldap",
            "flext-tap-oracle-oic",
            "flext-tap-oracle-wms",
            "flext-target-ldap",
            "flext-target-oracle",
            "flext-dbt-ldap",
        ],
        "enterprise_projects": [
            "algar-oud-mig",
            "gruponos-poc-oic-wms",
            "gruponos-meltano-native",
        ],
    }


__all__ = ["__version__", "get_version", "get_workspace_info"]
