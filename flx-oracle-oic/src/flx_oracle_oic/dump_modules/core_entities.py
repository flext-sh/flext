"""Core Entity Dump Methods - Main OIC entities (integrations, connections, packages, projects)."""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

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


async def dump_standardized_projects(
    self: Any, dump_path: Path, progress_callback: ProgressCallback | None = None
) -> dict[str, Any]:
    """Dump ALL projects using Oracle OIC v3 API."""
    try:
        from .base import _dump_generic_entity

        return await _dump_generic_entity(
            self,
            "projects",
            "/ic/api/integration/v1/projects",
            dump_path,
            include_artifacts=False,
            progress_callback=progress_callback,
        )
    except Exception as e:
        error_msg = f"CRITICAL ERROR: Failed to dump projects: {e!s}"
        raise RuntimeError(error_msg) from e
