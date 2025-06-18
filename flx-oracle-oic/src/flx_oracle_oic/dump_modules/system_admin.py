"""System & Administration Dump Methods - System info, monitoring, security, metadata."""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

# Progress callback type
ProgressCallback = Any


async def dump_standardized_adapters(
    self: Any, dump_path: Path, _progress_callback: ProgressCallback | None = None
) -> dict[str, Any]:
    """Dump ALL adapters using Oracle OIC v3 API."""
    try:
        from .base import _dump_generic_entity

        return await _dump_generic_entity(
            self,
            "adapters",
            "/ic/api/integration/v1/adapters",
            dump_path,
            include_artifacts=False,
            progress_callback=_progress_callback,
        )
    except Exception as e:
        error_msg = f"CRITICAL ERROR: Failed to dump adapters: {e!s}"
        raise RuntimeError(error_msg) from e


async def dump_standardized_system(
    self: Any, dump_path: Path, _progress_callback: ProgressCallback | None = None
) -> dict[str, Any]:
    """Dump system information using Oracle OIC v3 API."""
    try:
        system_dir = dump_path / "10-system"
        system_dir.mkdir(parents=True, exist_ok=True)

        system_data = {
            "instance_id": self.config.instance_id,
            "region": self.config.region,
            "base_url": self.config.base_url,
            "api_version": self.config.api_version,
            "exported_at": datetime.now(UTC).isoformat(),
        }

        # Save system info
        system_file = system_dir / "system_info.yaml"
        with system_file.open("w", encoding="utf-8") as f:
            yaml.dump(
                {
                    "metadata": {
                        "category": "system",
                        "type": "system_info",
                        "exported_at": datetime.now(UTC).isoformat(),
                    },
                    "system_data": system_data,
                },
                f,
                default_flow_style=False,
                allow_unicode=True,
                indent=2,
            )

        return {
            "success": True,
            "category": "system",
            "total_entities": 1,
            "total_artifacts": 0,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    except Exception as e:
        error_msg = f"CRITICAL ERROR: Failed to dump system: {e!s}"
        raise RuntimeError(error_msg) from e


async def dump_standardized_monitoring(
    self: Any, dump_path: Path, _progress_callback: ProgressCallback | None = None
) -> dict[str, Any]:
    """Dump monitoring data using Oracle OIC v3 API."""
    try:
        monitoring_dir = dump_path / "09-monitoring"
        monitoring_dir.mkdir(parents=True, exist_ok=True)

        # Get runtime monitoring from integrations
        integrations = await self.get_integrations()
        monitoring_data = {
            "total_integrations": len(integrations),
            "status_summary": {},
            "runtime_health": {},
        }

        for integration in integrations:
            status = integration.get("status", "unknown")
            monitoring_data["status_summary"][status] = (
                monitoring_data["status_summary"].get(status, 0) + 1
            )

            if integration.get("runtimeHealth"):
                monitoring_data["runtime_health"][integration.get("id", "")] = (
                    integration["runtimeHealth"]
                )

        # Save monitoring data
        monitoring_file = monitoring_dir / "runtime_monitoring.yaml"
        with monitoring_file.open("w", encoding="utf-8") as f:
            yaml.dump(
                {
                    "metadata": {
                        "category": "monitoring",
                        "type": "runtime_monitoring",
                        "exported_at": datetime.now(UTC).isoformat(),
                    },
                    "monitoring_data": monitoring_data,
                },
                f,
                default_flow_style=False,
                allow_unicode=True,
                indent=2,
            )

        return {
            "success": True,
            "category": "monitoring",
            "total_entities": 1,
            "total_artifacts": 0,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    except Exception as e:
        error_msg = f"CRITICAL ERROR: Failed to dump monitoring: {e!s}"
        raise RuntimeError(error_msg) from e


async def dump_standardized_security(
    self: Any, dump_path: Path, _progress_callback: ProgressCallback | None = None
) -> dict[str, Any]:
    """Dump security data using Oracle OIC v3 API."""
    try:
        security_dir = dump_path / "11-security"
        security_dir.mkdir(parents=True, exist_ok=True)

        # Get security properties from connections (masked)
        connections = await self.get_connections()
        security_data = []

        for conn in connections:
            conn_id = conn.get("id", "")
            if conn_id:
                try:
                    conn_details = await self.get_connection(conn_id)
                    if conn_details and "connectionProperties" in conn_details:
                        security_props = {
                            "connection_id": conn_id,
                            "connection_name": conn_details.get("name", ""),
                            "adapter_type": conn_details.get("adapterType", ""),
                            "security_properties": [],
                        }

                        for prop in conn_details["connectionProperties"]:
                            prop_name = prop.get("propertyName", "").lower()
                            security_terms = [
                                "password",
                                "secret",
                                "key",
                                "token",
                                "auth",
                                "credential",
                            ]
                            if any(
                                sec_term in prop_name for sec_term in security_terms
                            ):
                                security_props["security_properties"].append(
                                    {
                                        "property_name": prop.get("propertyName", ""),
                                        "property_type": prop.get("propertyType", ""),
                                        "is_sensitive": True,
                                        "value": "***MASKED***",
                                    }
                                )

                        if security_props["security_properties"]:
                            security_data.append(security_props)

                except Exception as e:
                    # Log connection error but continue processing other connections
                    error_info = {
                        "connection_id": conn_id,
                        "error": str(e),
                        "timestamp": datetime.now(UTC).isoformat(),
                    }
                    security_data.append(
                        {
                            "connection_id": conn_id,
                            "error": "Failed to retrieve connection details",
                            "error_details": error_info,
                        }
                    )

        # Save security data
        if security_data:
            security_file = security_dir / "connection_security_data.yaml"
            with security_file.open("w", encoding="utf-8") as f:
                yaml.dump(
                    {
                        "metadata": {
                            "category": "security",
                            "type": "connection_security_properties",
                            "exported_at": datetime.now(UTC).isoformat(),
                            "total_connections_with_security": len(security_data),
                        },
                        "security_data": security_data,
                    },
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    indent=2,
                )

        return {
            "success": True,
            "category": "security",
            "total_entities": len(security_data),
            "total_artifacts": 0,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    except Exception as e:
        error_msg = f"CRITICAL ERROR: Failed to dump security: {e!s}"
        raise RuntimeError(error_msg) from e


async def dump_standardized_REDACTED_LDAP_BIND_PASSWORDistration(
    self: Any, dump_path: Path, _progress_callback: ProgressCallback | None = None
) -> dict[str, Any]:
    """Dump REDACTED_LDAP_BIND_PASSWORDistration data using Oracle OIC v3 API."""
    try:
        REDACTED_LDAP_BIND_PASSWORD_dir = dump_path / "12-REDACTED_LDAP_BIND_PASSWORDistration"
        REDACTED_LDAP_BIND_PASSWORD_dir.mkdir(parents=True, exist_ok=True)

        REDACTED_LDAP_BIND_PASSWORD_data = {
            "instance_info": {
                "instance_id": self.config.instance_id,
                "region": self.config.region,
                "base_url": self.config.base_url,
            }
        }

        # Save REDACTED_LDAP_BIND_PASSWORD data
        REDACTED_LDAP_BIND_PASSWORD_file = REDACTED_LDAP_BIND_PASSWORD_dir / "system_REDACTED_LDAP_BIND_PASSWORDistration.yaml"
        with REDACTED_LDAP_BIND_PASSWORD_file.open("w", encoding="utf-8") as f:
            yaml.dump(
                {
                    "metadata": {
                        "category": "REDACTED_LDAP_BIND_PASSWORDistration",
                        "type": "system_REDACTED_LDAP_BIND_PASSWORDistration_data",
                        "exported_at": datetime.now(UTC).isoformat(),
                    },
                    "REDACTED_LDAP_BIND_PASSWORDistration_data": REDACTED_LDAP_BIND_PASSWORD_data,
                },
                f,
                default_flow_style=False,
                allow_unicode=True,
                indent=2,
            )

        return {
            "success": True,
            "category": "REDACTED_LDAP_BIND_PASSWORDistration",
            "total_entities": 1,
            "total_artifacts": 0,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    except Exception as e:
        error_msg = f"CRITICAL ERROR: Failed to dump REDACTED_LDAP_BIND_PASSWORDistration: {e!s}"
        raise RuntimeError(error_msg) from e


async def dump_standardized_metadata(
    self: Any, dump_path: Path, _progress_callback: ProgressCallback | None = None
) -> dict[str, Any]:
    """Dump metadata using Oracle OIC v3 API."""
    try:
        metadata_dir = dump_path / "13-metadata"
        metadata_dir.mkdir(parents=True, exist_ok=True)

        # Get metadata from integrations
        integrations = await self.get_integrations()
        metadata_analysis = {
            "total_integrations": len(integrations),
            "integration_patterns": {},
            "status_distribution": {},
            "version_distribution": {},
        }

        for integration in integrations:
            # Pattern analysis
            pattern = integration.get("pattern", "unknown")
            current_count = metadata_analysis["integration_patterns"].get(pattern, 0)
            metadata_analysis["integration_patterns"][pattern] = current_count + 1

            # Status analysis
            status = integration.get("status", "unknown")
            current_status_count = metadata_analysis["status_distribution"].get(
                status, 0
            )
            metadata_analysis["status_distribution"][status] = current_status_count + 1

            # Version analysis
            version = integration.get("version", "unknown")
            current_version_count = metadata_analysis["version_distribution"].get(
                version, 0
            )
            metadata_analysis["version_distribution"][version] = (
                current_version_count + 1
            )

        # Save metadata
        metadata_file = metadata_dir / "system_metadata.yaml"
        with metadata_file.open("w", encoding="utf-8") as f:
            yaml.dump(
                {
                    "metadata": {
                        "category": "metadata",
                        "type": "system_metadata_analysis",
                        "exported_at": datetime.now(UTC).isoformat(),
                    },
                    "metadata_analysis": metadata_analysis,
                },
                f,
                default_flow_style=False,
                allow_unicode=True,
                indent=2,
            )

        return {
            "success": True,
            "category": "metadata",
            "total_entities": 1,
            "total_artifacts": 0,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    except Exception as e:
        error_msg = f"CRITICAL ERROR: Failed to dump metadata: {e!s}"
        raise RuntimeError(error_msg) from e
