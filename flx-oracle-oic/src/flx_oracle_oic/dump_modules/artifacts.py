"""Artifact Dump Methods - Downloadable artifacts (lookups, libraries, certificates)."""

from pathlib import Path
from typing import Any

# Progress callback type
ProgressCallback = Any


async def dump_standardized_lookups(
    self: Any,
    dump_path: Path,
    *,
    include_artifacts: bool = True,
    progress_callback: ProgressCallback | None = None,
) -> dict[str, Any]:
    """Dump ALL lookups using Oracle OIC v3 API."""
    try:
        from .base import _dump_generic_entity

        return await _dump_generic_entity(
            self,
            "lookups",
            "/ic/api/integration/v1/lookups",
            dump_path,
            include_artifacts=include_artifacts,
            progress_callback=progress_callback,
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
    progress_callback: ProgressCallback | None = None,
) -> dict[str, Any]:
    """Dump ALL libraries using Oracle OIC v3 API."""
    try:
        from .base import _dump_generic_entity

        return await _dump_generic_entity(
            self,
            "libraries",
            "/ic/api/integration/v1/libraries",
            dump_path,
            include_artifacts=include_artifacts,
            progress_callback=progress_callback,
            artifact_extension=".jar",
        )
    except Exception as e:
        error_msg = f"CRITICAL ERROR: Failed to dump libraries: {e!s}"
        raise RuntimeError(error_msg) from e


async def dump_standardized_certificates(
    self: Any, dump_path: Path, progress_callback: ProgressCallback | None = None
) -> dict[str, Any]:
    """Dump ALL certificates using Oracle OIC v3 API."""
    try:
        from .base import _dump_generic_entity

        return await _dump_generic_entity(
            self,
            "certificates",
            "/ic/api/integration/v1/certificates",
            dump_path,
            include_artifacts=False,
            progress_callback=progress_callback,
        )
    except Exception as e:
        error_msg = f"CRITICAL ERROR: Failed to dump certificates: {e!s}"
        raise RuntimeError(error_msg) from e
