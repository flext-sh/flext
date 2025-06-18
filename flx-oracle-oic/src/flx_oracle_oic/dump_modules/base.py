"""Base dump functionality - Common utilities and generic dump method."""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

# Progress callback type
ProgressCallback = Any


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
