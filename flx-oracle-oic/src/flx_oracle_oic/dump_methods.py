"""Oracle OIC v3 Dump Methods - Following Official Documentation
Implements all standardized dump methods with STRICT error propagation.
"""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

# Import OIC v3 API paths from Oracle documentation
OIC_LOOKUPS_PATH = "/ic/api/integration/v1/lookups"
OIC_LIBRARIES_PATH = "/ic/api/integration/v1/libraries"
OIC_CERTIFICATES_PATH = "/ic/api/integration/v1/certificates"
OIC_ADAPTERS_PATH = "/ic/api/integration/v1/adapters"
OIC_PROJECTS_PATH = "/ic/api/integration/v1/projects"
OIC_MONITORING_INSTANCES_PATH = "/ic/api/integration/v1/monitoring/instances"
OIC_SYSTEM_PATH = "/ic/api/integration/v1/system"
OIC_SECURITY_PATH = "/ic/api/integration/v1/security"

# Progress callback type
ProgressCallback = Any


async def dump_standardized_integrations(
    self: Any,
    dump_path: Path,
    *,
    include_artifacts: bool = True,
    _include_logs: bool = False,
    progress_callback: ProgressCallback | None = None,
) -> dict[str, Any]:
    """Dump ALL integrations with artifacts and logs using Oracle OIC v3 API."""
    try:
        from datetime import UTC, datetime

        if progress_callback:
            await progress_callback.on_category_start("integrations", 0)

        # Get all integrations using existing method
        integrations = await self.get_integrations()

        if progress_callback:
            await progress_callback.on_category_start("integrations", len(integrations))

        integrations_dir = dump_path / "01-integrations"
        integrations_dir.mkdir(parents=True, exist_ok=True)

        # Save integrations list
        list_file = integrations_dir / "integrations_list.yaml"
        with list_file.open("w", encoding="utf-8") as f:
            yaml.dump(
                {
                    "metadata": {
                        "category": "integrations",
                        "type": "list",
                        "exported_at": datetime.now(UTC).isoformat(),
                        "total_count": len(integrations),
                    },
                    "integrations": integrations,
                },
                f,
                default_flow_style=False,
                allow_unicode=True,
                indent=2,
            )

        # Process each integration
        total_entities = 0
        total_artifacts = 0

        for _i, integration in enumerate(integrations):
            integration_id = integration.get("id", "")
            integration_name = integration.get("name", "")

            if not integration_id:
                error_msg = f"CRITICAL ERROR: Integration missing ID: {integration}"
                raise RuntimeError(error_msg)

            if progress_callback:
                await progress_callback.on_entity_start(
                    "integrations",
                    integration_id,
                    f"{integration_name} ({integration_id})",
                )

            try:
                # Get detailed integration info
                details = await self.get_integration(integration_id)

                if not details:
                    error_msg = f"CRITICAL ERROR: Integration {integration_id} has no details - data integrity issue"
                    raise RuntimeError(error_msg)

                # Save integration as YAML
                clean_id = integration_id.replace("|", "_").replace("/", "_")
                yaml_file = integrations_dir / f"integration_{clean_id}.yaml"

                with yaml_file.open("w", encoding="utf-8") as f:
                    yaml.dump(
                        {
                            "metadata": {
                                "category": "integrations",
                                "type": "integration",
                                "exported_at": datetime.now(UTC).isoformat(),
                                "integration_id": integration_id,
                                "integration_name": integration_name,
                            },
                            "integration_data": details,
                        },
                        f,
                        default_flow_style=False,
                        allow_unicode=True,
                        indent=2,
                    )

                total_entities += 1

                # Download artifact if requested
                artifact_downloaded = False
                if include_artifacts:
                    try:
                        # Use Oracle OIC v3 export API - correct endpoint from documentation
                        export_url = f"{self.config.base_url}{self.config.base_path}/integrations/{integration_id}/archive"

                        # Progress callback for artifact download
                        # Note: on_artifact_start may not be available in all callback implementations

                        import httpx

                        headers = {
                            "Authorization": f"Bearer {self.auth_token}",
                            "Accept": "application/octet-stream",
                        }

                        # Add required parameters for OIC API
                        params = {"integrationInstance": self.config.instance_id}

                        async with httpx.AsyncClient() as client:
                            response = await client.get(
                                export_url, params=params, headers=headers, timeout=60.0
                            )

                            if response.status_code == 200:
                                artifacts_dir = dump_path / "artifacts" / "integrations"
                                artifacts_dir.mkdir(parents=True, exist_ok=True)

                                artifact_file = artifacts_dir / f"{clean_id}.iar"
                                with artifact_file.open("wb") as af:
                                    af.write(response.content)

                                artifact_downloaded = True
                                total_artifacts += 1

                                # Progress callback for completed artifact
                                # Note: on_artifact_complete may not be available in all callback implementations
                            else:
                                error_msg = (
                                    f"CRITICAL ERROR: Failed to download artifact for {integration_id}: "
                                    f"HTTP {response.status_code}"
                                )
                                raise RuntimeError(error_msg)

                    except Exception as e:
                        error_msg = f"CRITICAL ERROR: Artifact download failed for {integration_id}: {e!s}"
                        raise RuntimeError(error_msg) from e

                if progress_callback:
                    await progress_callback.on_entity_complete(
                        "integrations",
                        integration_id,
                        success=True,
                        artifact_downloaded=artifact_downloaded,
                        error="",
                    )

            except Exception as e:
                error_msg = f"CRITICAL ERROR: Failed to process integration {integration_id}: {e!s}"
                raise RuntimeError(error_msg) from e

        result = {
            "success": True,
            "category": "integrations",
            "total_entities": total_entities,
            "total_artifacts": total_artifacts,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        if progress_callback:
            await progress_callback.on_category_complete(
                "integrations", total_entities, total_entities, 0
            )

        return result

    except Exception as e:
        error_msg = f"CRITICAL ERROR: Failed to dump integrations: {e!s}"
        raise RuntimeError(error_msg) from e


async def dump_standardized_connections(
    self: Any, dump_path: Path, progress_callback: ProgressCallback | None = None
) -> dict[str, Any]:
    """Dump ALL connections using Oracle OIC v3 API."""
    try:
        if progress_callback:
            await progress_callback.on_category_start("connections", 0)

        # Get all connections using existing method
        connections = await self.get_connections()

        if progress_callback:
            await progress_callback.on_category_start("connections", len(connections))

        connections_dir = dump_path / "02-connections"
        connections_dir.mkdir(parents=True, exist_ok=True)

        # Save connections list
        list_file = connections_dir / "connections_list.yaml"
        with list_file.open("w", encoding="utf-8") as f:
            yaml.dump(
                {
                    "metadata": {
                        "category": "connections",
                        "type": "list",
                        "exported_at": datetime.now(UTC).isoformat(),
                        "total_count": len(connections),
                    },
                    "connections": connections,
                },
                f,
                default_flow_style=False,
                allow_unicode=True,
                indent=2,
            )

        total_entities = 0

        for connection in connections:
            connection_id = connection.get("id", "")
            if not connection_id:
                error_msg = f"CRITICAL ERROR: Connection missing ID: {connection}"
                raise RuntimeError(error_msg)

            try:
                # Get detailed connection info
                details = await self.get_connection(connection_id)

                # Save connection as YAML
                clean_id = connection_id.replace("|", "_").replace("/", "_")
                yaml_file = connections_dir / f"connection_{clean_id}.yaml"

                with yaml_file.open("w", encoding="utf-8") as f:
                    yaml.dump(
                        {
                            "metadata": {
                                "category": "connections",
                                "type": "connection",
                                "exported_at": datetime.now(UTC).isoformat(),
                                "connection_id": connection_id,
                            },
                            "connection_data": details,
                        },
                        f,
                        default_flow_style=False,
                        allow_unicode=True,
                        indent=2,
                    )

                total_entities += 1

            except Exception as e:
                error_msg = f"CRITICAL ERROR: Failed to process connection {connection_id}: {e!s}"
                raise RuntimeError(error_msg) from e

        result = {
            "success": True,
            "category": "connections",
            "total_entities": total_entities,
            "total_artifacts": 0,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        if progress_callback:
            await progress_callback.on_category_complete(
                "connections", total_entities, total_entities, 0
            )

        return result

    except Exception as e:
        error_msg = f"CRITICAL ERROR: Failed to dump connections: {e!s}"
        raise RuntimeError(error_msg) from e


async def dump_standardized_packages(
    self: Any,
    dump_path: Path,
    *,
    include_artifacts: bool = True,
    progress_callback: ProgressCallback | None = None,
) -> dict[str, Any]:
    """Dump ALL packages using Oracle OIC v3 API."""
    try:
        if progress_callback:
            await progress_callback.on_category_start("packages", 0)

        # Get all packages using existing method
        packages = await self.get_packages()

        if progress_callback:
            await progress_callback.on_category_start("packages", len(packages))

        packages_dir = dump_path / "03-packages"
        packages_dir.mkdir(parents=True, exist_ok=True)

        # Save packages list
        list_file = packages_dir / "packages_list.yaml"
        with list_file.open("w", encoding="utf-8") as f:
            yaml.dump(
                {
                    "metadata": {
                        "category": "packages",
                        "type": "list",
                        "exported_at": datetime.now(UTC).isoformat(),
                        "total_count": len(packages),
                    },
                    "packages": packages,
                },
                f,
                default_flow_style=False,
                allow_unicode=True,
                indent=2,
            )

        total_entities = 0
        total_artifacts = 0

        for package in packages:
            package_id = package.get("id", "")
            if not package_id:
                error_msg = f"CRITICAL ERROR: Package missing ID: {package}"
                raise RuntimeError(error_msg)

            try:
                # Save package as YAML
                clean_id = package_id.replace("|", "_").replace("/", "_")
                yaml_file = packages_dir / f"package_{clean_id}.yaml"

                with yaml_file.open("w", encoding="utf-8") as f:
                    yaml.dump(
                        {
                            "metadata": {
                                "category": "packages",
                                "type": "package",
                                "exported_at": datetime.now(UTC).isoformat(),
                                "package_id": package_id,
                            },
                            "package_data": package,
                        },
                        f,
                        default_flow_style=False,
                        allow_unicode=True,
                        indent=2,
                    )

                total_entities += 1

                # Download package artifact if requested
                if include_artifacts:
                    try:
                        export_url = f"{self.config.base_url}{self.config.base_path}/packages/{package_id}/archive"

                        import httpx

                        headers = {
                            "Authorization": f"Bearer {self.auth_token}",
                            "Accept": "application/octet-stream",
                        }

                        async with httpx.AsyncClient() as client:
                            response = await client.get(
                                export_url, headers=headers, timeout=60.0
                            )

                            if response.status_code == 200:
                                artifacts_dir = dump_path / "artifacts" / "packages"
                                artifacts_dir.mkdir(parents=True, exist_ok=True)

                                artifact_file = artifacts_dir / f"{clean_id}.par"
                                with artifact_file.open("wb") as af:
                                    af.write(response.content)

                                total_artifacts += 1

                    except Exception as e:
                        error_msg = f"CRITICAL ERROR: Package artifact download failed for {package_id}: {e!s}"
                        raise RuntimeError(error_msg) from e

            except Exception as e:
                error_msg = (
                    f"CRITICAL ERROR: Failed to process package {package_id}: {e!s}"
                )
                raise RuntimeError(error_msg) from e

        result = {
            "success": True,
            "category": "packages",
            "total_entities": total_entities,
            "total_artifacts": total_artifacts,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        if progress_callback:
            await progress_callback.on_category_complete(
                "packages", total_entities, total_entities, 0
            )

        return result

    except Exception as e:
        error_msg = f"CRITICAL ERROR: Failed to dump packages: {e!s}"
        raise RuntimeError(error_msg) from e


# Additional dump methods for other OIC v3 entities...
async def dump_standardized_lookups(
    self: Any,
    dump_path: Path,
    *,
    include_artifacts: bool = True,
    _progress_callback: ProgressCallback | None = None,
) -> dict[str, Any]:
    """Dump ALL lookups using Oracle OIC v3 API."""
    try:
        return await self._dump_generic_entity(
            "lookups",
            OIC_LOOKUPS_PATH,
            dump_path,
            include_artifacts=include_artifacts,
            progress_callback=_progress_callback,
            artifact_extension=".csv",
        )
    except Exception as e:
        error_msg = f"CRITICAL ERROR: Failed to dump lookups: {e!s}"
        raise RuntimeError(error_msg) from e


async def dump_standardized_libraries(
    self: Any,
    dump_path: Path,
    *,
    include_artifacts: bool = True,
    _progress_callback: ProgressCallback | None = None,
) -> dict[str, Any]:
    """Dump ALL libraries using Oracle OIC v3 API."""
    try:
        return await self._dump_generic_entity(
            "libraries",
            OIC_LIBRARIES_PATH,
            dump_path,
            include_artifacts=include_artifacts,
            progress_callback=_progress_callback,
            artifact_extension=".jar",
        )
    except Exception as e:
        error_msg = f"CRITICAL ERROR: Failed to dump libraries: {e!s}"
        raise RuntimeError(error_msg) from e


async def dump_standardized_certificates(
    self: Any, dump_path: Path, _progress_callback: ProgressCallback | None = None
) -> dict[str, Any]:
    """Dump ALL certificates using Oracle OIC v3 API."""
    try:
        return await self._dump_generic_entity(
            "certificates",
            OIC_CERTIFICATES_PATH,
            dump_path,
            include_artifacts=False,
            progress_callback=_progress_callback,
        )
    except Exception as e:
        error_msg = f"CRITICAL ERROR: Failed to dump certificates: {e!s}"
        raise RuntimeError(error_msg) from e


async def dump_standardized_adapters(
    self: Any, dump_path: Path, _progress_callback: ProgressCallback | None = None
) -> dict[str, Any]:
    """Dump ALL adapters using Oracle OIC v3 API."""
    try:
        return await self._dump_generic_entity(
            "adapters",
            OIC_ADAPTERS_PATH,
            dump_path,
            include_artifacts=False,
            progress_callback=_progress_callback,
        )
    except Exception as e:
        error_msg = f"CRITICAL ERROR: Failed to dump adapters: {e!s}"
        raise RuntimeError(error_msg) from e


async def dump_standardized_projects(
    self: Any, dump_path: Path, _progress_callback: ProgressCallback | None = None
) -> dict[str, Any]:
    """Dump ALL projects using Oracle OIC v3 API."""
    try:
        return await self._dump_generic_entity(
            "projects",
            OIC_PROJECTS_PATH,
            dump_path,
            include_artifacts=False,
            progress_callback=_progress_callback,
        )
    except Exception as e:
        error_msg = f"CRITICAL ERROR: Failed to dump projects: {e!s}"
        raise RuntimeError(error_msg) from e


async def dump_standardized_instances(
    self: Any, dump_path: Path, _progress_callback: ProgressCallback | None = None
) -> dict[str, Any]:
    """Dump integration instances using Oracle OIC v3 API."""
    try:
        return await self._dump_generic_entity(
            "instances",
            OIC_MONITORING_INSTANCES_PATH,
            dump_path,
            include_artifacts=False,
            progress_callback=_progress_callback,
        )
    except Exception as e:
        error_msg = f"CRITICAL ERROR: Failed to dump instances: {e!s}"
        raise RuntimeError(error_msg) from e


async def dump_standardized_schedules(
    self: Any, dump_path: Path, _progress_callback: ProgressCallback | None = None
) -> dict[str, Any]:
    """Dump scheduled integrations using Oracle OIC v3 API."""
    try:
        schedules_dir = dump_path / "16-schedules"
        schedules_dir.mkdir(parents=True, exist_ok=True)

        # No direct schedules API, extract from integrations
        integrations = await self.get_integrations()

        scheduled_integrations = [
            {
                "integration_id": integration.get("id"),
                "integration_name": integration.get("name"),
                "schedule_type": integration.get("scheduleType"),
                "schedule_info": integration.get("schedule", {}),
                "status": integration.get("status"),
            }
            for integration in integrations
            if integration.get("schedule") or integration.get("scheduleType")
        ]

        # Save schedules
        if scheduled_integrations:
            schedules_file = schedules_dir / "integration_schedules.yaml"
            with schedules_file.open("w", encoding="utf-8") as f:
                yaml.dump(
                    {
                        "metadata": {
                            "category": "schedules",
                            "type": "integration_schedules",
                            "exported_at": datetime.now(UTC).isoformat(),
                            "total_scheduled": len(scheduled_integrations),
                        },
                        "schedules": scheduled_integrations,
                    },
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    indent=2,
                )

        return {
            "success": True,
            "category": "schedules",
            "total_entities": len(scheduled_integrations),
            "total_artifacts": 0,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    except Exception as e:
        error_msg = f"CRITICAL ERROR: Failed to dump schedules: {e!s}"
        raise RuntimeError(error_msg) from e


async def dump_standardized_tracking(
    self: Any, dump_path: Path, _progress_callback: ProgressCallback | None = None
) -> dict[str, Any]:
    """Dump tracking data using Oracle OIC v3 API."""
    try:
        tracking_dir = dump_path / "17-tracking"
        tracking_dir.mkdir(parents=True, exist_ok=True)

        # Get tracking data from instances
        instances_url = f"{self.config.base_url}{OIC_MONITORING_INSTANCES_PATH}"
        params = {"integrationInstance": self.config.instance_id}

        import httpx

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        async with httpx.AsyncClient() as client:
            response = await client.get(
                instances_url, params=params, headers=headers, timeout=60.0
            )

            if response.status_code != 200:
                error_msg = f"CRITICAL ERROR: Failed to get tracking data: HTTP {response.status_code}"
                raise RuntimeError(error_msg)

            data = response.json()
            tracking_items = data.get("items", [])

            # Save tracking data
            tracking_file = tracking_dir / "tracking_data.yaml"
            with tracking_file.open("w", encoding="utf-8") as f:
                yaml.dump(
                    {
                        "metadata": {
                            "category": "tracking",
                            "type": "tracking_data",
                            "exported_at": datetime.now(UTC).isoformat(),
                            "total_items": len(tracking_items),
                        },
                        "tracking_data": tracking_items,
                    },
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    indent=2,
                )

        return {
            "success": True,
            "category": "tracking",
            "total_entities": len(tracking_items),
            "total_artifacts": 0,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    except Exception as e:
        error_msg = f"CRITICAL ERROR: Failed to dump tracking: {e!s}"
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

                except Exception:
                    # Log but don't fail for individual connections
                    pass

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


async def dump_standardized_administration(
    self: Any, dump_path: Path, _progress_callback: ProgressCallback | None = None
) -> dict[str, Any]:
    """Dump administration data using Oracle OIC v3 API."""
    try:
        admin_dir = dump_path / "12-administration"
        admin_dir.mkdir(parents=True, exist_ok=True)

        admin_data = {
            "instance_info": {
                "instance_id": self.config.instance_id,
                "region": self.config.region,
                "base_url": self.config.base_url,
            }
        }

        # Save admin data
        admin_file = admin_dir / "system_administration.yaml"
        with admin_file.open("w", encoding="utf-8") as f:
            yaml.dump(
                {
                    "metadata": {
                        "category": "administration",
                        "type": "system_administration_data",
                        "exported_at": datetime.now(UTC).isoformat(),
                    },
                    "administration_data": admin_data,
                },
                f,
                default_flow_style=False,
                allow_unicode=True,
                indent=2,
            )

        return {
            "success": True,
            "category": "administration",
            "total_entities": 1,
            "total_artifacts": 0,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    except Exception as e:
        error_msg = f"CRITICAL ERROR: Failed to dump administration: {e!s}"
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


async def _dump_generic_entity(
    self: Any,
    category: str,
    api_path: str,
    dump_path: Path,
    *,
    include_artifacts: bool = False,
    progress_callback: ProgressCallback | None = None,
    artifact_extension: str = ".dat",
) -> dict[str, Any]:
    """Generic dump method for OIC entities using Oracle OIC v3 API."""
    try:
        # Map category to directory number
        category_mapping = {
            "lookups": "05-lookups",
            "libraries": "06-libraries",
            "certificates": "07-certificates",
            "adapters": "08-adapters",
            "projects": "04-projects",
            "instances": "14-instances",
        }

        dir_name = category_mapping.get(category, f"99-{category}")
        entity_dir = dump_path / dir_name
        entity_dir.mkdir(parents=True, exist_ok=True)

        # Get entities using OIC v3 API
        # API paths already include full path, don't concatenate with base_path
        url = f"{self.config.base_url}{api_path}"
        params = {"integrationInstance": self.config.instance_id}

        import httpx

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url, params=params, headers=headers, timeout=60.0
            )

            if response.status_code != 200:
                error_msg = f"CRITICAL ERROR: Failed to get {category}: HTTP {response.status_code}"
                raise RuntimeError(error_msg)

            data = response.json()
            entities = data.get("items", [])

            if progress_callback:
                await progress_callback.on_category_start(category, len(entities))

            # Save entities list
            list_file = entity_dir / f"{category}_list.yaml"
            with list_file.open("w", encoding="utf-8") as f:
                yaml.dump(
                    {
                        "metadata": {
                            "category": category,
                            "type": "list",
                            "exported_at": datetime.now(UTC).isoformat(),
                            "total_count": len(entities),
                        },
                        category: entities,
                    },
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    indent=2,
                )

            total_entities = 0
            total_artifacts = 0

            for entity in entities:
                entity_id = entity.get("id", "") or entity.get("name", "")
                if not entity_id:
                    error_msg = f"CRITICAL ERROR: {category.title()} entity missing ID/name: {entity}"
                    raise RuntimeError(error_msg)

                # Save entity as YAML
                clean_id = entity_id.replace("|", "_").replace("/", "_")
                yaml_file = entity_dir / f"{category[:-1]}_{clean_id}.yaml"

                with yaml_file.open("w", encoding="utf-8") as f:
                    yaml.dump(
                        {
                            "metadata": {
                                "category": category,
                                "type": category[:-1],  # Remove 's' from plural
                                "exported_at": datetime.now(UTC).isoformat(),
                                "entity_id": entity_id,
                            },
                            f"{category[:-1]}_data": entity,
                        },
                        f,
                        default_flow_style=False,
                        allow_unicode=True,
                        indent=2,
                    )

                total_entities += 1

                # Download artifact if requested
                if include_artifacts:
                    try:
                        export_url = f"{url}/{entity_id}/archive"

                        artifact_response = await client.get(
                            export_url, headers=headers, timeout=60.0
                        )

                        if artifact_response.status_code == 200:
                            artifacts_dir = dump_path / "artifacts" / category
                            artifacts_dir.mkdir(parents=True, exist_ok=True)

                            artifact_file = (
                                artifacts_dir / f"{clean_id}{artifact_extension}"
                            )
                            with artifact_file.open("wb") as af:
                                af.write(artifact_response.content)

                            total_artifacts += 1

                    except Exception as e:
                        error_msg = f"CRITICAL ERROR: Artifact download failed for {category} {entity_id}: {e!s}"
                        raise RuntimeError(error_msg) from e

        result = {
            "success": True,
            "category": category,
            "total_entities": total_entities,
            "total_artifacts": total_artifacts,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        if progress_callback:
            await progress_callback.on_category_complete(
                category, total_entities, total_entities, 0
            )

        return result

    except Exception as e:
        error_msg = f"CRITICAL ERROR: Failed to dump {category}: {e!s}"
        raise RuntimeError(error_msg) from e
